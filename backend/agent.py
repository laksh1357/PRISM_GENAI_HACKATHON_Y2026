from __future__ import annotations

import json
import os
from dataclasses import dataclass

import httpx
from dotenv import load_dotenv

from .scanner import CodeIssue, RepositoryAnalysis

load_dotenv()


@dataclass
class AgentPlan:
    issue: CodeIssue
    root_cause: str
    proposed_fix: str
    replacement: str
    source: str
    ai_error: str | None = None

    def as_dict(self) -> dict:
        return {
            "issue": self.issue.__dict__,
            "root_cause": self.root_cause,
            "proposed_fix": self.proposed_fix,
            "replacement": self.replacement,
            "source": self.source,
            "ai_error": self.ai_error,
        }


def _local_plan(issue: CodeIssue) -> AgentPlan:
    return AgentPlan(
        issue=issue,
        root_cause=(
            "The average calculation uses floor division (`//`), which discards "
            "the fractional part of a result such as 5 / 2."
        ),
        proposed_fix="Use true division (`/`) so averages preserve fractional values.",
        replacement="/",
        source="deterministic fallback",
        ai_error="LLM_API_KEY and LLM_MODEL are not configured; used AST evidence instead.",
    )


def create_plan(
    analysis: RepositoryAnalysis,
    source_code: str,
    test_output: str,
) -> AgentPlan:
    if not analysis.issues:
        raise ValueError("No supported issue was detected in the repository.")
    issue = analysis.issues[0]
    api_key = os.getenv("LLM_API_KEY")
    endpoint = os.getenv("LLM_API_URL", "https://api.openai.com/v1/chat/completions")
    model = os.getenv("LLM_MODEL")
    if not api_key or not model:
        return _local_plan(issue)

    prompt = (
        "You are the AI Bug Hunter in a software engineering agent. Analyze the "
        "actual Python source, AST finding, and pytest output below. Return only "
        "valid JSON with keys issue, severity, affected_file, affected_function, "
        "root_cause, recommended_fix, replacement. replacement must be exactly "
        "the safe operator / for this demo. Do not invent test results.\n\n"
        f"AST finding: {json.dumps(issue.__dict__)}\n"
        f"Source:\n{source_code}\n"
        f"Pytest output:\n{test_output}"
    )
    try:
        response = httpx.post(
            endpoint,
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": model,
                "temperature": 0,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=20,
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        data = json.loads(content)
        replacement = data["replacement"]
        if replacement != "/":
            raise ValueError("LLM returned an unsafe replacement.")
        return AgentPlan(
            issue=issue,
            root_cause=data["root_cause"],
            proposed_fix=data["proposed_fix"],
            replacement=replacement,
            source=f"LLM ({model})",
        )
    except (httpx.HTTPError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        fallback = _local_plan(issue)
        fallback.ai_error = f"LLM request failed ({exc.__class__.__name__}); used AST fallback."
        return fallback
