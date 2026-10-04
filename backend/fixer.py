from __future__ import annotations

import difflib
from pathlib import Path

from .agent import AgentPlan


def apply_fix(repository: Path, plan: AgentPlan) -> dict:
    target = (repository / plan.issue.file).resolve()
    repository_root = repository.resolve()
    if repository_root not in target.parents or target.suffix != ".py":
        raise ValueError("Refusing to patch a file outside the demo repository.")

    before = target.read_text(encoding="utf-8")
    old_expression = plan.issue.evidence
    if plan.replacement not in {"/"}:
        raise ValueError("Refusing to apply an unapproved code replacement.")
    new_expression = old_expression.replace("//", plan.replacement, 1)
    if old_expression not in before:
        raise ValueError("Expected vulnerable expression was not found; refusing to patch.")
    after = before.replace(old_expression, new_expression, 1)
    target.write_text(after, encoding="utf-8")
    diff = "".join(
        difflib.unified_diff(
            before.splitlines(keepends=True),
            after.splitlines(keepends=True),
            fromfile=plan.issue.file,
            tofile=plan.issue.file,
        )
    )
    return {"file": plan.issue.file, "before": before, "after": after, "diff": diff}
