#!/usr/bin/env python3
"""Otter meeting digest helper.

Usage:
  python app.py --input sample_transcript.txt --output digest.md
"""
from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


ACTION_PATTERNS = [
    r"\baction item\b",
    r"\bTODO\b",
    r"\bI'll\b",
    r"\bI will\b",
    r"\bwe should\b",
    r"\bnext step\b",
    r"\bfollow up\b",
    r"\bdeadline\b",
]

QUESTION_PATTERNS = [r"\?$", r"\bcan we\b", r"\bshould we\b", r"\bwhat if\b", r"\bhow do we\b"]

TOPIC_KEYWORDS = {
    "product": ["feature", "roadmap", "release", "bug", "backlog"],
    "sales": ["prospect", "deal", "pipeline", "renewal", "contract"],
    "ops": ["process", "incident", "runbook", "on-call", "sla"],
    "finance": ["budget", "forecast", "expense", "revenue", "invoice"],
}


@dataclass
class MeetingDigest:
    generated_at: str
    title: str
    topics: list[str]
    action_items: list[str]
    decisions: list[str]
    open_questions: list[str]
    highlights: list[str]


def read_lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


def detect_topics(lines: Iterable[str]) -> list[str]:
    content = " ".join(lines).lower()
    found: list[str] = []
    for topic, words in TOPIC_KEYWORDS.items():
        if any(word in content for word in words):
            found.append(topic)
    return found or ["general"]


def pick_matches(lines: Iterable[str], patterns: list[str], limit: int = 12) -> list[str]:
    selected: list[str] = []
    for line in lines:
        for pat in patterns:
            if re.search(pat, line, flags=re.IGNORECASE):
                selected.append(line)
                break
        if len(selected) >= limit:
            break
    return selected


def pick_decisions(lines: Iterable[str], limit: int = 8) -> list[str]:
    decision_markers = [r"\bdecided\b", r"\bagreed\b", r"\bwe'll\b", r"\bapproved\b"]
    return pick_matches(lines, decision_markers, limit=limit)


def build_digest(text: str, title: str = "Meeting Digest") -> MeetingDigest:
    lines = read_lines(text)
    topics = detect_topics(lines)
    action_items = pick_matches(lines, ACTION_PATTERNS, limit=12)
    decisions = pick_decisions(lines, limit=8)
    questions = pick_matches(lines, QUESTION_PATTERNS, limit=8)
    highlights = lines[: min(10, len(lines))]

    return MeetingDigest(
        generated_at=datetime.now(timezone.utc).isoformat(),
        title=title,
        topics=topics,
        action_items=action_items,
        decisions=decisions,
        open_questions=questions,
        highlights=highlights,
    )


def render_markdown(digest: MeetingDigest) -> str:
    def section(name: str, items: list[str]) -> str:
        if not items:
            return f"## {name}\n- _(none found)_"
        return "\n".join([f"## {name}"] + [f"- {item}" for item in items])

    blocks = [
        f"# {digest.title}",
        f"Generated: {digest.generated_at}",
        "",
        f"**Topics:** {', '.join(digest.topics)}",
        "",
        section("Action Items", digest.action_items),
        "",
        section("Decisions", digest.decisions),
        "",
        section("Open Questions", digest.open_questions),
        "",
        section("Highlights", digest.highlights),
    ]
    return "\n".join(blocks).strip() + "\n"


def maybe_llm_enrich(raw_text: str, digest: MeetingDigest) -> MeetingDigest:
    """Optionally enrich using OpenAI if SDK + API key is available.

    Safe fallback: returns heuristic digest if not configured.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return digest

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        prompt = (
            "You are a concise meeting analyst. Return strict JSON with keys: "
            "topics (string[]), action_items (string[]), decisions (string[]), "
            "open_questions (string[]), highlights (string[])."
        )
        resp = client.responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
            input=[
                {"role": "system", "content": prompt},
                {
                    "role": "user",
                    "content": f"Transcript:\n{raw_text[:15000]}\n\nSeed summary:\n{json.dumps(asdict(digest))}",
                },
            ],
            temperature=0.2,
            max_output_tokens=1200,
        )
        text = getattr(resp, "output_text", "").strip()
        data = json.loads(text)
        return MeetingDigest(
            generated_at=digest.generated_at,
            title=digest.title,
            topics=data.get("topics", digest.topics),
            action_items=data.get("action_items", digest.action_items),
            decisions=data.get("decisions", digest.decisions),
            open_questions=data.get("open_questions", digest.open_questions),
            highlights=data.get("highlights", digest.highlights),
        )
    except Exception:
        return digest


def main() -> None:
    parser = argparse.ArgumentParser(description="Build daily meeting digests from Otter transcripts")
    parser.add_argument("--input", required=True, help="Path to transcript text file")
    parser.add_argument("--output", required=True, help="Output markdown path")
    parser.add_argument("--title", default="Otter Meeting Digest")
    parser.add_argument("--json-output", help="Optional JSON output path")
    args = parser.parse_args()

    in_path = Path(args.input)
    out_path = Path(args.output)
    raw_text = in_path.read_text(encoding="utf-8")

    digest = build_digest(raw_text, title=args.title)
    digest = maybe_llm_enrich(raw_text, digest)

    out_path.write_text(render_markdown(digest), encoding="utf-8")
    if args.json_output:
        Path(args.json_output).write_text(json.dumps(asdict(digest), indent=2), encoding="utf-8")

    print(f"Wrote digest: {out_path}")


if __name__ == "__main__":
    main()
