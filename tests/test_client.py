"""
Unit tests for OpsBeaconClient.
"""

import pytest
import responses

from opsbeacon import OpsBeaconClient
from opsbeacon.exceptions import (
    APIError,
    AuthenticationError,
    ValidationError,
)


class TestClientInitialization:
    """Tests for client initialization."""

    def test_client_initialization(self, api_domain: str, api_token: str):
        """Test successful client initialization."""
        client = OpsBeaconClient(api_domain=api_domain, api_token=api_token)
        assert client.api_domain == api_domain
        assert client.base_url == f"https://{api_domain}"

    def test_client_initialization_strips_trailing_slash(self, api_token: str):
        """Test that trailing slash is stripped from domain."""
        client = OpsBeaconClient(
            api_domain="api.test.com/",
            api_token=api_token,
        )
        assert client.api_domain == "api.test.com"

    def test_client_initialization_missing_domain(self, api_token: str):
        """Test that missing domain raises ValidationError."""
        with pytest.raises(ValidationError, match="api_domain is required"):
            OpsBeaconClient(api_domain="", api_token=api_token)

    def test_client_initialization_missing_token(self, api_domain: str):
        """Test that missing token raises ValidationError."""
        with pytest.raises(ValidationError, match="api_token is required"):
            OpsBeaconClient(api_domain=api_domain, api_token="")

    def test_client_custom_timeout(self, api_domain: str, api_token: str):
        """Test client with custom timeout."""
        client = OpsBeaconClient(
            api_domain=api_domain,
            api_token=api_token,
            timeout=60.0,
        )
        assert client.timeout == 60.0

    def test_client_context_manager(self, api_domain: str, api_token: str):
        """Test client as context manager."""
        with OpsBeaconClient(api_domain=api_domain, api_token=api_token) as client:
            assert client is not None


class TestCommands:
    """Tests for commands API."""

    def test_commands_success(
        self, client: OpsBeaconClient, mock_responses, base_url: str, sample_commands: list
    ):
        """Test fetching commands successfully."""
        mock_responses.add(
            responses.GET,
            f"{base_url}/workspace/v2/commands",
            json={"commands": sample_commands},
            status=200,
        )

        commands = client.commands()
        assert len(commands) == 2
        assert commands[0]["name"] == "check-disk"

    def test_commands_empty(self, client: OpsBeaconClient, mock_responses, base_url: str):
        """Test fetching commands when none exist."""
        mock_responses.add(
            responses.GET,
            f"{base_url}/workspace/v2/commands",
            json={"commands": []},
            status=200,
        )

        commands = client.commands()
        assert commands == []


class TestConnections:
    """Tests for connections API."""

    def test_connections_success(
        self, client: OpsBeaconClient, mock_responses, base_url: str, sample_connections: list
    ):
        """Test fetching connections successfully."""
        mock_responses.add(
            responses.GET,
            f"{base_url}/workspace/v2/connections",
            json={"connections": sample_connections},
            status=200,
        )

        connections = client.connections()
        assert len(connections) == 2
        assert connections[0]["name"] == "prod-server"


class TestUsers:
    """Tests for users API."""

    def test_users_success(
        self, client: OpsBeaconClient, mock_responses, base_url: str, sample_users: list
    ):
        """Test fetching users successfully."""
        mock_responses.add(
            responses.GET,
            f"{base_url}/workspace/v2/users",
            json={"users": sample_users},
            status=200,
        )

        users = client.users()
        assert len(users) == 2
        assert users[0]["email"] == "admin@example.com"

    def test_add_user_success(self, client: OpsBeaconClient, mock_responses, base_url: str):
        """Test adding a user successfully."""
        new_user = {"email": "new@example.com", "role": "user"}
        mock_responses.add(
            responses.POST,
            f"{base_url}/workspace/v2/users",
            json={"id": "user-3", **new_user},
            status=201,
        )

        result = client.add_user(new_user)
        assert result["email"] == "new@example.com"

    def test_add_user_empty_data(self, client: OpsBeaconClient):
        """Test adding user with empty data raises error."""
        with pytest.raises(ValidationError, match="User data is required"):
            client.add_user({})

    def test_delete_user_success(self, client: OpsBeaconClient, mock_responses, base_url: str):
        """Test deleting a user successfully."""
        mock_responses.add(
            responses.DELETE,
            f"{base_url}/workspace/v2/users/user-1",
            status=204,
        )

        result = client.delete_user("user-1")
        assert result is True

    def test_delete_user_empty_id(self, client: OpsBeaconClient):
        """Test deleting user with empty ID raises error."""
        with pytest.raises(ValidationError, match="user_id is required"):
            client.delete_user("")


class TestGroups:
    """Tests for groups API."""

    def test_groups_success(
        self, client: OpsBeaconClient, mock_responses, base_url: str, sample_groups: list
    ):
        """Test fetching groups successfully."""
        mock_responses.add(
            responses.GET,
            f"{base_url}/workspace/v2/policy/group",
            json={"groups": sample_groups},
            status=200,
        )

        groups = client.groups()
        assert len(groups) == 2
        assert groups[0]["name"] == "developers"

    def test_add_group_success(self, client: OpsBeaconClient, mock_responses, base_url: str):
        """Test adding a group successfully."""
        new_group = {"name": "testers", "members": []}
        mock_responses.add(
            responses.POST,
            f"{base_url}/workspace/v2/policy/group",
            json=new_group,
            status=201,
        )

        result = client.add_group(new_group)
        assert result["name"] == "testers"

    def test_delete_group_success(self, client: OpsBeaconClient, mock_responses, base_url: str):
        """Test deleting a group successfully."""
        mock_responses.add(
            responses.DELETE,
            f"{base_url}/workspace/v2/policy/group/developers",
            status=204,
        )

        result = client.delete_group("developers")
        assert result is True


class TestCommandExecution:
    """Tests for command execution."""

    def test_run_with_command_text(self, client: OpsBeaconClient, mock_responses, base_url: str):
        """Test running command with command text."""
        mock_responses.add(
            responses.POST,
            f"{base_url}/trigger/v1/api",
            json={"success": True, "output": "Command executed"},
            status=200,
        )

        result = client.run(command_text="myserver: check-disk")
        assert result["success"] is True

    def test_run_with_structured_params(
        self, client: OpsBeaconClient, mock_responses, base_url: str
    ):
        """Test running command with structured parameters."""
        mock_responses.add(
            responses.POST,
            f"{base_url}/trigger/v1/api",
            json={"success": True, "output": "Command executed"},
            status=200,
        )

        result = client.run(
            connection="myserver",
            command="check-disk",
            args=["--verbose"],
        )
        assert result["success"] is True

    def test_run_with_string_args(self, client: OpsBeaconClient, mock_responses, base_url: str):
        """Test running command with string args."""
        mock_responses.add(
            responses.POST,
            f"{base_url}/trigger/v1/api",
            json={"success": True},
            status=200,
        )

        result = client.run(
            connection="myserver",
            command="check-disk",
            args="--verbose --path /var",
        )
        assert result["success"] is True

    def test_run_missing_params(self, client: OpsBeaconClient):
        """Test running command with missing params raises error."""
        with pytest.raises(ValidationError):
            client.run()

    def test_run_only_connection(self, client: OpsBeaconClient):
        """Test running command with only connection raises error."""
        with pytest.raises(ValidationError):
            client.run(connection="myserver")


class TestTriggers:
    """Tests for triggers API."""

    def test_triggers_success(
        self, client: OpsBeaconClient, mock_responses, base_url: str, sample_triggers: list
    ):
        """Test fetching triggers successfully."""
        mock_responses.add(
            responses.GET,
            f"{base_url}/workspace/v2/triggers",
            json={"triggers": sample_triggers},
            status=200,
        )

        triggers = client.triggers()
        assert len(triggers) == 2

    def test_triggers_filter_by_kind(
        self, client: OpsBeaconClient, mock_responses, base_url: str, sample_triggers: list
    ):
        """Test filtering triggers by kind."""
        mock_responses.add(
            responses.GET,
            f"{base_url}/workspace/v2/triggers",
            json={"triggers": sample_triggers},
            status=200,
        )

        triggers = client.triggers(kind="mcp")
        assert len(triggers) == 1
        assert triggers[0]["kind"] == "mcp"

    def test_mcp_triggers(
        self, client: OpsBeaconClient, mock_responses, base_url: str, sample_triggers: list
    ):
        """Test fetching MCP triggers."""
        mock_responses.add(
            responses.GET,
            f"{base_url}/workspace/v2/triggers",
            json={"triggers": sample_triggers},
            status=200,
        )

        triggers = client.mcp_triggers()
        assert len(triggers) == 1
        assert triggers[0]["name"] == "mcp-trigger-1"

    def test_get_trigger_success(
        self, client: OpsBeaconClient, mock_responses, base_url: str, sample_triggers: list
    ):
        """Test getting a specific trigger."""
        mock_responses.add(
            responses.GET,
            f"{base_url}/workspace/v2/triggers/mcp-trigger-1",
            json=sample_triggers[0],
            status=200,
        )

        trigger = client.get_trigger("mcp-trigger-1")
        assert trigger["name"] == "mcp-trigger-1"

    def test_delete_trigger_success(
        self, client: OpsBeaconClient, mock_responses, base_url: str
    ):
        """Test deleting a trigger."""
        mock_responses.add(
            responses.DELETE,
            f"{base_url}/workspace/v2/triggers/test-trigger",
            status=204,
        )

        result = client.delete_trigger("test-trigger")
        assert result is True


class TestPolicies:
    """Tests for policies API."""

    def test_policies_success(
        self, client: OpsBeaconClient, mock_responses, base_url: str, sample_policies: list
    ):
        """Test fetching policies successfully."""
        mock_responses.add(
            responses.GET,
            f"{base_url}/workspace/v2/policy",
            json={"policies": sample_policies},
            status=200,
        )

        policies = client.policies()
        assert len(policies) == 1
        assert policies[0]["name"] == "default-policy"

    def test_create_policy_success(
        self, client: OpsBeaconClient, mock_responses, base_url: str
    ):
        """Test creating a policy."""
        mock_responses.add(
            responses.POST,
            f"{base_url}/workspace/v2/policy",
            json={"name": "new-policy", "description": "Test policy"},
            status=201,
        )

        result = client.create_policy(
            name="new-policy",
            description="Test policy",
            commands=["check-disk"],
        )
        assert result["name"] == "new-policy"

    def test_delete_policy_success(
        self, client: OpsBeaconClient, mock_responses, base_url: str
    ):
        """Test deleting a policy."""
        mock_responses.add(
            responses.DELETE,
            f"{base_url}/workspace/v2/policy/test-policy",
            status=204,
        )

        result = client.delete_policy("test-policy")
        assert result is True


class TestErrorHandling:
    """Tests for error handling."""

    def test_authentication_error(
        self, client: OpsBeaconClient, mock_responses, base_url: str
    ):
        """Test handling of 401 authentication error."""
        mock_responses.add(
            responses.GET,
            f"{base_url}/workspace/v2/commands",
            json={"error": "Unauthorized"},
            status=401,
        )

        with pytest.raises(AuthenticationError):
            client.commands()

    def test_forbidden_error(
        self, client: OpsBeaconClient, mock_responses, base_url: str
    ):
        """Test handling of 403 forbidden error."""
        mock_responses.add(
            responses.GET,
            f"{base_url}/workspace/v2/commands",
            json={"error": "Forbidden"},
            status=403,
        )

        with pytest.raises(AuthenticationError, match="forbidden"):
            client.commands()

    def test_api_error(
        self, client: OpsBeaconClient, mock_responses, base_url: str
    ):
        """Test handling of generic API error."""
        mock_responses.add(
            responses.GET,
            f"{base_url}/workspace/v2/commands",
            json={"err": "Something went wrong"},
            status=500,
        )

        with pytest.raises(APIError):
            client.commands()

    def test_rate_limit_error(
        self, client: OpsBeaconClient, mock_responses, base_url: str
    ):
        """Test handling of rate limit error."""
        mock_responses.add(
            responses.GET,
            f"{base_url}/workspace/v2/commands",
            json={"error": "Rate limit exceeded"},
            status=429,
            headers={"Retry-After": "60"},
        )

        from opsbeacon.exceptions import RateLimitError

        with pytest.raises(RateLimitError) as exc_info:
            client.commands()
        assert exc_info.value.retry_after == 60
