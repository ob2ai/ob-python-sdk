"""
Pytest configuration and fixtures for OpsBeacon SDK tests.
"""

import pytest
import responses

from opsbeacon import OpsBeaconClient


@pytest.fixture
def api_domain() -> str:
    """Return test API domain."""
    return "api.test.opsbeacon.com"


@pytest.fixture
def api_token() -> str:
    """Return test API token."""
    return "test-api-token-12345"


@pytest.fixture
def client(api_domain: str, api_token: str) -> OpsBeaconClient:
    """Create a test OpsBeacon client."""
    return OpsBeaconClient(api_domain=api_domain, api_token=api_token)


@pytest.fixture
def base_url(api_domain: str) -> str:
    """Return the base URL for API requests."""
    return f"https://{api_domain}"


@pytest.fixture
def mock_responses():
    """
    Activate responses mock for HTTP requests.

    Usage:
        def test_something(mock_responses, base_url):
            mock_responses.add(
                responses.GET,
                f"{base_url}/workspace/v2/commands",
                json={"commands": []}
            )
    """
    with responses.RequestsMock() as rsps:
        yield rsps


# Sample data fixtures
@pytest.fixture
def sample_commands() -> list:
    """Return sample command data."""
    return [
        {
            "id": "cmd-1",
            "name": "check-disk",
            "description": "Check disk usage",
        },
        {
            "id": "cmd-2",
            "name": "restart-service",
            "description": "Restart a service",
        },
    ]


@pytest.fixture
def sample_connections() -> list:
    """Return sample connection data."""
    return [
        {
            "id": "conn-1",
            "name": "prod-server",
            "type": "ssh",
        },
        {
            "id": "conn-2",
            "name": "staging-server",
            "type": "ssh",
        },
    ]


@pytest.fixture
def sample_users() -> list:
    """Return sample user data."""
    return [
        {
            "id": "user-1",
            "email": "admin@example.com",
            "role": "admin",
        },
        {
            "id": "user-2",
            "email": "dev@example.com",
            "role": "user",
        },
    ]


@pytest.fixture
def sample_groups() -> list:
    """Return sample group data."""
    return [
        {
            "name": "developers",
            "members": ["user-1", "user-2"],
        },
        {
            "name": "admins",
            "members": ["user-1"],
        },
    ]


@pytest.fixture
def sample_triggers() -> list:
    """Return sample trigger data."""
    return [
        {
            "name": "mcp-trigger-1",
            "kind": "mcp",
            "description": "MCP trigger for testing",
            "triggerUrl": "https://mcp.opsbeacon.com/trigger/abc123",
            "mcpTriggerInfo": {
                "toolInstances": [
                    {
                        "instanceId": "tool-1",
                        "templateId": "tool-1",
                        "overrides": {
                            "name": "check-disk-tool",
                            "description": "Check disk space",
                            "connection": "prod-server",
                            "command": "check-disk",
                        },
                    }
                ]
            },
        },
        {
            "name": "webhook-trigger-1",
            "kind": "webHook",
            "description": "Webhook trigger",
        },
    ]


@pytest.fixture
def sample_policies() -> list:
    """Return sample policy data."""
    return [
        {
            "name": "default-policy",
            "description": "Default execution policy",
            "commands": ["check-disk"],
            "connections": ["prod-server"],
        },
    ]
