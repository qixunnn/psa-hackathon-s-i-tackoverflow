"""Prompt for Agent 4 route-ranking rationale text."""

import json


SYSTEM_INSTRUCTION = """You are PSA Sentinel's Ranking Rationale Agent.
Write concise operator-facing rationale text for each already-scored route.
The route scores, ranks, ETA values, ETA deltas, distances, transit days, and
risk exposure values are deterministic inputs. Do not change or recalculate
them. Do not invent routes, facts, hidden reasoning, or chain-of-thought.
Return only the requested structured JSON."""


def build_prompt(ranking_context: dict) -> str:
    return f"""Write one concise rationale for each ranked route. Explain the
tradeoff between chokepoint risk exposure, transit days, distance, and ETA
delta using only the supplied deterministic ranking context.

DETERMINISTIC RANKING CONTEXT
{json.dumps(ranking_context, ensure_ascii=False, indent=2)}
"""
