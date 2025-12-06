"""
Unit tests for OpsBeacon exceptions.
"""


from opsbeacon.exceptions import (
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


class TestOpsBeaconError:
    """Tests for base OpsBeaconError."""

    def test_basic_exception(self):
        """Test basic exception creation."""
        error = OpsBeaconError("Test error")
        assert str(error) == "Test error"
        assert error.message == "Test error"

    def test_exception_inheritance(self):
        """Test that OpsBeaconError inherits from Exception."""
        error = OpsBeaconError("Test")
        assert isinstance(error, Exception)


class TestAuthenticationError:
    """Tests for AuthenticationError."""

    def test_default_message(self):
        """Test default error message."""
        error = AuthenticationError()
        assert "Authentication failed" in str(error)

    def test_custom_message(self):
        """Test custom error message."""
        error = AuthenticationError("Token expired")
        assert str(error) == "Token expired"

    def test_inheritance(self):
        """Test exception inheritance."""
        error = AuthenticationError()
        assert isinstance(error, OpsBeaconError)


class TestAPIError:
    """Tests for APIError."""

    def test_basic_error(self):
        """Test basic API error."""
        error = APIError("API failed")
        assert str(error) == "API failed"

    def test_with_status_code(self):
        """Test API error with status code."""
        error = APIError("Not found", status_code=404)
        assert error.status_code == 404
        assert "404" in str(error)

    def test_with_response_body(self):
        """Test API error with response body."""
        error = APIError("Error", status_code=500, response_body='{"err": "Server error"}')
        assert error.response_body == '{"err": "Server error"}'


class TestConnectionError:
    """Tests for ConnectionError."""

    def test_default_message(self):
        """Test default error message."""
        error = ConnectionError()
        assert "Failed to connect" in str(error)

    def test_inheritance(self):
        """Test exception inheritance."""
        error = ConnectionError()
        assert isinstance(error, OpsBeaconError)


class TestTimeoutError:
    """Tests for TimeoutError."""

    def test_default_message(self):
        """Test default error message."""
        error = TimeoutError()
        assert "timed out" in str(error)

    def test_with_timeout_value(self):
        """Test timeout error with value."""
        error = TimeoutError(timeout=30.0)
        assert error.timeout == 30.0


class TestValidationError:
    """Tests for ValidationError."""

    def test_basic_error(self):
        """Test basic validation error."""
        error = ValidationError("Invalid input")
        assert str(error) == "Invalid input"

    def test_with_field(self):
        """Test validation error with field."""
        error = ValidationError("Required field", field="email")
        assert error.field == "email"


class TestResourceNotFoundError:
    """Tests for ResourceNotFoundError."""

    def test_error_message(self):
        """Test error message format."""
        error = ResourceNotFoundError("User", "user-123")
        assert "User" in str(error)
        assert "user-123" in str(error)
        assert "not found" in str(error)

    def test_attributes(self):
        """Test error attributes."""
        error = ResourceNotFoundError("Command", "check-disk")
        assert error.resource_type == "Command"
        assert error.resource_id == "check-disk"


class TestRateLimitError:
    """Tests for RateLimitError."""

    def test_default_message(self):
        """Test default error message."""
        error = RateLimitError()
        assert "Rate limit" in str(error)

    def test_with_retry_after(self):
        """Test rate limit error with retry-after."""
        error = RateLimitError(retry_after=60)
        assert error.retry_after == 60

    def test_inherits_from_api_error(self):
        """Test that RateLimitError inherits from APIError."""
        error = RateLimitError()
        assert isinstance(error, APIError)
        assert error.status_code == 429


class TestCommandExecutionError:
    """Tests for CommandExecutionError."""

    def test_basic_error(self):
        """Test basic command execution error."""
        error = CommandExecutionError("Command failed")
        assert str(error) == "Command failed"

    def test_with_command_info(self):
        """Test error with command information."""
        error = CommandExecutionError(
            "Execution failed",
            command="check-disk",
            connection="prod-server",
        )
        assert error.command == "check-disk"
        assert error.connection == "prod-server"


class TestFileOperationError:
    """Tests for FileOperationError."""

    def test_basic_error(self):
        """Test basic file operation error."""
        error = FileOperationError("Upload failed")
        assert str(error) == "Upload failed"

    def test_with_file_info(self):
        """Test error with file information."""
        error = FileOperationError(
            "Download failed",
            file_name="data.csv",
            operation="download",
        )
        assert error.file_name == "data.csv"
        assert error.operation == "download"


class TestMCPError:
    """Tests for MCPError."""

    def test_basic_error(self):
        """Test basic MCP error."""
        error = MCPError("MCP operation failed")
        assert str(error) == "MCP operation failed"

    def test_with_trigger_name(self):
        """Test error with trigger name."""
        error = MCPError("Creation failed", trigger_name="my-trigger")
        assert error.trigger_name == "my-trigger"


class TestExceptionHierarchy:
    """Tests for exception hierarchy."""

    def test_all_inherit_from_base(self):
        """Test all exceptions inherit from OpsBeaconError."""
        exceptions = [
            AuthenticationError(),
            APIError("test"),
            ConnectionError(),
            TimeoutError(),
            ValidationError("test"),
            ResourceNotFoundError("Type", "id"),
            RateLimitError(),
            CommandExecutionError("test"),
            FileOperationError("test"),
            MCPError("test"),
        ]

        for exc in exceptions:
            assert isinstance(exc, OpsBeaconError), f"{type(exc).__name__} should inherit from OpsBeaconError"

    def test_catch_all_with_base(self):
        """Test catching all exceptions with base class."""
        try:
            raise ValidationError("test error")
        except OpsBeaconError as e:
            assert "test error" in str(e)
