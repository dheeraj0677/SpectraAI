# Third-Party Attribution & Dependencies

SpectraAI is built upon open-source software and services. We gratefully acknowledge the following projects, datasets, and libraries:

---

## 1. Machine Learning & API Services
- **[Anthropic Claude](https://www.anthropic.com/):** Used for multimodal visual document extraction and zero-shot VLM parsing (`claude-3-opus-20240229`). (Optional in runtime; fallback demo execution is fully offline and independent).

---

## 2. Backend Libraries
- **[FastAPI](https://fastapi.tiangolo.com/):** Modern, fast (high-performance) web framework for building APIs with Python (MIT License).
- **[Uvicorn](https://www.uvicorn.org/):** Lightning-fast ASGI server implementation (BSD-3-Clause License).
- **[Pydantic](https://docs.pydantic.dev/):** Data validation and settings management using Python type annotations (MIT License).
- **[PyPDF](https://pypdf.readthedocs.io/):** Pure-python PDF library capable of extracting document text and metadata (BSD-3-Clause License).
- **[NetworkX](https://networkx.org/):** Python package for the creation, manipulation, and study of the structure and dynamics of complex networks (BSD-3-Clause License).
- **[AIOFiles](https://github.com/Tinche/aiofiles):** Async file operations support (Apache-2.0 License).
- **[Pillow](https://python-pillow.org/):** Python Imaging Library fork (HPND License).
- **[ReportLab](https://www.reportlab.com/):** Open-source engine for creating PDF documents (BSD License).

---

## 3. Frontend Libraries
- **[React](https://react.dev/):** JavaScript library for building user interfaces (MIT License).
- **[Vite](https://vitejs.dev/):** Next-generation frontend tooling (MIT License).
- **[D3.js](https://d3js.org/):** JavaScript library for bespoke data visualization and force-directed graphs (ISC License).
- **[Lucide React](https://lucide.dev/):** Beautiful & consistent icon toolkit for React (ISC License).

---

## 4. Sample Fixtures & Data
- **Datasheet Fixtures:** All technical specifications, nameplate images, and CSV files in `test_data/` and fallback routines are synthetic demonstration fixtures created specifically for testing and educational purposes. No copyrighted proprietary industrial schemas or confidential vendor data are included.
- **Classification Standards:** UNSPSC and ETIM code taxonomies referenced in seed knowledge bases represent open classification standards for commercial categorization.
