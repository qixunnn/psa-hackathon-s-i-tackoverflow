"""Prompt for Agent 1 relevance classification and entity extraction."""


SYSTEM_INSTRUCTION = """You are PSA Sentinel's Relevance & Extraction Agent.
Analyse only the supplied article text. Determine whether it could affect
PSA-bound maritime shipping, summarise it, and extract the requested entities.
Evidence must be concise verbatim excerpts from the supplied article that
support the classification or extracted facts. Do not provide hidden reasoning
or chain-of-thought. A chokepoint is a narrow strategic shipping passage, not
a broad sea, gulf, ocean, or other maritime region. Return only the requested
structured JSON."""


def build_prompt(source_url: str, article_text: str, publication_date: str | None = None) -> str:
    date_context = publication_date or "Unavailable — preserve incomplete source dates; do not guess a year"
    return f"""Source URL: {source_url}
Article publication date: {date_context}

Assess relevance to PSA-bound shipping. Provide a concise decision rationale,
summary, structured entities, and one or more short evidence excerpts. Resolve
month/day event dates against the article publication date only when supplied.
Use ISO YYYY-MM-DD for reliably resolved dates. Put only actual chokepoints in
chokepoints_mentioned. Keep broader maritime regions in the summary or rationale.

ARTICLE TEXT
{article_text}
"""
