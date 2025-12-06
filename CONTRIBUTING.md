# Contributing to OpsBeacon Python SDK

Thank you for your interest in contributing to the OpsBeacon Python SDK! This document provides guidelines and instructions for contributing.

## Development Setup

### Prerequisites

- Python 3.8 or higher
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

### Setting Up the Development Environment

1. Clone the repository:
   ```bash
   git clone https://github.com/ob2ai/ob-python-sdk.git
   cd ob-python-sdk
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

4. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

## Development Workflow

### Code Style

We use [Ruff](https://docs.astral.sh/ruff/) for linting and formatting. The configuration is in `pyproject.toml`.

- Run linting: `ruff check .`
- Run formatting: `ruff format .`
- Auto-fix issues: `ruff check --fix .`

### Type Checking

We use [MyPy](https://mypy.readthedocs.io/) for static type checking:

```bash
mypy opsbeacon
```

### Running Tests

We use [pytest](https://pytest.org/) for testing:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=opsbeacon --cov-report=html

# Run specific test file
pytest tests/test_client.py

# Run specific test
pytest tests/test_client.py::TestCommands::test_commands_success
```

### Pre-commit Hooks

Pre-commit hooks run automatically on `git commit`. To run them manually:

```bash
pre-commit run --all-files
```

## Making Changes

### Branching Strategy

1. Create a new branch from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and commit:
   ```bash
   git add .
   git commit -m "Add: description of your changes"
   ```

3. Push your branch:
   ```bash
   git push -u origin feature/your-feature-name
   ```

4. Open a Pull Request on GitHub.

### Commit Message Guidelines

We follow conventional commit messages:

- `Add:` New features
- `Fix:` Bug fixes
- `Update:` Updates to existing features
- `Remove:` Removed features
- `Refactor:` Code refactoring
- `Docs:` Documentation changes
- `Test:` Test additions or changes
- `Chore:` Maintenance tasks

### Pull Request Guidelines

1. Update the CHANGELOG.md with your changes
2. Ensure all tests pass
3. Ensure linting and type checking pass
4. Update documentation if needed
5. Request review from maintainers

## Adding New Features

### Adding a New API Method

1. Add the method to `opsbeacon/client.py`
2. Add appropriate type hints
3. Add docstring with Google-style documentation
4. Add proper error handling using exceptions from `opsbeacon/exceptions.py`
5. Add unit tests in `tests/test_client.py`
6. Update CHANGELOG.md

### Adding a New Exception

1. Add the exception class to `opsbeacon/exceptions.py`
2. Export it in `opsbeacon/__init__.py`
3. Add tests in `tests/test_exceptions.py`

## Testing Guidelines

### Writing Tests

- Use descriptive test names: `test_<method>_<scenario>`
- Use fixtures from `conftest.py`
- Mock HTTP requests with `responses` library
- Test both success and error cases

Example:
```python
def test_commands_success(
    self, client: OpsBeaconClient, mock_responses, base_url: str
):
    """Test fetching commands successfully."""
    mock_responses.add(
        responses.GET,
        f"{base_url}/workspace/v2/commands",
        json={"commands": [{"name": "test"}]},
        status=200,
    )

    commands = client.commands()
    assert len(commands) == 1
```

### Test Coverage

We aim for 80%+ code coverage. Check coverage with:

```bash
pytest --cov=opsbeacon --cov-report=term-missing
```

## Documentation

### Docstrings

Use Google-style docstrings:

```python
def method_name(self, param1: str, param2: int = 10) -> dict[str, Any]:
    """
    Short description of the method.

    Longer description if needed.

    Args:
        param1: Description of param1.
        param2: Description of param2.

    Returns:
        Description of return value.

    Raises:
        ValidationError: If validation fails.
        APIError: If API request fails.

    Example:
        >>> result = client.method_name("value", param2=20)
    """
```

## Releasing

Releases are handled by maintainers:

1. Update version in:
   - `pyproject.toml`
   - `opsbeacon/__init__.py`
   - `opsbeacon/client.py`

2. Update CHANGELOG.md

3. Create a GitHub release with tag `vX.Y.Z`

4. GitHub Actions will automatically publish to PyPI

## Getting Help

- Open an issue for bugs or feature requests
- Discussions for questions and ideas

Thank you for contributing!
