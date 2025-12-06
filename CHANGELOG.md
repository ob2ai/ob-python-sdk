# Changelog

All notable changes to the OpsBeacon Python SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.3.0] - 2024-12-06

### Added
- Comprehensive exception hierarchy for better error handling
  - `OpsBeaconError` - Base exception
  - `AuthenticationError` - Authentication failures
  - `APIError` - API error responses
  - `ConnectionError` - Network connection issues
  - `TimeoutError` - Request timeouts
  - `ValidationError` - Input validation errors
  - `ResourceNotFoundError` - Resource not found (404)
  - `RateLimitError` - Rate limit exceeded (429)
  - `CommandExecutionError` - Command execution failures
  - `FileOperationError` - File operation failures
  - `MCPError` - MCP protocol errors
- Type hints throughout the codebase
- `py.typed` marker for PEP 561 compliance
- Proper logging support with configurable debug mode
- Context manager support for `OpsBeaconClient`
- HTTP session reuse for better performance
- Comprehensive test suite with pytest
- GitHub Actions CI/CD pipeline
  - Automated testing on Python 3.8-3.12
  - Linting with Ruff
  - Type checking with MyPy
  - Automated PyPI publishing on release
- Pre-commit hooks configuration
- Modern `pyproject.toml` packaging (PEP 517/518/621)

### Changed
- Migrated from `setup.py` to `pyproject.toml`
- Replaced print statements with proper logging
- Improved error handling with specific exception types
- Better API response handling
- Session-based HTTP requests for connection pooling

### Fixed
- Sensitive data (API tokens) no longer logged in debug mode
- Proper cleanup of resources with context manager

## [1.2.2] - 2024-11-XX

### Changed
- Lowered Python requirement to >=3.8

## [1.2.1] - 2024-11-XX

### Added
- Array argument support for command execution
- Improved MCP protocol support

## [1.2.0] - 2024-11-XX

### Added
- MCP (Model Context Protocol) trigger support
- Policy management APIs
- Enhanced documentation

## [1.1.0] - 2024-10-XX

### Added
- File upload and download support
- User and group management
- Connection management

## [1.0.0] - 2024-09-XX

### Added
- Initial release
- Basic command execution
- Connection listing
- Command listing

[Unreleased]: https://github.com/ob2ai/ob-python-sdk/compare/v1.3.0...HEAD
[1.3.0]: https://github.com/ob2ai/ob-python-sdk/compare/v1.2.2...v1.3.0
[1.2.2]: https://github.com/ob2ai/ob-python-sdk/compare/v1.2.1...v1.2.2
[1.2.1]: https://github.com/ob2ai/ob-python-sdk/compare/v1.2.0...v1.2.1
[1.2.0]: https://github.com/ob2ai/ob-python-sdk/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/ob2ai/ob-python-sdk/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/ob2ai/ob-python-sdk/releases/tag/v1.0.0
