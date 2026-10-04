# ALPHAR

ALPHAR (Autonomous Software Engineering Agent) is a simple hackathon MVP that
demonstrates this workflow:

```text
Repository → Analyze → Detect Bug → Explain → Generate Test
→ Generate Fix → Run Test → Show Diff
```

The current demo is intentionally restricted to the included `demo_repo`. It
uses Python AST analysis to find the calculator's floor-division bug, runs the
real pytest suite before and after the patch, sends the actual source and
failing test output to an OpenAI-compatible LLM when configured, applies a
guarded source change, and displays the actual unified diff. If LLM settings
are unavailable or the request fails, the UI explicitly labels the
deterministic AST fallback; it never claims that an LLM ran.

## Project structure

```text
ALPHAR/
├── backend/       # FastAPI application and demo workflow
├── frontend/      # Streamlit application
├── demo_repo/     # Intentionally buggy calculator repository
├── tests/         # Automated tests
├── docs/          # Project documentation
├── .env.example   # Environment variable template
├── .gitignore
├── requirements.txt
└── README.md
```

## Requirements

- Python 3.10 or newer
- An optional OpenAI-compatible LLM API key

## Setup

From the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

The `.env` file is ignored by Git. Do not commit API keys or other secrets.

## Start the backend

From the project root, with the virtual environment activated:

```bash
uvicorn backend.main:app --reload
```

The API will be available at <http://127.0.0.1:8000>. Check it with:

```bash
curl http://127.0.0.1:8000/health
```

Interactive API documentation is available at
<http://127.0.0.1:8000/docs>.

The demo endpoint is `POST /run`. It is intentionally limited to the checked-in
demo repository.

## Team

**VITV_ALPHAR_1**

| Member | Registration No. | Role |
| --- | --- | --- |
| Lakshya Singh | 24BDS0054 | Team Lead / AI & Backend |
| Hardik Vikas Jain | 24BCI0294 | AI / Backend |
| Rupanshu | 24BCI0308 | Frontend / Integration |
| Apoorv Sharma | 24BCT0243 | Testing / Engineering |

**College:** VIT Vellore

**Hackathon:** Samsung PRISM | Gen AI Hackathon 2026

**Required Git tag:** `PRISM_GENAI_HACKATHON_Y2026`

## Start the frontend

Open a second terminal, activate the same virtual environment, and run:

```bash
streamlit run frontend/app.py
```

Streamlit will print the local URL, normally
<http://localhost:8501>.
