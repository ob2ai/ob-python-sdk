"""
OpsBeacon SDK Exceptions.

This module defines the exception hierarchy for the OpsBeacon SDK.
All exceptions inherit from OpsBeaconError for easy catching.
"""

from typing import Any, Optional


class OpsBeaconError(Exception):
    """Base exception for all OpsBeacon SDK errors."""

    def __init__(self, message: str, *args: Any, **kwargs: Any) -> None:
        self.message = message
        super().__init__(message, *args, **kwargs)

    def __str__(self) -> str:
        return self.message


class AuthenticationError(OpsBeaconError):
    """Raised when authentication fails (invalid or expired token)."""

    def __init__(
        self,
        message: str = "Authentication failed. Check your API token.",
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, *args, **kwargs)


class APIError(OpsBeaconError):
    """Raised when the API returns an error response."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_body: Optional[str] = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self.status_code = status_code
        self.response_body = response_body
        super().__init__(message, *args, **kwargs)

    def __str__(self) -> str:
        parts = [self.message]
        if self.status_code:
            parts.append(f"(status: {self.status_code})")
        return " ".join(parts)


class ConnectionError(OpsBeaconError):
    """Raised when unable to connect to the OpsBeacon API."""

    def __init__(
        self,
        message: str = "Failed to connect to OpsBeacon API.",
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, *args, **kwargs)


class TimeoutError(OpsBeaconError):
    """Raised when an API request times out."""

    def __init__(
        self,
        message: str = "Request timed out.",
        timeout: Optional[float] = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self.timeout = timeout
        super().__init__(message, *args, **kwargs)


class ValidationError(OpsBeaconError):
    """Raised when input validation fails."""

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self.field = field
        super().__init__(message, *args, **kwargs)


class ResourceNotFoundError(OpsBeaconError):
    """Raised when a requested resource is not found."""

    def __init__(
        self,
        resource_type: str,
        resource_id: str,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self.resource_type = resource_type
        self.resource_id = resource_id
        message = f"{resource_type} '{resource_id}' not found"
        super().__init__(message, *args, **kwargs)


class RateLimitError(APIError):
    """Raised when API rate limit is exceeded."""

    def __init__(
        self,
        message: str = "Rate limit exceeded. Please retry later.",
        retry_after: Optional[int] = None,
    ) -> None:
        self.retry_after = retry_after
        super().__init__(message, status_code=429)


class CommandExecutionError(OpsBeaconError):
    """Raised when command execution fails."""

    def __init__(
        self,
        message: str,
        command: Optional[str] = None,
        connection: Optional[str] = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self.command = command
        self.connection = connection
        super().__init__(message, *args, **kwargs)


class FileOperationError(OpsBeaconError):
    """Raised when file operations fail."""

    def __init__(
        self,
        message: str,
        file_name: Optional[str] = None,
        operation: Optional[str] = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self.file_name = file_name
        self.operation = operation
        super().__init__(message, *args, **kwargs)


class MCPError(OpsBeaconError):
    """Raised when MCP protocol operations fail."""

    def __init__(
        self,
        message: str,
        trigger_name: Optional[str] = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self.trigger_name = trigger_name
        super().__init__(message, *args, **kwargs)
