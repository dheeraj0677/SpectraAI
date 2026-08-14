# Contributing to SpectraAI

Thank you for contributing! Please read these guidelines before opening a PR.

---

## Environment Setup

**Requirements:**
- Python ≥ 3.12 (tested on 3.13.11)
- Node.js ≥ 18 (tested on 24.13.0)

### Backend
```bash
cd backend
pip install -r requirements.txt
# Optional — enables real Claude Vision extraction:
# set ANTHROPIC_API_KEY=your-key-here
python main.py
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

---

## Running Tests

```bash
# From the project root
python test_e2e.py
```

All 95 tests must pass before submitting a PR. The suite runs entirely in **fallback/demo mode** (no API key required) to verify all pure-Python pipeline logic.

If `ANTHROPIC_API_KEY` is set, the extraction stage will call Claude Vision instead of the built-in fallback. Test results may differ from the baseline `test_report.json` in that mode.

---

## Branch Naming

Create a focused branch for each change:

```
improvement/<short-phase-name>   # e.g. improvement/phase1-stabilize
fix/<short-issue-description>    # e.g. fix/conflict-merge-edge-case
feat/<short-feature-name>        # e.g. feat/pdf-table-extraction
docs/<short-doc-name>            # e.g. docs/api-reference
```

---

## Commit Messages (Conventional Commits)

Use the [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>(<scope>): <short summary>

<optional longer body>

<optional footer>
```

| Type | When to use |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `refactor` | Code change with no behavior change |
| `test` | Adding or updating tests |
| `chore` | Build, config, or tooling changes |

**Examples:**
```
fix(extract): correct power_watts unit annotation (kW → W)
feat(pipeline): add async batch job queue endpoint
docs(readme): clarify Python version requirement
```

---

## Collaboration Rules

1. **Preserve existing behaviour** unless the PR explicitly documents a behavior change and its migration notes.
2. **Do not delete large areas of code** to "clean up" — make targeted changes.
3. **No API keys, tokens, credentials, or database files** in commits. The `.gitignore` already excludes `*.db`, `backend/uploads/*`, and `.env`.
4. **No production readiness claims** unless benchmarks are reproduced with a documented method.
5. **Treat fallback/demo mode separately** from real Claude API mode — document which mode is being tested.
6. **Human review step required** before merging to `main`. Do not self-merge.

---

## Fallback vs. Real-API Mode

SpectraAI has two extraction modes:

| Mode | When Active | Behavior |
|------|------------|----------|
| **Fallback/Demo** | `ANTHROPIC_API_KEY` not set | Returns pre-seeded synthetic data for the UltraDrive X500 demo product |
| **Live Claude API** | `ANTHROPIC_API_KEY` set | Calls Claude Vision (claude-sonnet-4-6) for real structured extraction |

The 95-test E2E suite runs in fallback mode. Fallback responses are deterministic and reproducible without any external service.

---

## File Structure

```
SpectraAI/
├── backend/                  # FastAPI application (Python)
│   ├── main.py               # API routes
│   ├── pipeline.py           # 6-stage intelligence pipeline orchestrator
│   ├── extract.py            # Claude Vision / fallback extraction
│   ├── merge.py              # Multi-source conflict resolution
│   ├── enrich.py             # RAG enrichment + UNSPSC/ETIM taxonomy
│   ├── validate.py           # Validation rules + CRI scorecard
│   ├── knowledge_graph.py    # NetworkX graph + anomaly detection
│   ├── human_review.py       # Human-in-the-loop edit + approval
│   ├── database.py           # SQLite async persistence (aiosqlite)
│   ├── models.py             # Pydantic v2 data models
│   ├── ingest.py             # File upload + SHA-256 source registration
│   └── seed_kb/              # Embedded RAG knowledge base (JSON)
├── frontend/                 # React + Vite dashboard (D3.js)
│   └── src/components/       # 8 UI components
├── test_e2e.py               # 95-test end-to-end suite
├── test_report.json          # Latest test run results
└── run_backend.bat           # One-click Windows launcher
```
