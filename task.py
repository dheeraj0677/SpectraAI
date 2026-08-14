#!/usr/bin/env python3
"""
SpectraAI Cross-Platform Task Runner
Provides native task execution without requiring GNU Make or container runtimes.

Usage:
    python task.py setup
    python task.py setup-backend
    python task.py setup-frontend
    python task.py run-backend
    python task.py run-frontend
    python task.py test
    python task.py build
    python task.py reset-demo
    python task.py clean
"""

import os
import sys
import io
import shutil
import subprocess
from pathlib import Path

# Ensure UTF-8 stdout encoding across all platforms
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

ROOT_DIR = Path(__file__).parent.resolve()
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend"

def run_cmd(cmd, cwd=ROOT_DIR):
    """Run a shell command and exit if it fails."""
    cmd_str = ' '.join(cmd) if isinstance(cmd, list) else cmd
    print(f"\n[SpectraAI Task] Running: {cmd_str}")
    use_shell = isinstance(cmd, str) or sys.platform == "win32"
    res = subprocess.run(cmd, cwd=str(cwd), shell=use_shell)
    if res.returncode != 0:
        print(f"[SpectraAI Task] Error: Command exited with code {res.returncode}")
        sys.exit(res.returncode)

def is_tool_available(name):
    return shutil.which(name) is not None

def setup_backend():
    """Set up Python environment using uv or standard venv."""
    print("[SpectraAI Task] Setting up backend environment...")
    req_file = BACKEND_DIR / "requirements.txt"
    lock_file = BACKEND_DIR / "requirements.lock"

    if is_tool_available("uv"):
        print("[SpectraAI Task] Found 'uv'! Using fast uv package installer...")
        if lock_file.exists():
            run_cmd(["uv", "pip", "install", "-r", str(lock_file)])
        else:
            run_cmd(["uv", "pip", "install", "-r", str(req_file)])
    else:
        print("[SpectraAI Task] 'uv' not found on PATH. Using standard pip...")
        run_cmd([sys.executable, "-m", "pip", "install", "-r", str(req_file)])

def setup_frontend():
    """Install frontend dependencies using npm."""
    print("[SpectraAI Task] Setting up frontend dependencies via npm...")
    run_cmd(["npm", "install"], cwd=FRONTEND_DIR)

def setup():
    """Install both backend and frontend dependencies."""
    setup_backend()
    setup_frontend()
    print("\n✅ SpectraAI setup complete!")

def run_backend():
    """Start FastAPI backend server."""
    print("[SpectraAI Task] Starting FastAPI backend on http://localhost:8000...")
    run_cmd([sys.executable, "main.py"], cwd=BACKEND_DIR)

def run_frontend():
    """Start Vite frontend dev server."""
    print("[SpectraAI Task] Starting Vite dev server on http://localhost:5173...")
    run_cmd(["npm", "run", "dev"], cwd=FRONTEND_DIR)

def run_tests():
    """Run Pytest suite, E2E runner, and Frontend smoke tests."""
    print("[SpectraAI Task] Running full test verification suite...\n")
    print("--- 1. Backend Pytest Suite ---")
    run_cmd([sys.executable, "-m", "pytest", "-v"])

    print("\n--- 2. Compatibility E2E Suite ---")
    run_cmd([sys.executable, "test_e2e.py"])

    print("\n--- 3. Frontend Smoke Suite ---")
    run_cmd(["npm", "test"], cwd=FRONTEND_DIR)
    print("\n✅ All test suites passed successfully!")

def build_frontend():
    """Build production frontend bundle."""
    print("[SpectraAI Task] Building frontend bundle...")
    run_cmd(["npm", "run", "build"], cwd=FRONTEND_DIR)
    print("\n✅ Frontend build successful!")

def reset_demo():
    """Reset SQLite database and uploads directory to pristine demo state."""
    print("[SpectraAI Task] Resetting local demo database and uploads...")
    db_file = BACKEND_DIR / "product_intelligence.db"
    if db_file.exists():
        db_file.unlink()
        print(f"  Removed: {db_file}")

    uploads_dir = BACKEND_DIR / "uploads"
    if uploads_dir.exists():
        for item in uploads_dir.iterdir():
            if item.name != ".gitkeep":
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
                print(f"  Removed: {item.name}")

    print("✅ Demo environment reset to clean state.")

def clean():
    """Remove cache directories, build artifacts, and test reports."""
    print("[SpectraAI Task] Cleaning temporary caches and build artifacts...")
    patterns = [
        "**/__pycache__",
        "**/.pytest_cache",
        "frontend/dist",
        ".coverage"
    ]
    for pattern in patterns:
        for p in ROOT_DIR.glob(pattern):
            if p.is_dir():
                shutil.rmtree(p, ignore_errors=True)
                print(f"  Removed directory: {p.relative_to(ROOT_DIR)}")
            elif p.is_file():
                p.unlink(missing_ok=True)
                print(f"  Removed file: {p.relative_to(ROOT_DIR)}")
    print("✅ Workspace cleaned.")

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    task = sys.argv[1].lower()
    tasks = {
        "setup": setup,
        "setup-backend": setup_backend,
        "setup-frontend": setup_frontend,
        "run-backend": run_backend,
        "run-frontend": run_frontend,
        "test": run_tests,
        "build": build_frontend,
        "reset-demo": reset_demo,
        "clean": clean
    }

    if task in tasks:
        tasks[task]()
    else:
        print(f"Unknown task '{task}'. Available tasks: {', '.join(tasks.keys())}")
        sys.exit(1)

if __name__ == "__main__":
    main()
