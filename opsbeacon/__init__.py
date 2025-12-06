"""
OpsBeacon Python SDK.

A client library for interacting with the OpsBeacon API.

Example:
    >>> from opsbeacon import OpsBeaconClient
    >>> client = OpsBeaconClient(
    ...     api_domain="api.console.opsbeacon.com",
    ...     api_token="your-api-token"
    ... )
    >>> commands = client.commands()
"""

from .client import OpsBeaconClient
from .exceptions import (
    APIError,
    AuthenticationError,
    CommandExecutionError,
    ConnectionError,
    FileOperationError,
    MCPError,
    OpsBeaconError,
    RateLimitError,
    ResourceNotFoundError,
    TimeoutError,
    ValidationError,
)

__version__ = "1.3.0"

__all__ = [
    "APIError",
    "AuthenticationError",
    "CommandExecutionError",
    "ConnectionError",
    "FileOperationError",
    "MCPError",
    "OpsBeaconClient",
    "OpsBeaconError",
    "RateLimitError",
    "ResourceNotFoundError",
    "TimeoutError",
    "ValidationError",
    "__version__",
]
