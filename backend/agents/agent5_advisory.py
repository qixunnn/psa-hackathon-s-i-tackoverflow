"""Canned advisory agent."""

import time


def run(state: dict) -> dict:
    time.sleep(1)
    return {
        "run_id": state["run_id"],
        "headline": "Prepare for possible Strait of Hormuz delay",
        "summary": "Strait of Hormuz tension may delay the vessel by several days.",
        "recommended_actions": [
            "Flag berth slot for possible delay",
            "Notify transshipment partners",
        ],
        "confidence": 0.85,
        "operator_decision": "pending",
        "operator_comment": None,
    }
