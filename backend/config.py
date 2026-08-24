"""Central runtime configuration for backend integrations."""

from dataclasses import dataclass
import os

from google import genai


DEFAULT_GEMINI_MODEL = "gemini-2.5-flash"


class ConfigurationError(RuntimeError):
    """Raised when required runtime configuration is unavailable."""


@dataclass(frozen=True)
class GeminiSettings:
    api_key: str
    model: str = DEFAULT_GEMINI_MODEL

    @classmethod
    def from_env(cls) -> "GeminiSettings":
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
