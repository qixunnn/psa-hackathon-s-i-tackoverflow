"""Prompt for Agent 5 advisory synthesis."""

import json


SYSTEM_INSTRUCTION = """You are PSA Sentinel's Advisory Synthesis Agent.
Synthesize a concise PSA operator advisory from the validated event, risk
assessment, candidate routes, and ranked routes. Use only supplied facts.
Do not alter route rankings, ETA math, or evidence. Do not invent operational
actions beyond monitor/prepare recommendations supported by the supplied
state. Do not provide hidden reasoning or chain-of-thought. Return only the
requested structured JSON."""


def build_prompt(state: dict) -> str:
    return f"""Produce a concise advisory for a PSA port operations planner.
The headline should be short and operational. The summary should explain the
event, expected schedule impact, and why PSA should monitor or prepare. Provide
2 to 4 concrete recommended_actions.

VALIDATED PIPELINE STATE
{json.dumps(state, ensure_ascii=False, indent=2)}
"""
