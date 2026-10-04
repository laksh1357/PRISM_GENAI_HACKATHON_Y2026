from __future__ import annotations

import ast
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class CodeIssue:
    file: str
    line: int
    category: str
    title: str
    explanation: str
    evidence: str


@dataclass
class RepositoryAnalysis:
    files: list[str]
    functions: list[str]
    classes: list[str]
    issues: list[CodeIssue]

    def as_dict(self) -> dict:
        return {
            "files": self.files,
            "functions": self.functions,
            "classes": self.classes,
            "issues": [asdict(issue) for issue in self.issues],
        }


def _relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def scan_repository(root: Path) -> RepositoryAnalysis:
    if not root.is_dir():
        raise ValueError(f"Repository does not exist: {root}")

    files: list[str] = []
    functions: list[str] = []
    classes: list[str] = []
    issues: list[CodeIssue] = []

    for path in sorted(root.rglob("*.py")):
        relative_path = path.relative_to(root)
        if any(
            part.startswith(".") or part == "__pycache__"
            for part in relative_path.parts
        ):
            continue
        relative = relative_path.as_posix()
        files.append(relative)
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=relative)
        except SyntaxError as exc:
            issues.append(
                CodeIssue(
                    relative,
                    exc.lineno or 1,
                    "syntax",
                    "Syntax error",
                    "Python could not parse this file.",
                    str(exc),
                )
            )
            continue

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                functions.append(f"{relative}:{node.name}")
            elif isinstance(node, ast.ClassDef):
                classes.append(f"{relative}:{node.name}")
            elif isinstance(node, ast.BinOp) and isinstance(node.op, ast.FloorDiv):
                issues.append(
                    CodeIssue(
                        relative,
                        node.lineno,
                        "logic",
                        "Unexpected floor division",
                        "Floor division truncates fractional results and is suspicious in a calculator average.",
                        ast.unparse(node),
                    )
                )

    return RepositoryAnalysis(files, functions, classes, issues)
