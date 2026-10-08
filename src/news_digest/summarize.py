import json
import os

import anthropic

# Summaries we've already written, by article link, so each story is only
# sent to Claude once instead of on every refresh.
SUMMARY_CACHE = {}

INSTRUCTIONS = """You write Nick's morning news brief.
For each story below, write ONE clear sentence (at most 25 words) in English
saying what happened. Lead with who did what, for example
"OpenAI released a new model that can ..." Use only the information given.
Do not add opinions or details that are not in the story.

Stories:
"""

SCHEMA = {
    "type": "object",
    "properties": {
        "summaries": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "summary": {"type": "string"},
                },
                "required": ["id", "summary"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["summaries"],
    "additionalProperties": False,
}


def summarize_stories(client, stories):
    lines = []
    for i, story in enumerate(stories):
        lines.append(f"[{i}] {story['title']}\n{story['description']}")

    response = client.beta.messages.create(
        model="claude-opus-5-5",
        max_tokens=4000,
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        output_config={
            "effort": "low",
            "format": {"type": "json_schema", "schema": SCHEMA},
        },
        messages=[{"role": "user", "content": INSTRUCTIONS + "\n\n".join(lines)}],
    )
    if response.stop_reason != "end_turn":
        print("Claude did not finish:", response.stop_reason, flush=True)
        return

    text = next(block.text for block in response.content if block.type == "text")
    for item in json.loads(text)["summaries"]:
        if 0 <= item["id"] < len(stories):
            SUMMARY_CACHE[stories[item["id"]]["link"]] = item["summary"]


def add_summaries(sections):
    # No API key yet? Then the site simply shows headlines without summaries.
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return

    client = anthropic.Anthropic()
    for section in sections:
        new_stories = [s for s in section["stories"] if s["link"] not in SUMMARY_CACHE]
        if new_stories:
            try:
                summarize_stories(client, new_stories)
            except anthropic.APIError as error:
                print("Summary failed for", section["name"], "-", error, flush=True)
        for story in section["stories"]:
            story["summary"] = SUMMARY_CACHE.get(story["link"], "")
