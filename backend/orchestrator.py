from __future__ import annotations

from pathlib import Path

from .agent import create_plan
from .fixer import apply_fix
from .scanner import scan_repository
from .tester import run_tests


def run_alphar(repository: Path) -> dict:
    analysis = scan_repository(repository)
    before = run_tests(repository)
    if before.passed:
        raise RuntimeError("The demo repository is already fixed; reset it before running again.")

    issue = analysis.issues[0] if analysis.issues else None
    if issue is None:
        raise RuntimeError("No supported issue was detected in the repository.")
    source_code = (repository / issue.file).read_text(encoding="utf-8")
    plan = create_plan(analysis, source_code, before.output)
    patch = apply_fix(repository, plan)

    after = run_tests(repository)
    if not after.passed:
        raise RuntimeError(f"Generated fix did not pass tests:\n{after.output}")

    return {
        "repository": repository.name,
        "task": "Find and fix the calculator average bug.",
        "activity": [
            {"agent": "Supervisor", "status": "complete", "message": "Workflow coordinated"},
            {"agent": "Explorer", "status": "complete", "message": "Repository analyzed"},
            {"agent": "AI Bug Hunter", "status": "complete", "message": "Bug detected and explained"},
            {"agent": "Fix Agent", "status": "complete", "message": "Fix generated and patch applied"},
            {"agent": "Test Runner", "status": "complete", "message": "Tests executed before and after"},
            {"agent": "Verification Agent", "status": "complete", "message": "Fix verified"},
        ],
        "analysis": analysis.as_dict(),
        "plan": plan.as_dict(),
        "tests_before": before.as_dict(),
        "tests_after": after.as_dict(),
        "patch": patch,
        "status": "VERIFIED",
    }
