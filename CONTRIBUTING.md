# Contributing to SpectraAI

Thank you for contributing to SpectraAI! Please read this guide before making changes or opening a pull request.

---

## ⚡ Native Tooling Quickstart (No Containers Required)

SpectraAI uses native Python and Node.js developer tooling for high performance, zero container overhead, and instant iteration.

### System Prerequisites
- **Python:** `≥ 3.12` (tested on `3.12` and `3.13` — see [`.python-version`](.python-version))
- **Node.js:** `≥ 18` (tested on `20` and `24` — see [`.nvmrc`](.nvmrc))
- **Package Managers:** Python `uv` (recommended) or `pip`/`venv`; Node `npm` (with Corepack)
- **Git:** Standard git client

---

### 1. Clone & Setup Repository

```bash
git clone https://github.com/dheeraj0677/SpectraAI.git
cd SpectraAI
```

#### Option A: Fast Setup with `uv` (Recommended)
```bash
# Set up Python virtual environment and install backend dependencies:
uv venv .venv
uv pip install -r backend/requirements.txt

# Set up frontend dependencies:
corepack enable
npm --prefix frontend install
```

#### Option B: Setup with Cross-Platform Task Runner (`task.py`)
```bash
python task.py setup
```

#### Option C: Setup with `make` (macOS / Linux / Windows with Make)
```bash
make setup
```

#### Option D: Standard Python `venv` Fallback
```bash
# Windows:
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r backend\requirements.txt
npm --prefix frontend install

# macOS / Linux:
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
npm --prefix frontend install
```

---

### 2. Configure Environment Variables (Optional)

SpectraAI runs completely locally in **Deterministic Fallback/Demo Mode** without any paid API key. If you wish to test live Claude 3.5 Sonnet extraction:

```bash
# Copy example configuration template:
cp .env.example .env

# Edit .env and supply:
# ANTHROPIC_API_KEY=your-api-key-here
```

---

### 3. Start Development Servers

#### Backend (FastAPI on Port 8000)
```bash
# Using task runner:
python task.py run-backend

# Or manually:
cd backend && python main.py
```
*(Windows shortcut: double-click `run_backend.bat` | macOS/Linux: `./run_backend.sh`)*

→ **Backend API:** [`http://localhost:8000`](http://localhost:8000)  
→ **Swagger Docs:** [`http://localhost:8000/docs`](http://localhost:8000/docs)  
→ **Diagnostics:** [`http://localhost:8000/api/diagnostics`](http://localhost:8000/api/diagnostics)

#### Frontend (Vite Dashboard on Port 5173)
In a separate terminal:
```bash
# Using task runner:
python task.py run-frontend

# Or manually:
cd frontend && npm run dev
```
*(Windows shortcut: double-click `run_frontend.bat` | macOS/Linux: `./run_frontend.sh`)*

→ **Interactive Dashboard:** [`http://localhost:5173`](http://localhost:5173)

---

## 🛠️ Cross-Platform Task Commands Reference

| Task Goal | `task.py` (Python) | `Makefile` (Make) | Manual Equivalent |
|---|---|---|---|
| **Full Setup** | `python task.py setup` | `make setup` | `uv venv && uv pip install -r backend/requirements.txt && npm --prefix frontend install` |
| **Backend Setup** | `python task.py setup-backend` | `make setup-backend` | `uv pip install -r backend/requirements.txt` |
| **Frontend Setup** | `python task.py setup-frontend` | `make setup-frontend` | `npm --prefix frontend install` |
| **Run Backend** | `python task.py run-backend` | `make run-backend` | `cd backend && python main.py` |
| **Run Frontend** | `python task.py run-frontend` | `make run-frontend` | `cd frontend && npm run dev` |
| **Run All Tests** | `python task.py test` | `make test` | `pytest -v && python test_e2e.py && npm --prefix frontend test` |
| **Build Frontend** | `python task.py build` | `make build` | `npm --prefix frontend run build` |
| **Reset Demo State** | `python task.py reset-demo` | `make reset-demo` | Remove `backend/product_intelligence.db` and upload files |
| **Clean Workspace** | `python task.py clean` | `make clean` | Remove `__pycache__`, `.pytest_cache`, `frontend/dist` |

---

## 🧪 Testing & Verification Workflow

Before opening a pull request, verify that all test suites pass cleanly:

```bash
python task.py test
```

Or run individual suites:

### 1. Pytest Suite (Unit, Integration, API, E2E)
```bash
pytest -v
```

### 2. Compatibility E2E Runner (131 Tests)
```bash
python test_e2e.py
```

### 3. Frontend Smoke Tests & Production Build
```bash
npm --prefix frontend test
npm --prefix frontend run build
```

### 4. Zero Deprecation Warnings Check
```bash
python -W error::DeprecationWarning -c "import backend.models, backend.main, backend.pipeline, backend.extract, backend.merge, backend.enrich, backend.knowledge_graph, backend.validate, backend.database, backend.human_review, backend.ingest, backend.normalize, backend.config, backend.telemetry; print('Clean!')"
```

---

## 🔄 Resetting Local State

To reset local state to an initial pristine condition:

```bash
python task.py reset-demo
```

*When `backend/main.py` is started, it will detect an empty database and automatically seed the baseline `PROD-DEMO-X500` demo product.*

---

## 🚨 Troubleshooting Setup Failures

If you encounter issues setting up SpectraAI locally:

1. **Python Version Incompatibility:** Ensure `python --version` outputs `3.12.x` or `3.13.x`. Older Python versions (<3.12) lack timezone-aware features.
2. **Port 8000 / 5173 in Use:** Set `PORT=8001` in `.env` for the backend. Vite will automatically prompt for port `5174` if 5173 is occupied.
3. **Missing `uv`:** Install `uv` via `pip install uv` or `curl -LsSf https://astral.sh/uv/install.sh`. If preferred, standard `python -m venv` works identically.
4. **SQLite Database Locks:** If multi-process tests lock the database, run `python task.py reset-demo` to re-initialize a fresh database.
5. **Reporting Failures:** If you encounter an unresolvable setup bug, please file an issue using our [Bug Report Template](https://github.com/dheeraj0677/SpectraAI/issues/new?template=bug_report.yml) detailing OS, Python version, Node version, and error logs.

---

## 🌿 Branch Naming & Commits

- **Branch Naming:**
  - `feat/<short-feature-name>`
  - `fix/<short-issue-description>`
  - `improvement/<short-improvement-name>`
  - `docs/<short-doc-name>`
  - `test/<short-test-name>`
- **Commit Messages:** Follow [Conventional Commits](https://www.conventionalcommits.org/) (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`).

---

## ✅ Pull Request Review Checklist

- [ ] Tested cleanly using native tooling (`uv` / `venv` and `npm`).
- [ ] No Docker, container configurations, or runtime databases committed.
- [ ] `python task.py test` passes completely (Pytest, E2E, Frontend smoke).
- [ ] Frontend builds cleanly with `npm --prefix frontend run build`.
- [ ] Zero secrets, private data, or hardcoded keys in `.env` or code.
- [ ] All timestamps use timezone-aware `datetime.now(timezone.utc)`.
- [ ] Convenience scripts (`run_backend.bat`, `run_frontend.bat`, `run_backend.sh`, `run_frontend.sh`) preserved.
