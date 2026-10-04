from __future__ import annotations

from pathlib import Path

from .agent import create_plan
from .fixer import apply_fix
from .scanner import scan_repository
from .tester import run_tests


def run_alphar(repository: Path) -> dict:
    activity = ["Repository analyzed"]
    analysis = scan_repository(repository)
    before = run_tests(repository)
    if before.passed:
        raise RuntimeError("The demo repository is already fixed; reset it before running again.")
    activity.append("Bug detected")

    plan = create_plan(analysis)
    activity.append("Root cause identified")
    activity.append("Fix generated")
    patch = apply_fix(repository, plan)
    activity.append("Patch applied")

    after = run_tests(repository)
    activity.append("Tests executed")
    if not after.passed:
        raise RuntimeError(f"Generated fix did not pass tests:\n{after.output}")
    activity.append("Fix verified")

    return {
        "repository": repository.name,
        "task": "Find and fix the calculator average bug.",
        "activity": activity,
        "analysis": analysis.as_dict(),
        "plan": plan.as_dict(),
        "tests_before": before.as_dict(),
        "tests_after": after.as_dict(),
        "patch": patch,
        "status": "VERIFIED",
    }

