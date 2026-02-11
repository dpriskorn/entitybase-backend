---
name: python-venv
description: "Before running Python scripts or installing packages, check for existing virtual environments and reuse them if found. If no virtual environment exists, ask the user to choose: (1) Create new venv in current directory (recommended), (2) Use system Python directly, or (3) Create venv at custom path. This applies to: running .py files, using pip/uv pip install, or any task requiring third-party packages. Exceptions: simple one-liners using only Python standard library."
---

# Python Virtual Environment Requirement

## Core Rule

**Check for existing virtual environments and reuse them. If none exists, ask user to choose: create new venv, use custom path, or use system Python directly.**

## When Virtual Environment is REQUIRED

| Scenario | Required? | Reason |
|----------|-----------|--------|
| `pip install` / `uv pip install` | ✅ YES | Installing packages |
| Running `.py` files with third-party imports | ✅ YES | Needs dependencies |
| `python script.py` with `requirements.txt` | ✅ YES | Project dependencies |
| Multi-file Python projects | ✅ YES | Isolation needed |

## When Virtual Environment is NOT Required

| Scenario | Example |
|----------|---------|
| Simple stdlib one-liner | `python3 -c "print('hello')"` |
| Built-in modules only | `python3 -c "import json; ..."` |
| Version check | `python3 --version` |

**Standard library modules**: os, sys, json, re, math, datetime, pathlib, subprocess, collections, itertools, functools, argparse, logging, urllib, http, socket, threading, multiprocessing, etc.

## Workflow (When venv IS Required)

```
1. Check for existing virtual environment (.venv, venv, env, .env) → If YES, activate and reuse it
2. If NOT exists → Ask user to choose:
   - **Create new venv** (recommended): Create .venv in current directory with uv or python3 -m venv
   - **Use system Python**: Skip venv, use system Python directly
   - **Custom path**: Specify custom path for virtual environment
3. Based on user choice: Create/skip/create-at-path virtual-environment
4. Activate (if venv was created), then proceed with Python commands
```

## Detecting Existing Virtual Environment

Check in this order (first match wins): `.venv/` → `venv/` → `env/` → `.env/`

Also check conda: `conda info --envs` or check if `CONDA_PREFIX` is set.

**Priority: Always reuse existing virtual environment to preserve installed packages.**

## Workflow Checklist

Before Python operations requiring venv:

1. [ ] Check for existing virtual environment: `.venv/`, `venv/`, `env/`, `.env/`
2. [ ] Check for conda: `conda info --envs` or `CONDA_PREFIX`
3. [ ] If exists → Reuse it (activate)
4. [ ] If not exists → Ask user: Create new (.venv)? Use system Python? Custom path?
5. [ ] Based on choice: Create / Skip / Create at path
6. [ ] Activate (if venv created), proceed

## Project Type Detection

| File Present | Install Command |
|--------------|-----------------|
| `requirements.txt` | `pip install -r requirements.txt` |
| `pyproject.toml` | `pip install -e .` or `uv pip install -e .` |
| `pyproject.toml` + `poetry.lock` | `poetry install` |
| `pyproject.toml` + `uv.lock` | `uv sync` |
| `setup.py` | `pip install -e .` |
| `Pipfile` | `pipenv install` |
| `environment.yml` | `conda env create -f environment.yml` |

## Quick Reference

| Task | Linux/macOS | Windows |
|------|-------------|---------|
| Create venv (uv) | `uv venv` | `uv venv` |
| Create venv (standard) | `python3 -m venv .venv` | `python -m venv .venv` |
| Activate | `source .venv/bin/activate` | `.venv\Scripts\activate` |
| Install package (uv) | `uv pip install <pkg>` | `uv pip install <pkg>` |
| Install package (pip) | `pip install <pkg>` | `pip install <pkg>` |
| Deactivate | `deactivate` | `deactivate` |
| Conda activate | `conda activate <env>` | `conda activate <env>` |

**For custom paths**: Replace `.venv` with your path in create/activate commands.

**For system Python**: Skip venv, use `python3`/`python` directly.

## Detailed Patterns

For common patterns, scripts, and platform-specific commands, see [patterns.md](references/patterns.md).

## Troubleshooting

For troubleshooting guidance, see [troubleshooting.md](references/troubleshooting.md).
