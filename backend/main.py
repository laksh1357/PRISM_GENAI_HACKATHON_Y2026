from pathlib import Path

from fastapi import FastAPI, HTTPException

from .orchestrator import run_alphar

app = FastAPI(title="ALPHAR API", version="0.1.0")
DEMO_REPOSITORY = Path(__file__).resolve().parents[1] / "demo_repo"


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/run")
def run() -> dict:
    try:
        return run_alphar(DEMO_REPOSITORY)
    except (RuntimeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
