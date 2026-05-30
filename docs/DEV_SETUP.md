# Development Setup Guide — Project Autopilot

## Prerequisites

- Python 3.11+ (recommended: 3.12)
- Git
- Cursor IDE (primary) or VS Code
- pip + venv (no poetry/pipenv for now — keep it simple)

---

## 1. Initial setup

```bash
# Clone
git clone https://github.com/manupesqueira-ship-it/project-autopilot.git
cd project-autopilot

# Virtual environment
python -m venv .venv

# Activate (Git Bash on Windows)
source .venv/Scripts/activate

# Or on Linux/Mac:
# source .venv/bin/activate

# Install agent dependencies
pip install -r agents/source_monitor/requirements.txt
```

## 2. Environment variables

Copy `.env.example` to `.env` and fill in:

```bash
cp .env.example .env
```

Required for Source Monitor:
```
INOREADER_APP_ID=your_app_id
INOREADER_APP_KEY=your_app_key
INOREADER_TOKEN=your_oauth_token
```

Optional:
```
ANTHROPIC_API_KEY=sk-...    # For Signal Scorer (not Source Monitor)
LOG_LEVEL=INFO
```

**Never commit `.env` — it's in `.gitignore`.**

---

## 3. Cursor IDE setup

### Recommended extensions
- **Python** (Microsoft) — linting, debugging, IntelliSense
- **Pylance** — type checking
- **YAML** — syntax for config files
- **GitLens** — blame, history

### Workspace settings (`.vscode/settings.json`)
```json
{
  "python.defaultInterpreterPath": ".venv/Scripts/python",
  "python.analysis.typeCheckingMode": "basic",
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["agents/", "core/"],
  "editor.formatOnSave": true,
  "editor.rulers": [100],
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true,
    ".venv": true,
    "evidence": true
  }
}
```

### .cursorrules
The repo already has `.cursorrules` at root. It tells Cursor's AI about the project structure, conventions, and architecture. Keep it up to date.

---

## 4. Running tests

```bash
# All tests
pytest agents/ -v

# Source Monitor tests only
pytest agents/source_monitor/tests/ -v

# Specific test class
pytest agents/source_monitor/tests/test_agent.py::TestT1FetchRSS -v

# With coverage
pip install pytest-cov
pytest agents/source_monitor/tests/ --cov=agents/source_monitor --cov-report=term-missing
```

### Test conventions
- Tests live in `agents/<agent>/tests/`
- Test files: `test_*.py`
- Fixtures: in the test file or in `conftest.py`
- Mock external calls (HTTP, APIs) — never hit real endpoints in tests
- Use `tmp_path` fixture for file I/O tests

---

## 5. Debugging an agent

### From CLI
```bash
# Run with verbose logging
LOG_LEVEL=DEBUG python -m agents.source_monitor.cli --property dinero-ia

# Or via the autopilot command (when wired up)
autopilot scan --property dinero-ia --verbose
```

### From Cursor debugger
1. Open `agents/source_monitor/agent.py`
2. Set breakpoint on `run()` method
3. Create a launch config in `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Debug Source Monitor",
      "type": "debugpy",
      "request": "launch",
      "module": "agents.source_monitor.cli",
      "args": ["--property", "dinero-ia"],
      "cwd": "${workspaceFolder}",
      "env": {"LOG_LEVEL": "DEBUG"},
      "justMyCode": false
    }
  ]
}
```

4. Press F5 to start debugging

### Inspecting output
After a run, check:
```bash
# Output JSON
cat evidence/<run_id>/source_monitor_output.json | python -m json.tool

# Stats
cat evidence/<run_id>/source_monitor_stats.json

# Dedup history
cat data/source_monitor/seen_items.json | python -m json.tool | head -20
```

---

## 6. Code conventions

### Python style
- **Type hints everywhere** — all function signatures, class attributes
- **Pydantic for data** — all data structures that cross boundaries use Pydantic models
- **Docstrings** — Google style, on all public methods
- **No magic numbers** — constants in config.yaml or as class-level constants
- **Imports** — stdlib, then third-party, then local. Use `from __future__ import annotations`

### Naming
- Files: `snake_case.py`
- Classes: `PascalCase`
- Functions/methods: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Private methods: `_prefixed`

### Error handling
- Agents must be resilient — catch exceptions per-source, not globally
- Log errors, don't swallow them
- Return errors as data (`SourceError`), not exceptions
- Only raise exceptions for truly unrecoverable situations (missing config, etc.)

### Config
- Agent-level config: `agents/<agent>/config.yaml`
- Property-level config: `projects/<property>/*.yaml`
- Secrets: `.env` (never in YAML/code)
- Runtime overrides: CLI flags

---

## 7. Git workflow

### Branch naming
```
feature/<agent>-<milestone>    # feature/source-monitor-m2
fix/<agent>-<description>      # fix/source-monitor-dedup-crash
```

### Commit messages
```
<verb> <what> (<scope>)

<optional body explaining why>
```

Examples:
```
Implement RSS fetching (source_monitor)
Fix dedup history pruning (source_monitor)
Add keyword scoring (source_monitor/scorer)
```

### Workflow
1. Work on `main` for now (solo developer, no PRs needed yet)
2. Commit after each milestone completion
3. Push to GitHub regularly
4. If experimenting with something risky, branch first

### What NOT to commit
- `.env` (secrets)
- `evidence/` (run outputs — gitignored)
- `data/` (dedup history — gitignored)
- `__pycache__/`
- `.venv/`

---

## 8. Adding a new agent

When starting a new agent (e.g., Signal Scorer):

1. Copy the `source_monitor/` structure as a template
2. Create: `__init__.py`, `agent.py`, `schemas.py`, `config.yaml`, `requirements.txt`, `tests/`, `DESIGN.md`
3. Define schemas first (inputs/outputs)
4. Write acceptance tests stubs
5. Implement incrementally per milestones
6. Update `agents/README.md` checklist
