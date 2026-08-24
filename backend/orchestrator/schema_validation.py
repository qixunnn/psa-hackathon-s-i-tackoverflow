"""JSON Schema validation for PSA Sentinel entity payloads."""

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft7Validator, FormatChecker, RefResolver


SCHEMAS_DIR = Path(__file__).resolve().parents[2] / "schemas"


class ValidationError(ValueError):
    """Raised when an entity payload violates its JSON Schema contract."""


def validate(entity_name: str, payload: dict) -> None:
    """Validate a payload against the named entity schema."""
    schema_filename = entity_name if entity_name.endswith(".schema.json") else f"{entity_name}.schema.json"
    schema_path = SCHEMAS_DIR / schema_filename

    if not schema_path.is_file():
        raise ValidationError(f"Schema not found for entity '{entity_name}': {schema_path}")

    with schema_path.open(encoding="utf-8") as schema_file:
        schema = json.load(schema_file)

    schema_store = {}
    for referenced_schema_path in SCHEMAS_DIR.glob("*.schema.json"):
        with referenced_schema_path.open(encoding="utf-8") as referenced_schema_file:
            referenced_schema = json.load(referenced_schema_file)
        schema_store[referenced_schema_path.name] = referenced_schema

    resolver = RefResolver.from_schema(schema, store=schema_store)
    validator = Draft7Validator(schema, resolver=resolver, format_checker=FormatChecker())
    try:
        validator.validate(payload)
    except Exception as error:
        if error.__class__.__module__.startswith("jsonschema"):
            message = getattr(error, "message", str(error))
            raise ValidationError(f"Invalid {entity_name} payload: {message}") from error
        raise
