"""Canned relevance and extraction agent."""

import time


def run(state: dict) -> dict:
    time.sleep(1)
    source_url = state["source_url"]
    if "irrelevant" in source_url:
        return {
            "run_id": state["run_id"],
            "relevant": False,
            "confidence": 0.98,
            "summary": "Article concerns a domestic labor dispute, no shipping impact",
            "entities": {
                "location": "Domestic labor market",
                "event_type": "labor dispute",
                "date": "2026-08-25",
                "actors": ["Domestic workers"],
                "chokepoints_mentioned": [],
            },
            "source_url": source_url,
            "extracted_at": "2026-08-25T00:00:00Z",
        }

    return {
        "run_id": state["run_id"],
        "relevant": True,
        "confidence": 0.91,
        "summary": "Strait of Hormuz tension may disrupt maritime transit to PSA Singapore.",
        "entities": {
            "location": "Strait of Hormuz",
            "event_type": "geopolitical tension",
            "date": "2026-08-25",
            "actors": ["Regional authorities", "Shipping operators"],
            "chokepoints_mentioned": ["Strait of Hormuz"],
        },
        "source_url": source_url,
        "extracted_at": "2026-08-25T00:00:00Z",
    }
