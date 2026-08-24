"""Agent 1: fetch an article and extract a validated relevance Event."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from google import genai
import trafilatura

from backend.config import ConfigurationError, GeminiSettings
from backend.orchestrator.schema_validation import validate
from backend.prompts.agent1 import SYSTEM_INSTRUCTION, build_prompt


EVENT_SCHEMA_PATH = Path(__file__).resolve().parents[2] / "schemas" / "event.schema.json"


class Agent1Error(RuntimeError):
    """Raised when Agent 1 cannot produce a trustworthy Event."""


class ArticleExtractionError(Agent1Error):
    """Raised when URL content cannot be fetched or extracted."""


class GeminiResponseError(Agent1Error):
    """Raised when Gemini does not return parseable structured JSON."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _gemini_response_schema() -> dict[str, Any]:
    """Derive Gemini's output shape from the authoritative Event schema."""
    with EVENT_SCHEMA_PATH.open(encoding="utf-8") as schema_file:
        event_schema = json.load(schema_file)
    generated_fields = {
        "relevant",
        "confidence",
        "relevance_rationale",
        "summary",
        "entities",
        "evidence",
    }
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            name: definition
            for name, definition in event_schema["properties"].items()
            if name in generated_fields
        },
        "required": [name for name in event_schema["required"] if name in generated_fields],
    }


def _fetch_article_text(
    source_url: str,
    fetcher: Callable[[str], Any],
    extractor: Callable[..., str | None],
) -> str:
    try:
        downloaded = fetcher(source_url)
        if not downloaded:
            raise ArticleExtractionError("Article fetch returned no content")
        extracted = extractor(downloaded, include_comments=False, include_tables=False)
    except ArticleExtractionError:
        raise
    except Exception as error:
        raise ArticleExtractionError(f"Article fetch/extraction failed: {error}") from error
    if not extracted or not extracted.strip():
        raise ArticleExtractionError("Article extraction returned no readable text")
    return extracted.strip()


def _create_client(settings: GeminiSettings):
    return genai.Client(api_key=settings.api_key)


def run(
    state: dict,
    *,
    fetcher: Callable[[str], Any] = trafilatura.fetch_url,
    extractor: Callable[..., str | None] = trafilatura.extract,
    client=None,
    settings: GeminiSettings | None = None,
) -> dict:
    """Return the validated Event for a URL or manually supplied article text."""
    source_url = state["source_url"]
    manual_text = state.get("article_text")
    article_text = manual_text.strip() if isinstance(manual_text, str) else ""
    if not article_text:
        article_text = _fetch_article_text(source_url, fetcher, extractor)

    try:
        resolved_settings = settings or GeminiSettings.from_env()
        gemini_client = client or _create_client(resolved_settings)
        response = gemini_client.models.generate_content(
            model=resolved_settings.model,
            contents=build_prompt(source_url, article_text),
            config={
                "system_instruction": SYSTEM_INSTRUCTION,
                "response_mime_type": "application/json",
                "response_json_schema": _gemini_response_schema(),
                "temperature": 0.1,
            },
        )
    except ConfigurationError as error:
        raise Agent1Error(str(error)) from error
    except Exception as error:
        raise Agent1Error(f"Gemini request failed: {error}") from error

    try:
        generated = json.loads(response.text)
    except (TypeError, json.JSONDecodeError) as error:
        raise GeminiResponseError("Gemini returned malformed JSON") from error
    if not isinstance(generated, dict):
        raise GeminiResponseError("Gemini response must be a JSON object")

    event = {
        **generated,
        "run_id": state["run_id"],
        "source_url": source_url,
        "extracted_at": _now(),
    }
    validate("event", event)
    return event
