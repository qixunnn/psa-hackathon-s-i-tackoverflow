import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv


BACKEND_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Settings:
    supabase_url: str
    supabase_service_role_key: str


@lru_cache
def get_settings() -> Settings:
    load_dotenv(BACKEND_ROOT / ".env")

    supabase_url = os.getenv("SUPABASE_URL")
    service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    missing = [
        name
        for name, value in (
            ("SUPABASE_URL", supabase_url),
            ("SUPABASE_SERVICE_ROLE_KEY", service_role_key),
        )
        if not value
    ]
    if missing:
        raise RuntimeError(
            f"Missing required environment variables: {', '.join(missing)}"
        )

    assert supabase_url is not None
    assert service_role_key is not None
    return Settings(
        supabase_url=supabase_url,
        supabase_service_role_key=service_role_key,
    )
