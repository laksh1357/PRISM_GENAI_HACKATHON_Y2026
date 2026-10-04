from __future__ import annotations

import json
import os
from dataclasses import dataclass

import httpx

from .scanner import CodeIssue, RepositoryAnalysis


@dataclass
class AgentPlan:
    issue: CodeIssue
    root_cause: str
    proposed_fix: str
    replacement: str
    source: str

    def as_dict(self) -> dict:
        return {
            "issue": self.issue.__dict__,
            "root_cause": self.root_cause,
            "proposed_fix": self.proposed_fix,
            "replacement": self.replacement,
            "source": self.source,
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
        source="local AST reasoning",
    )


def create_plan(analysis: RepositoryAnalysis) -> AgentPlan:
    if not analysis.issues:
        raise ValueError("No supported issue was detected in the repository.")
    issue = analysis.issues[0]
    api_key = os.getenv("LLM_API_KEY")
    endpoint = os.getenv("LLM_API_URL", "https://api.openai.com/v1/chat/completions")
    model = os.getenv("LLM_MODEL")
    if not api_key or not model:
        return _local_plan(issue)

    prompt = (
        "Analyze this AST finding. Return JSON with root_cause, proposed_fix, "
        "and replacement. The replacement must be exactly one character. "
        f"Finding: {json.dumps(issue.__dict__)}"
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
    except (httpx.HTTPError, KeyError, TypeError, ValueError, json.JSONDecodeError):
        return _local_plan(issue)

