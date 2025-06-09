# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the OpsBeacon Python SDK - a client library for interacting with the OpsBeacon API. The SDK provides methods for executing commands on remote servers, managing connections, users, groups, files, and workspace commands.

## Development Commands

### Setup
```bash
# Copy and configure environment variables
cp .env.example .env
# Edit .env with OPSBEACON_API_DOMAIN and OPSBEACON_API_TOKEN

# Install in development mode (choose one):
pip install -e ".[cli]"    # Traditional approach with CLI extras
uv sync && uv pip install -e .    # UV package manager approach
```

### Testing
```bash
# Run the manual test script
python test_arguments.py

# Test CLI execution
python opsbeacon_execute.py --connection-ids <id> --command-path <path> --arguments '{"key": "value"}'
```

### Building and Publishing
```bash
# Build distribution packages
python -m build

# Upload to PyPI
twine upload dist/*
```

## Architecture

The SDK follows a simple client-server pattern:

- **`opsbeacon/opsbeacon.py`**: Contains the `OpsBeaconClient` class which implements all API interactions using the `requests` library
- **API Authentication**: Uses bearer token authentication via `OPSBEACON_API_TOKEN`
- **Error Handling**: Custom `OpsBeaconError` exception for API errors
- **Response Format**: All methods return parsed JSON responses from the API

### Key API Endpoints
- `/api/opsbeacon/cli/execute` - Execute commands on connections
- `/api/opsbeacon/cli/connections` - List available connections
- `/api/opsbeacon/cli/commands` - List available commands
- `/api/opsbeacon/cli/users/*` - User management
- `/api/opsbeacon/cli/groups/*` - Group management
- `/api/opsbeacon/cli/files/*` - File operations

## Important Notes

- **Version Inconsistency**: `setup.py` (v1.1.0, Python >=3.11) and `pyproject.toml` (v0.1.0, Python >=3.13) have different configurations. Verify which is authoritative before making changes.
- **No Automated Tests**: The project lacks a test suite. When adding features, consider creating proper unit tests.
- **Environment Variables**: The SDK requires `OPSBEACON_API_DOMAIN` and `OPSBEACON_API_TOKEN` to function.
- **CLI Tool**: `opsbeacon_execute.py` provides command-line access to the execute functionality.