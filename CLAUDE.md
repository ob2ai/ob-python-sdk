# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the OpsBeacon Python SDK - a client library for interacting with the OpsBeacon API. The SDK provides methods for executing commands on remote servers, managing connections, users, groups, files, triggers, policies, and MCP (Model Context Protocol) operations.

## Project Structure

```
ob-python-sdk/
├── opsbeacon/                    # Main package
│   ├── __init__.py              # Package exports and version
│   ├── client.py                # Main OpsBeaconClient class
│   ├── exceptions.py            # Exception hierarchy
│   └── py.typed                 # PEP 561 type marker
├── tests/                       # Test suite
│   ├── conftest.py              # Pytest fixtures
│   ├── test_client.py           # Client tests
│   └── test_exceptions.py       # Exception tests
├── examples/                    # Example scripts
├── .github/workflows/           # CI/CD pipelines
│   ├── ci.yml                   # Testing & linting
│   └── publish.yml              # PyPI publishing
├── pyproject.toml               # Project configuration
├── .pre-commit-config.yaml      # Pre-commit hooks
├── CHANGELOG.md                 # Version history
└── CONTRIBUTING.md              # Contribution guide
```

## Development Commands

### Setup
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install in development mode with all extras
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=opsbeacon --cov-report=html

# Run specific test
pytest tests/test_client.py::TestCommands -v
```

### Linting & Formatting
```bash
# Run Ruff linter
ruff check .

# Run Ruff formatter
ruff format .

# Run MyPy type checker
mypy opsbeacon

# Run all pre-commit hooks
pre-commit run --all-files
```

### Building & Publishing
```bash
# Build package
python -m build

# Check package
twine check dist/*

# Upload to PyPI (done via GitHub Actions on release)
```

## Architecture

The SDK follows a clean architecture with proper separation of concerns:

### Core Components

- **`opsbeacon/client.py`**: Main `OpsBeaconClient` class implementing all API interactions
  - Uses `requests.Session` for connection pooling
  - Proper logging with configurable debug mode
  - Context manager support for resource cleanup

- **`opsbeacon/exceptions.py`**: Comprehensive exception hierarchy
  - `OpsBeaconError` - Base exception
  - `AuthenticationError`, `APIError`, `ValidationError`, etc.
  - All exceptions include relevant context (status codes, resource IDs, etc.)

### API Endpoints

The SDK covers these main API endpoint groups:
- `/workspace/v2/commands` - Command management
- `/workspace/v2/connections` - Connection management
- `/workspace/v2/users` - User management
- `/workspace/v2/policy/group` - Group management
- `/workspace/v2/files` - File operations
- `/workspace/v2/triggers` - Trigger management (including MCP)
- `/workspace/v2/policy` - Policy management
- `/trigger/v1/api` - Command execution

## CI/CD

### GitHub Actions Workflows

1. **CI (`ci.yml`)**: Runs on push/PR to main
   - Linting with Ruff
   - Type checking with MyPy
   - Testing on Python 3.8-3.12
   - Coverage reporting

2. **Publish (`publish.yml`)**: Runs on GitHub release or manual trigger
   - Builds package
   - Publishes to PyPI (or TestPyPI for testing)
   - Requires `PYPI_API_TOKEN` secret

### Required GitHub Secrets

- `PYPI_API_TOKEN`: PyPI API token for publishing
- `TEST_PYPI_API_TOKEN`: TestPyPI token (optional, for testing)

## Version Management

Version is defined in three places (kept in sync via pre-commit hook):
1. `pyproject.toml` - `version = "X.Y.Z"`
2. `opsbeacon/__init__.py` - `__version__ = "X.Y.Z"`
3. `opsbeacon/client.py` - `SDK_VERSION = "X.Y.Z"`

## Environment Variables

- `OPSBEACON_API_DOMAIN` - API domain (e.g., `api.console.opsbeacon.com`)
- `OPSBEACON_API_TOKEN` - Bearer token for authentication

## Best Practices Applied

- Modern `pyproject.toml` packaging (PEP 517/518/621)
- Comprehensive type hints with `py.typed` marker
- Structured exception hierarchy
- Proper logging (no print statements)
- HTTP session reuse for performance
- Context manager support
- 80%+ test coverage target
- Pre-commit hooks for code quality
- Automated CI/CD with GitHub Actions
