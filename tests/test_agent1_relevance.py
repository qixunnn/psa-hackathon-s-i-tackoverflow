import json
from types import SimpleNamespace

import pytest

from backend.agents import agent1_relevance
from backend.config import GeminiSettings
from backend.orchestrator.schema_validation import ValidationError


SETTINGS = GeminiSettings(api_key="test-key", model="gemini-2.5-flash")
ARTICLE_TEXT = (
    "A carrier temporarily suspended vessel transit through the Strait of Hormuz "
    "after regional authorities issued a maritime security warning."
)


def valid_gemini_payload(*, relevant=True):
    return {
        "relevant": relevant,
        "confidence": 0.91,
        "relevance_rationale": (
            "The disruption affects a chokepoint used by PSA-bound shipping."
            if relevant
            else "The event has no maritime transport or PSA-bound shipping impact."
        ),
        "summary": "A carrier suspended transit through the Strait of Hormuz.",
        "entities": {
            "location": "Strait of Hormuz",
            "event_type": "maritime security disruption",
            "date": "2026-08-25",
            "actors": ["Carrier", "Regional authorities"],
            "chokepoints_mentioned": ["Strait of Hormuz"] if relevant else [],
        },
        "evidence": ["temporarily suspended vessel transit through the Strait of Hormuz"],
    }


class FakeModels:
    def __init__(self, payload=None, text=None, error=None):
        self.payload = payload
        self.text = text
        self.error = error
        self.calls = []

    def generate_content(self, **kwargs):
        self.calls.append(kwargs)
        if self.error:
            raise self.error
        response_text = self.text if self.text is not None else json.dumps(self.payload)
        return SimpleNamespace(text=response_text)


def fake_client(payload=None, text=None, error=None):
    models = FakeModels(payload=payload, text=text, error=error)
    return SimpleNamespace(models=models), models


def state(**overrides):
    return {
        "run_id": "run-1",
        "source_url": "https://example.com/article",
        **overrides,
    }


def test_successful_mocked_url_fetch_and_extraction():
    client, models = fake_client(valid_gemini_payload())
    fetched = []
    extracted = []

    def fetcher(url):
        fetched.append(url)
        return "<html>downloaded</html>"

    def extractor(downloaded, **options):
        extracted.append((downloaded, options))
        return ARTICLE_TEXT

    event = agent1_relevance.run(
        state(), fetcher=fetcher, extractor=extractor, client=client, settings=SETTINGS
    )

    assert event["relevant"] is True
    assert event["run_id"] == "run-1"
    assert fetched == ["https://example.com/article"]
    assert extracted[0][0] == "<html>downloaded</html>"
    assert models.calls[0]["model"] == "gemini-2.5-flash"
    assert ARTICLE_TEXT in models.calls[0]["contents"]
    assert models.calls[0]["config"]["response_mime_type"] == "application/json"


def test_manual_article_text_bypasses_trafilatura():
    client, _ = fake_client(valid_gemini_payload())

    def unexpected_fetch(_url):
        raise AssertionError("trafilatura fetch must not run for manual text")

    event = agent1_relevance.run(
        state(article_text=ARTICLE_TEXT),
        fetcher=unexpected_fetch,
        client=client,
        settings=SETTINGS,
    )

    assert event["summary"] == "A carrier suspended transit through the Strait of Hormuz."


def test_scraping_failure_is_explicit():
    client, _ = fake_client(valid_gemini_payload())
    with pytest.raises(agent1_relevance.ArticleExtractionError):
        agent1_relevance.run(
            state(), fetcher=lambda _url: None, client=client, settings=SETTINGS
        )


def test_relevant_valid_gemini_response_returns_valid_event():
    client, _ = fake_client(valid_gemini_payload(relevant=True))
    event = agent1_relevance.run(
        state(article_text=ARTICLE_TEXT), client=client, settings=SETTINGS
    )
    assert event["relevant"] is True
    assert event["evidence"]
    assert event["source_url"] == "https://example.com/article"


def test_irrelevant_valid_gemini_response_is_not_an_error():
    payload = valid_gemini_payload(relevant=False)
    payload["entities"]["chokepoints_mentioned"] = []
    client, _ = fake_client(payload)
    event = agent1_relevance.run(
        state(article_text=ARTICLE_TEXT), client=client, settings=SETTINGS
    )
    assert event["relevant"] is False


def test_malformed_gemini_json_raises_explicit_error():
    client, _ = fake_client(text="{not valid json")
    with pytest.raises(agent1_relevance.GeminiResponseError):
        agent1_relevance.run(
            state(article_text=ARTICLE_TEXT), client=client, settings=SETTINGS
        )


def test_missing_required_gemini_field_is_rejected():
    payload = valid_gemini_payload()
    payload.pop("relevance_rationale")
    client, _ = fake_client(payload)
    with pytest.raises(ValidationError):
        agent1_relevance.run(
            state(article_text=ARTICLE_TEXT), client=client, settings=SETTINGS
        )


def test_schema_invalid_gemini_output_is_rejected():
    payload = valid_gemini_payload()
    payload["confidence"] = 1.5
    client, _ = fake_client(payload)
    with pytest.raises(ValidationError):
        agent1_relevance.run(
            state(article_text=ARTICLE_TEXT), client=client, settings=SETTINGS
        )


def test_invalid_evidence_is_rejected():
    payload = valid_gemini_payload()
    payload["evidence"] = "not-an-array"
    client, _ = fake_client(payload)
    with pytest.raises(ValidationError):
        agent1_relevance.run(
            state(article_text=ARTICLE_TEXT), client=client, settings=SETTINGS
        )


def test_gemini_api_error_is_explicit_and_wrapped():
    client, _ = fake_client(error=RuntimeError("service unavailable"))
    with pytest.raises(agent1_relevance.Agent1Error, match="Gemini request failed"):
        agent1_relevance.run(
            state(article_text=ARTICLE_TEXT), client=client, settings=SETTINGS
        )
