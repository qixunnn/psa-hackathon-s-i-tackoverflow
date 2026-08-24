"""Canned risk assessment agent."""

import time


def run(state: dict) -> dict:
    time.sleep(1)
    return {
        "run_id": state["run_id"],
        "severity": "High",
        "probability": 0.7,
        "affected_chokepoints": ["Strait of Hormuz"],
        "estimated_duration": "3-5 days",
        "rationale": "Tension at the Strait of Hormuz creates a material risk of transit delay.",
    }
