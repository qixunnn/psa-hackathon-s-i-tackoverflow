"""Deterministic chokepoint taxonomy shared by extraction and risk agents."""

import json
from pathlib import Path


DATA_DIRECTORY = Path(__file__).resolve().parent / "data"
TAXONOMY_PATH = DATA_DIRECTORY / "chokepoint_taxonomy.json"
ROUTE_GRAPH_PATH = DATA_DIRECTORY / "route_graph.json"


class UnknownChokepointError(ValueError):
    """Raised when a purported chokepoint is neither known nor an excluded region."""


def _key(value: str) -> str:
    return " ".join(value.split()).casefold()


with TAXONOMY_PATH.open(encoding="utf-8") as taxonomy_file:
    _TAXONOMY = json.load(taxonomy_file)

_CANONICAL_BY_KEY = {
    _key(candidate): canonical
    for canonical, aliases in _TAXONOMY["chokepoints"].items()
    for candidate in [canonical, *aliases]
}
_REGION_KEYS = {_key(name) for name in _TAXONOMY["non_chokepoint_regions"]}

with ROUTE_GRAPH_PATH.open(encoding="utf-8") as route_graph_file:
    _ROUTE_GRAPH_CHOKEPOINTS = {
        chokepoint
        for route in json.load(route_graph_file)
        for chokepoint in route["chokepoints"]
    }

_MISSING_GRAPH_CHOKEPOINTS = _ROUTE_GRAPH_CHOKEPOINTS - set(_TAXONOMY["chokepoints"])
if _MISSING_GRAPH_CHOKEPOINTS:
    missing = ", ".join(sorted(_MISSING_GRAPH_CHOKEPOINTS))
    raise RuntimeError(f"Chokepoint taxonomy is missing route-graph identifiers: {missing}")


def known_chokepoints() -> frozenset[str]:
    return frozenset(_TAXONOMY["chokepoints"])


def normalize_chokepoints(values: list[str]) -> list[str]:
    """Canonicalize known names, omit known regions, and reject unknown values."""
    normalized = []
    for value in values:
        lookup_key = _key(value)
        if lookup_key in _REGION_KEYS:
            continue
        canonical = _CANONICAL_BY_KEY.get(lookup_key)
        if canonical is None:
            raise UnknownChokepointError(f"Unrecognized chokepoint: {value}")
        if canonical not in normalized:
            normalized.append(canonical)
    return normalized
