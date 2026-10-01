# Portfolio Analysis / Optimization

Takes a user's existing portfolio, splits it into investment tracks, flags redundant holdings, and reports on risk — using an LLM (Claude or Codex) for the parts that are hard to hard-code.

## Overview

Given a user's holdings, this service categorizes each position, finds stocks that are dominated by a better name in the same track, recommends removals, and produces per-stock and portfolio-level risk analysis.

**Open question:** the optimization metric isn't fixed yet. The definition of "dominated" and the risk analysis both depend on it (candidates: Sharpe ratio, a mean-variance objective, or a drawdown-based measure). Decide this before implementing the dominance step.

## Pipeline

1. **Intake** — accept and parse a user's holdings into a normalized list.
2. **Classify** — call the LLM (Claude/Codex) to assign each holding to an investment track.
3. **Per-stock metrics** — compute volatility and the chosen optimization metric for each holding.
4. **Dominance** — within each track, compare stocks and flag the dominated ones (a stock beaten by another in the same track).
5. **Recommendations** — surface the dominated stocks as removal candidates.
6. **Risk report** — compute portfolio-level risk (concentration, overall riskiness) and assemble the analysis output.

## Tech stack

- **LLM:** Claude or Codex API (portfolio reading + track classification)
- **Pipeline & risk metrics:** Python, pandas, NumPy
- **Data store:** PostgreSQL (shared with the Nexus integration)

## Setup

Do this once, before your first work session. It takes about 10 minutes.

### 1. Install Python 3.11

**3.11 recommended, 3.12 okay, 3.13+ won't install.**

| Python | Works? | Why |
|---|---|---|
| 3.11 | ✅ Recommended | Matches production exactly |
| 3.12 | ✅ Okay | Installs fine, but CI runs on 3.11, so a few newer-only syntax features will fail there (see below) |
| 3.13, 3.14 | ❌ | Our pinned numpy (1.26.4) has no ready-made install for them, so `pip install` tries to compile it from source, which is slow and usually fails |

Why 3.11: production runs 3.11, and code written on a newer Python can use syntax 3.11 rejects. For example, `f"{row["ticker"]}"` (same quote type inside an f-string) works on 3.12 but is a `SyntaxError` on 3.11. Use `f"{row['ticker']}"` instead.

- Windows: install it from [python.org](https://www.python.org/downloads/release/python-3119/). Check with `py -3.11 --version`.
- Mac: `brew install python@3.11`. Check with `python3.11 --version`.

You can keep other Python versions installed. The virtual environment in step 3 picks 3.11 for this project. (On 3.12, replace `3.11` with `3.12` in the commands below.)

### 2. Get the code

```bash
git clone <repo-url>
cd Portfolio-Analysis
```

### 3. Create and activate a virtual environment

A virtual environment (venv) is a private folder of packages for this project, so it doesn't clash with your other projects. It lives in `.venv/`, which git ignores.

Windows (PowerShell):

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
```

Mac / Linux:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

Your prompt should now start with `(.venv)`, and `python --version` should print 3.11 (or 3.12). **Activate the venv every time you open a new terminal.**

In VS Code, run "Python: Select Interpreter" and pick the one in `.venv`.

### 4. Install packages

```bash
pip install -r requirements.txt
```

### 5. Add the Plaid keys

You've been invited to our Plaid team. Copy the example file to `.env` in the repo root (the same folder as this README):

```bash
cp .env.example .env        # Mac / Linux
copy .env.example .env      # Windows
```

Open `.env` and fill in both values from the [Plaid dashboard → Developers → Keys](https://dashboard.plaid.com/developers/keys):

- `PLAID_CLIENT_ID`: the client ID
- `PLAID_SECRET`: the **Sandbox** secret (not Production)

**Never commit `.env`, and never paste keys into code, Slack or screenshots.** Git already ignores `.env`.

### 6. Set up the database and check that everything works

```bash
cd backend
python manage.py migrate
python manage.py test plaid_integration
```

If the tests *run*, your setup works, even if some of them fail. Failing tests are expected while a task is unfinished. Run all `manage.py` commands from the `backend/` folder.

### 7. (Optional) Run the website

```bash
python manage.py createsuperuser    # once, to make a login for yourself
python manage.py runserver
```

Then open http://127.0.0.1:8000/admin/ and log in. Stop the server with Ctrl+C.

### Troubleshooting

| Problem | Fix |
|---|---|
| `KeyError: 'PLAID_CLIENT_ID'` | `.env` is missing, empty, or not in the repo root. Redo step 5. |
| `ModuleNotFoundError: No module named 'django'` | Your venv isn't active. Activate it (step 3). |
| `pip install` shows "Building wheel for numpy" or "for pandas" for minutes, or fails while building | Your venv uses Python 3.13 or newer. Delete `.venv` and redo step 3 with 3.11. |
| Windows: "running scripts is disabled on this system" | Run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once, then activate again. |
| `python manage.py` says "No such file" | You're not in `backend/`. Run `cd backend`. |

## Suggested project structure

\`\`\`
portfolio-analysis/
├── src/
│   ├── intake.py       # parse holdings into a normalized list
│   ├── classify.py     # LLM call → track assignment
│   ├── metrics.py      # volatility + optimization metric
│   ├── dominance.py    # flag dominated stocks per track
│   └── risk.py         # portfolio-level risk analysis
├── prompts/            # LLM prompt templates
├── requirements.txt
└── README.md
\`\`\`

## Roadmap

- [ ] Decide the optimization metric
- [ ] Portfolio intake + normalization
- [ ] LLM track-classification step
- [ ] Per-stock metrics
- [ ] Dominance detection + removal recommendations
- [ ] Portfolio-level risk report

## Resources

- Claude API — Get started (official docs): https://platform.claude.com/docs/en/get-started
- Anthropic Academy — Build with Claude (free course): https://www.anthropic.com/learn/build-with-claude
- Anthropic Cookbook / Quickstarts (runnable code samples): https://github.com/anthropics/claude-quickstarts
- PostgreSQL — official tutorial: https://www.postgresql.org/docs/current/tutorial.html
- PostgreSQL + Python (psycopg guide): https://neon.com/postgresql/python