from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class TestResult:
    passed: bool
    exit_code: int
    output: str

    def as_dict(self) -> dict:
        return {
            "passed": self.passed,
            "exit_code": self.exit_code,
            "output": self.output,
        }


def run_tests(repository: Path) -> TestResult:
    completed = subprocess.run(
        [sys.executable, "-m", "pytest", "-q"],
        cwd=repository,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    output = (completed.stdout + "\n" + completed.stderr).strip()
    return TestResult(completed.returncode == 0, completed.returncode, output)

