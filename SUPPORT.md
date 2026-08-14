# Getting Support for SpectraAI

Thank you for using SpectraAI! Here is how to get help, find documentation, or report issues.

---

## 1. Documentation & Architecture Reference
Before opening an issue, check the bundled architectural documentation:
- **Quickstart Guide:** [`README.md`](file:///c:/Users/viswa/Desktop/SpectraAI/README.md)
- **Contributor Setup:** [`CONTRIBUTING.md`](file:///c:/Users/viswa/Desktop/SpectraAI/CONTRIBUTING.md)
- **REST API Contract:** [`docs/api-contract.md`](file:///c:/Users/viswa/Desktop/SpectraAI/docs/api-contract.md)
- **Architecture Overview:** [`docs/architecture-current.md`](file:///c:/Users/viswa/Desktop/SpectraAI/docs/architecture-current.md)
- **Future Roadmap:** [`docs/roadmap.md`](file:///c:/Users/viswa/Desktop/SpectraAI/docs/roadmap.md)

---

## 2. Asking Questions & Discussions
For general questions, design discussions, ideas, or usage help:
- Use **[GitHub Discussions](https://github.com/dheeraj0677/SpectraAI/discussions)** to connect with the community.
- For architectural proposals or benchmark suggestions, open a Research/Benchmark issue template.

---

## 3. Reporting Bugs & Feature Requests
- **Bugs:** If you encounter unexpected behavior or failed tests, check existing issues and open a **[Bug Report](https://github.com/dheeraj0677/SpectraAI/issues/new?template=bug_report.yml)** with logs and reproduction steps.
- **Features:** To propose additions to the pipeline, UI, or normalization engine, open a **[Feature Request](https://github.com/dheeraj0677/SpectraAI/issues/new?template=feature_request.yml)**.
- **Security Vulnerabilities:** Follow [`SECURITY.md`](file:///c:/Users/viswa/Desktop/SpectraAI/SECURITY.md) for private reporting.

---

## 4. Common Troubleshooting FAQ

| Problem | Cause | Solution |
|---|---|---|
| `ANTHROPIC_API_KEY is not set` | No API key in `.env` | SpectraAI will automatically fall back to the deterministic offline extraction demo. Set `ANTHROPIC_API_KEY` in `.env` only if live Claude VLM inference is desired. |
| `Port 8000 already in use` | Another backend process running | Terminate old Python process or start on a different port: `python -m uvicorn backend.main:app --port 8001`. |
| `CORS Error in Browser` | Frontend port mismatch | Configure `CORS_ORIGINS=["http://localhost:5173", ...]` in `.env`. |
| `SQLite database locked` | Concurrent process hold | Reset demo database by removing `backend/product_intelligence.db`. It will recreate cleanly on next startup. |
