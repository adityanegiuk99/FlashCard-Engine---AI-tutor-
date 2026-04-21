from __future__ import annotations

import json
import re
from textwrap import dedent

from openai import OpenAI

from app.config import settings


SYSTEM_PROMPT = dedent(
    """
    You are building a high-retention flashcard deck from educational material.
    Generate specific, concept-rich cards that test active recall.
    Favor:
    - precise definitions
    - relationships and comparisons
    - small examples
    - beginner-friendly phrasing

    Avoid:
    - vague trivia
    - cards whose answer is a single unexplained keyword
    - duplicate questions

    Return valid JSON only.
    """
).strip()

FLASHCARD_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "cards": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "question": {"type": "string"},
                    "answer": {"type": "string"},
                    "concept": {"type": "string"},
                    "difficulty": {
                        "type": "string",
                        "enum": ["easy", "medium", "hard"],
                    },
                },
                "required": ["question", "answer", "concept", "difficulty"],
            },
        }
    },
    "required": ["cards"],
}

REGENERATE_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "question": {"type": "string"},
        "answer": {"type": "string"},
        "concept": {"type": "string"},
        "difficulty": {
            "type": "string",
            "enum": ["easy", "medium", "hard"],
        },
    },
    "required": ["question", "answer", "concept", "difficulty"],
}


def _client() -> OpenAI:
    if not settings.openrouter_api_key:
        raise ValueError("OPENROUTER_API_KEY is missing.")
    return OpenAI(
        api_key=settings.openrouter_api_key,
        base_url="https://openrouter.ai/api/v1",
    )


def _parse_json_response(response_text: str, fallback_label: str) -> dict:
    text = (response_text or "").strip()
    if not text:
        raise ValueError(f"{fallback_label} returned an empty response.")

    fenced_match = re.search(r"```(?:json)?\s*(.*?)```", text, flags=re.DOTALL)
    if fenced_match:
        text = fenced_match.group(1).strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        first_brace = text.find("{")
        last_brace = text.rfind("}")
        if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
            return json.loads(text[first_brace : last_brace + 1])
        raise ValueError(f"{fallback_label} did not return valid JSON: {text[:200]}")


def generate_flashcards(title: str, excerpt: str, summary: list[dict]) -> list[dict]:
    client = _client()
    prompt = dedent(
        f"""
        Create 10 to 16 flashcards for a study deck titled "{title}".
        Use the source summary and excerpt below.

        Summary:
        {json.dumps(summary, indent=2)}

        Excerpt:
        {excerpt[:10000]}

        Return JSON with this schema:
        {{
          "cards": [
            {{
              "question": "string",
              "answer": "string",
              "concept": "string",
              "difficulty": "easy|medium|hard"
            }}
          ]
        }}
        """
    ).strip()

    response = client.chat.completions.create(
        model=settings.openrouter_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"},
    )
    payload = _parse_json_response(response.choices[0].message.content, "Flashcard generation")
    return payload["cards"]


def explain_flashcard(question: str, answer: str) -> str:
    client = _client()
    prompt = dedent(
        f"""
        Explain this flashcard like you are tutoring a beginner.
        Include:
        1. the core idea
        2. why it matters
        3. one tiny example or analogy

        Question: {question}
        Answer: {answer}
        """
    ).strip()

    response = client.chat.completions.create(
        model=settings.openrouter_model,
        messages=[
            {"role": "user", "content": prompt},
        ],
    )
    return (response.choices[0].message.content or "").strip()


def regenerate_flashcard(question: str, answer: str, concept: str) -> dict:
    client = _client()
    prompt = dedent(
        f"""
        Improve this flashcard so it tests understanding better.

        Current question: {question}
        Current answer: {answer}
        Concept: {concept}

        Return JSON:
        {{
          "question": "string",
          "answer": "string",
          "concept": "string",
          "difficulty": "easy|medium|hard"
        }}
        """
    ).strip()

    response = client.chat.completions.create(
        model=settings.openrouter_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"},
    )
    return _parse_json_response(response.choices[0].message.content, "Card regeneration")