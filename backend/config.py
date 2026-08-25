"""Central runtime configuration for backend integrations."""

from dataclasses import dataclass
import os
from pathlib import Path

from google import genai


DEFAULT_GEMINI_MODEL = "gemini-2.5-flash"
ENV_PATH = Path(__file__).resolve().parent / ".env"


def _load_env_file(path: Path = ENV_PATH) -> None:
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            os.environ.setdefault(key, value)


class ConfigurationError(RuntimeError):
    """Raised when required runtime configuration is unavailable."""


@dataclass(frozen=True)
class GeminiSettings:
    api_key: str
    model: str = DEFAULT_GEMINI_MODEL

    @classmethod
    def from_env(cls) -> "GeminiSettings":
        _load_env_file()
        api_key = os.getenv("GEMINI_API_KEY", "").strip()
        if not api_key:
            raise ConfigurationError("GEMINI_API_KEY is required for Gemini agents")
        model = os.getenv("GEMINI_MODEL", DEFAULT_GEMINI_MODEL).strip()
        if not model:
            raise ConfigurationError("GEMINI_MODEL must not be empty")
        if "flash" not in model.lower():
            raise ConfigurationError("Gemini agents require a Gemini Flash model")
        return cls(api_key=api_key, model=model)


def create_gemini_client(settings: GeminiSettings):
    """Create the shared Gemini client used by semantic pipeline agents."""
    return genai.Client(api_key=settings.api_key)
