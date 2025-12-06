"""
OpsBeacon API Client.

This module provides the main client for interacting with the OpsBeacon API.
"""

from __future__ import annotations

import json
import logging
import shlex
import uuid
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional, Union

import requests

from .exceptions import (
    APIError,
    AuthenticationError,
    CommandExecutionError,
    ConnectionError,
    FileOperationError,
    MCPError,
    RateLimitError,
    ResourceNotFoundError,
    TimeoutError,
    ValidationError,
)

if TYPE_CHECKING:
    from requests import Response

# Configure module logger
logger = logging.getLogger(__name__)


class OpsBeaconClient:
    """
    Client for interacting with the OpsBeacon API.

    This client provides methods for managing commands, connections, users,
    groups, files, triggers, and policies in your OpsBeacon workspace.

    Attributes:
        api_domain: The domain of the OpsBeacon API.
        timeout: Request timeout in seconds.

    Example:
        >>> from opsbeacon import OpsBeaconClient
        >>> client = OpsBeaconClient(
        ...     api_domain="api.console.opsbeacon.com",
        ...     api_token="your-api-token"
        ... )
        >>> commands = client.commands()
        >>> for cmd in commands:
        ...     print(cmd["name"])
    """

    DEFAULT_TIMEOUT = 30.0
    SDK_VERSION = "1.3.0"

    def __init__(
        self,
        api_domain: str,
        api_token: str,
        *,
        timeout: float = DEFAULT_TIMEOUT,
        debug: bool = False,
    ) -> None:
        """
        Initialize the OpsBeacon client.

        Args:
            api_domain: The OpsBeacon API domain (e.g., "api.console.opsbeacon.com").
            api_token: Your API token for authentication.
            timeout: Request timeout in seconds (default: 30).
            debug: Enable debug logging for HTTP requests/responses.

        Raises:
            ValidationError: If api_domain or api_token is empty.
        """
        if not api_domain:
            raise ValidationError("api_domain is required", field="api_domain")
        if not api_token:
            raise ValidationError("api_token is required", field="api_token")

        self.api_domain = api_domain.rstrip("/")
        self._api_token = api_token
        self.timeout = timeout
        self.debug = debug

        self._session = requests.Session()
        self._session.headers.update(
            {
                "Authorization": f"Bearer {self._api_token}",
                "Content-Type": "application/json",
                "User-Agent": f"OpsBeacon-Python-SDK/{self.SDK_VERSION}",
            }
        )

        if debug:
            logging.basicConfig(level=logging.DEBUG)
            logger.setLevel(logging.DEBUG)

    @property
    def base_url(self) -> str:
        """Return the base URL for API requests."""
        return f"https://{self.api_domain}"

    def _log_request(
        self,
        method: str,
        url: str,
        headers: Optional[dict[str, Any]] = None,
        json_data: Optional[dict[str, Any]] = None,
    ) -> None:
        """Log HTTP request details in debug mode."""
        if self.debug:
            # Mask sensitive data
            safe_headers = {k: "***" if k.lower() == "authorization" else v
                           for k, v in (headers or {}).items()}
            logger.debug("HTTP Request: %s %s", method, url)
            logger.debug("Headers: %s", safe_headers)
            if json_data:
                logger.debug("Body: %s", json.dumps(json_data, indent=2))

    def _log_response(self, response: Response) -> None:
        """Log HTTP response details in debug mode."""
        if self.debug:
            logger.debug("HTTP Response: %s", response.status_code)
            try:
                logger.debug("Body: %s", json.dumps(response.json(), indent=2))
            except ValueError:
                logger.debug("Body: %s", response.text[:500])

    def _handle_response_error(self, response: Response) -> None:
        """Handle HTTP error responses and raise appropriate exceptions."""
        if response.status_code == 401:
            raise AuthenticationError()
        if response.status_code == 403:
            raise AuthenticationError("Access forbidden. Check your API token permissions.")
        if response.status_code == 404:
            raise APIError("Resource not found", status_code=404, response_body=response.text)
        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            raise RateLimitError(
                retry_after=int(retry_after) if retry_after else None
            )
        if response.status_code >= 400:
            try:
                error_body = response.json()
                error_msg = error_body.get("err", error_body.get("error", response.text))
            except ValueError:
                error_msg = response.text
            raise APIError(
                f"API error: {error_msg}",
                status_code=response.status_code,
                response_body=response.text,
            )

    def _request(
        self,
        method: str,
        endpoint: str,
        *,
        json_data: Optional[dict[str, Any]] = None,
        data: Optional[dict[str, Any]] = None,
        files: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
    ) -> Response:
        """
        Make an HTTP request to the OpsBeacon API.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE).
            endpoint: API endpoint path.
            json_data: JSON body data.
            data: Form data.
            files: Files to upload.
            headers: Additional headers.

        Returns:
            The response object.

        Raises:
            ConnectionError: If unable to connect to the API.
            TimeoutError: If the request times out.
            AuthenticationError: If authentication fails.
            APIError: If the API returns an error.
        """
        url = f"{self.base_url}{endpoint}"
        request_headers = dict(self._session.headers)
        if headers:
            request_headers.update(headers)

        # Remove Content-Type for file uploads
        if files:
            request_headers.pop("Content-Type", None)

        self._log_request(method, url, request_headers, json_data)

        try:
            response = self._session.request(
                method=method,
                url=url,
                json=json_data,
                data=data,
                files=files,
                headers=headers,
                timeout=self.timeout,
            )
        except requests.exceptions.ConnectionError as e:
            logger.error("Connection error: %s", e)
            raise ConnectionError(f"Failed to connect to {url}") from e
        except requests.exceptions.Timeout as e:
            logger.error("Request timeout: %s", e)
            raise TimeoutError(timeout=self.timeout) from e
        except requests.exceptions.RequestException as e:
            logger.error("Request error: %s", e)
            raise APIError(f"Request failed: {e}") from e

        self._log_response(response)

        if not response.ok:
            self._handle_response_error(response)

        return response

    # =========================================================================
    # Commands
    # =========================================================================

    def commands(self) -> list[dict[str, Any]]:
        """
        Fetch available commands in the workspace.

        Returns:
            A list of command objects.

        Raises:
            APIError: If the request fails.
        """
        response = self._request("GET", "/workspace/v2/commands")
        return response.json().get("commands", [])

    # =========================================================================
    # Connections
    # =========================================================================

    def connections(self) -> list[dict[str, Any]]:
        """
        Retrieve connections in the workspace.

        Returns:
            A list of connection objects.

        Raises:
            APIError: If the request fails.
        """
        response = self._request("GET", "/workspace/v2/connections")
        return response.json().get("connections", [])

    # =========================================================================
    # Users
    # =========================================================================

    def users(self) -> list[dict[str, Any]]:
        """
        Fetch users in the workspace.

        Returns:
            A list of user objects.

        Raises:
            APIError: If the request fails.
        """
        response = self._request("GET", "/workspace/v2/users")
        return response.json().get("users", [])

    def add_user(self, user: dict[str, Any]) -> dict[str, Any]:
        """
        Add a new user to the workspace.

        Args:
            user: User details including email and role.

        Returns:
            The created user object.

        Raises:
            ValidationError: If user data is invalid.
            APIError: If the request fails.
        """
        if not user:
            raise ValidationError("User data is required", field="user")
        response = self._request("POST", "/workspace/v2/users", json_data=user)
        return response.json()

    def delete_user(self, user_id: str) -> bool:
        """
        Delete a user from the workspace.

        Args:
            user_id: The ID of the user to delete.

        Returns:
            True if successfully deleted.

        Raises:
            ValidationError: If user_id is empty.
            ResourceNotFoundError: If user is not found.
            APIError: If the request fails.
        """
        if not user_id:
            raise ValidationError("user_id is required", field="user_id")
        self._request("DELETE", f"/workspace/v2/users/{user_id}")
        return True

    # =========================================================================
    # Groups
    # =========================================================================

    def groups(self) -> list[dict[str, Any]]:
        """
        Fetch groups in the workspace.

        Returns:
            A list of group objects.

        Raises:
            APIError: If the request fails.
        """
        response = self._request("GET", "/workspace/v2/policy/group")
        return response.json().get("groups", [])

    def add_group(self, group: dict[str, Any]) -> dict[str, Any]:
        """
        Add a new group to the workspace.

        Args:
            group: Group details including name and members.

        Returns:
            The created group object.

        Raises:
            ValidationError: If group data is invalid.
            APIError: If the request fails.
        """
        if not group:
            raise ValidationError("Group data is required", field="group")
        response = self._request("POST", "/workspace/v2/policy/group", json_data=group)
        return response.json()

    def delete_group(self, group_name: str) -> bool:
        """
        Delete a group from the workspace.

        Args:
            group_name: The name of the group to delete.

        Returns:
            True if successfully deleted.

        Raises:
            ValidationError: If group_name is empty.
            APIError: If the request fails.
        """
        if not group_name:
            raise ValidationError("group_name is required", field="group_name")
        self._request("DELETE", f"/workspace/v2/policy/group/{group_name}")
        return True

    # =========================================================================
    # Files
    # =========================================================================

    def file_upload(
        self,
        *,
        file_content: Optional[str] = None,
        file_name: Optional[str] = None,
        input_file: Optional[Union[str, Path]] = None,
    ) -> str:
        """
        Upload a file to the OpsBeacon workspace.

        Args:
            file_content: Content of the file as a string.
            file_name: Name for the uploaded file.
            input_file: Path to a local file to upload.

        Returns:
            The upload response text.

        Raises:
            ValidationError: If required parameters are missing.
            FileOperationError: If the upload fails.
        """
        if file_content is not None:
            if not file_name:
                raise ValidationError(
                    "file_name is required when uploading content",
                    field="file_name",
                )
            files = {"file": (file_name, file_content, "text/csv")}
            data = {"filename": file_name}
        elif input_file is not None:
            input_path = Path(input_file)
            if not input_path.exists():
                raise FileOperationError(
                    f"File not found: {input_file}",
                    file_name=str(input_file),
                    operation="upload",
                )
            actual_file_name = file_name or input_path.name
            files = {"file": (actual_file_name, input_path.open("rb"), "application/octet-stream")}
            data = {"filename": actual_file_name}
        else:
            raise ValidationError(
                "Either file_content or input_file must be provided",
            )

        try:
            response = self._request(
                "POST",
                "/workspace/v2/files",
                data=data,
                files=files,
            )
            return response.text
        except APIError as e:
            raise FileOperationError(
                f"Failed to upload file: {e}",
                file_name=file_name,
                operation="upload",
            ) from e

    def get_file_download_url(self, file_id: str) -> str:
        """
        Get a download URL for a file.

        Args:
            file_id: The ID of the file.

        Returns:
            The download URL.

        Raises:
            ValidationError: If file_id is empty.
            ResourceNotFoundError: If file is not found.
            APIError: If the request fails.
        """
        if not file_id:
            raise ValidationError("file_id is required", field="file_id")

        response = self._request("GET", f"/workspace/v2/file-url/{file_id}")
        result = response.json()

        if not result.get("success", False):
            error_msg = result.get("err", "Unknown error")
            raise FileOperationError(
                error_msg,
                file_name=file_id,
                operation="get_download_url",
            )

        return result["url"]

    def file_download(
        self,
        file_name: str,
        destination_path: Optional[Union[str, Path]] = None,
    ) -> bool:
        """
        Download a file from OpsBeacon.

        Args:
            file_name: Name of the file to download.
            destination_path: Local path to save the file.

        Returns:
            True if successfully downloaded.

        Raises:
            ValidationError: If file_name is empty.
            FileOperationError: If download fails.
        """
        if not file_name:
            raise ValidationError("file_name is required", field="file_name")

        download_url = self.get_file_download_url(file_name)
        dest = Path(destination_path) if destination_path else Path(file_name)

        try:
            response = requests.get(download_url, timeout=self.timeout)
            response.raise_for_status()
            dest.write_bytes(response.content)
            return True
        except requests.RequestException as e:
            raise FileOperationError(
                f"Failed to download file: {e}",
                file_name=file_name,
                operation="download",
            ) from e

    # =========================================================================
    # Command Execution
    # =========================================================================

    def run(
        self,
        *,
        command_text: Optional[str] = None,
        connection: Optional[str] = None,
        command: Optional[str] = None,
        args: Optional[Union[list[str], str]] = None,
    ) -> dict[str, Any]:
        """
        Execute a command in the OpsBeacon workspace.

        You can either provide a command_text string, or use structured
        parameters (connection, command, args).

        Args:
            command_text: A command line string to execute.
            connection: Connection identifier for structured execution.
            command: Command name for structured execution.
            args: Arguments for the command (list or space-separated string).

        Returns:
            The command execution response.

        Raises:
            ValidationError: If required parameters are missing.
            CommandExecutionError: If execution fails.

        Example:
            >>> # Using command text
            >>> result = client.run(command_text="myserver: check-disk")
            >>>
            >>> # Using structured parameters
            >>> result = client.run(
            ...     connection="myserver",
            ...     command="check-disk",
            ...     args=["--verbose"]
            ... )
        """
        if command_text:
            body: dict[str, Any] = {"commandLine": command_text}
        elif command and connection:
            # Convert string args to list if needed
            if isinstance(args, str):
                args_list = shlex.split(args) if args else []
            else:
                args_list = list(args) if args else []
            body = {
                "command": command,
                "connection": connection,
                "arguments": args_list,
            }
        else:
            raise ValidationError(
                "Either command_text or both connection and command are required"
            )

        try:
            response = self._request("POST", "/trigger/v1/api", json_data=body)
            return response.json()
        except APIError as e:
            raise CommandExecutionError(
                f"Command execution failed: {e}",
                command=command or command_text,
                connection=connection,
            ) from e

    # =========================================================================
    # Triggers
    # =========================================================================

    def triggers(self, kind: Optional[str] = None) -> list[dict[str, Any]]:
        """
        Fetch triggers in the workspace.

        Args:
            kind: Filter by trigger kind (e.g., 'mcp', 'webHook', 'cron', 'link').

        Returns:
            A list of trigger objects.

        Raises:
            APIError: If the request fails.
        """
        response = self._request("GET", "/workspace/v2/triggers")
        triggers = response.json().get("triggers", [])

        if kind:
            triggers = [t for t in triggers if t.get("kind") == kind]

        return triggers

    def mcp_triggers(self) -> list[dict[str, Any]]:
        """
        Fetch MCP triggers in the workspace.

        Returns:
            A list of MCP trigger objects.

        Raises:
            APIError: If the request fails.
        """
        return self.triggers(kind="mcp")

    def get_trigger(self, name: str) -> dict[str, Any]:
        """
        Get details of a specific trigger.

        Args:
            name: The name of the trigger.

        Returns:
            The trigger details.

        Raises:
            ValidationError: If name is empty.
            ResourceNotFoundError: If trigger is not found.
            APIError: If the request fails.
        """
        if not name:
            raise ValidationError("name is required", field="name")

        try:
            response = self._request("GET", f"/workspace/v2/triggers/{name}")
            return response.json()
        except APIError as e:
            # Try listing all triggers and finding by name
            all_triggers = self.triggers()
            for trigger in all_triggers:
                if trigger.get("name") == name:
                    return trigger
            raise ResourceNotFoundError("Trigger", name) from e

    def create_mcp_trigger(
        self,
        name: str,
        *,
        description: str = "",
        tool_instances: Optional[list[dict[str, Any]]] = None,
        policies: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        """
        Create a new MCP trigger.

        Important:
            The API token is only returned during creation and cannot be
            retrieved later. Save it immediately.

        Args:
            name: The name of the MCP trigger.
            description: Description of the trigger.
            tool_instances: List of tool configurations.
            policies: List of policy names to apply.

        Returns:
            Response containing:
                - success: True if created
                - name: The trigger name
                - url: The MCP server URL
                - apiToken: The API token (save this!)

        Raises:
            ValidationError: If name is empty.
            MCPError: If creation fails.
        """
        if not name:
            raise ValidationError("name is required", field="name")

        # Extract commands and connections from tool instances
        commands: list[str] = []
        connections: list[str] = []

        for tool in tool_instances or []:
            overrides = tool.get("overrides", {})
            if overrides.get("command"):
                commands.append(overrides["command"])
            if overrides.get("connection"):
                connections.append(overrides["connection"])

        # Remove duplicates
        commands = list(set(commands))
        connections = list(set(connections))

        payload = {
            "name": name,
            "description": description,
            "kind": "mcp",
            "commands": commands,
            "connections": connections,
            "policies": policies or [],
            "mcpTriggerInfo": {"toolInstances": tool_instances or []},
        }

        try:
            response = self._request("POST", "/workspace/v2/triggers", json_data=payload)
            result = response.json()

            if result.get("url"):
                return {
                    "success": True,
                    "name": name,
                    "url": result.get("url"),
                    "apiToken": result.get("apiToken"),
                    "message": f"MCP trigger '{name}' created successfully",
                }

            if result.get("err"):
                raise MCPError(result["err"], trigger_name=name)

            return result
        except APIError as e:
            raise MCPError(f"Failed to create MCP trigger: {e}", trigger_name=name) from e

    def update_mcp_trigger(
        self,
        name: str,
        *,
        description: Optional[str] = None,
        tool_instances: Optional[list[dict[str, Any]]] = None,
    ) -> dict[str, Any]:
        """
        Update an existing MCP trigger.

        Args:
            name: The name of the MCP trigger to update.
            description: New description (optional).
            tool_instances: Updated tool configurations (optional).

        Returns:
            The updated trigger object.

        Raises:
            ValidationError: If name is empty.
            ResourceNotFoundError: If trigger is not found.
            MCPError: If update fails.
        """
        if not name:
            raise ValidationError("name is required", field="name")

        # Get existing trigger
        existing = self.get_trigger(name)
        if existing.get("kind") != "mcp":
            raise MCPError(f"'{name}' is not an MCP trigger", trigger_name=name)

        # Extract commands and connections
        if tool_instances is not None:
            commands: list[str] = []
            connections: list[str] = []
            for tool in tool_instances:
                overrides = tool.get("overrides", {})
                if overrides.get("command"):
                    commands.append(overrides["command"])
                if overrides.get("connection"):
                    connections.append(overrides["connection"])
            commands = list(set(commands))
            connections = list(set(connections))
        else:
            commands = existing.get("commands", [])
            connections = existing.get("connections", [])

        payload = {
            "name": name,
            "kind": "mcp",
            "description": description if description is not None else existing.get("description", ""),
            "commands": commands,
            "connections": connections,
            "mcpTriggerInfo": existing.get("mcpTriggerInfo", {}),
        }

        if tool_instances is not None:
            payload["mcpTriggerInfo"]["toolInstances"] = tool_instances

        try:
            response = self._request("PUT", f"/workspace/v2/triggers/{name}", json_data=payload)
            return response.json()
        except APIError as e:
            raise MCPError(f"Failed to update MCP trigger: {e}", trigger_name=name) from e

    def delete_trigger(self, name: str) -> bool:
        """
        Delete a trigger.

        Args:
            name: The name of the trigger to delete.

        Returns:
            True if successfully deleted.

        Raises:
            ValidationError: If name is empty.
            APIError: If deletion fails.
        """
        if not name:
            raise ValidationError("name is required", field="name")
        self._request("DELETE", f"/workspace/v2/triggers/{name}")
        return True

    def get_mcp_trigger_url(self, name: str) -> Optional[str]:
        """
        Get the MCP server URL for a trigger.

        Args:
            name: The name of the MCP trigger.

        Returns:
            The MCP server URL, or None if not found.

        Raises:
            ValidationError: If name is empty.
        """
        if not name:
            raise ValidationError("name is required", field="name")

        try:
            trigger = self.get_trigger(name)
            if trigger.get("kind") == "mcp":
                return trigger.get("triggerUrl")
        except ResourceNotFoundError:
            pass
        return None

    def add_tool_to_mcp_trigger(
        self,
        trigger_name: str,
        tool_config: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Add a tool to an existing MCP trigger.

        Args:
            trigger_name: The name of the MCP trigger.
            tool_config: Tool configuration with:
                - name: Tool name visible to AI
                - description: Tool description
                - connection: Connection to use
                - command: Command to execute
                - arguments: Optional argument configurations

        Returns:
            The updated trigger object.

        Raises:
            ValidationError: If parameters are invalid.
            ResourceNotFoundError: If trigger is not found.
            MCPError: If update fails.
        """
        if not trigger_name:
            raise ValidationError("trigger_name is required", field="trigger_name")
        if not tool_config:
            raise ValidationError("tool_config is required", field="tool_config")

        trigger = self.get_trigger(trigger_name)
        if trigger.get("kind") != "mcp":
            raise MCPError(f"'{trigger_name}' is not an MCP trigger", trigger_name=trigger_name)

        # Get existing tool instances
        mcp_info = trigger.get("mcpTriggerInfo", {})
        tool_instances = list(mcp_info.get("toolInstances", []))

        # Create new tool instance
        instance_id = str(uuid.uuid4())
        new_tool = {
            "instanceId": instance_id,
            "templateId": instance_id,
            "overrides": {
                "name": tool_config.get("name", f"tool_{len(tool_instances) + 1}"),
                "description": tool_config.get("description", ""),
                "connection": tool_config.get("connection", ""),
                "command": tool_config.get("command", ""),
                "argumentOverrides": tool_config.get("arguments", {}),
            },
        }

        tool_instances.append(new_tool)
        return self.update_mcp_trigger(trigger_name, tool_instances=tool_instances)

    def remove_tool_from_mcp_trigger(
        self,
        trigger_name: str,
        tool_name: str,
    ) -> dict[str, Any]:
        """
        Remove a tool from an MCP trigger.

        Args:
            trigger_name: The name of the MCP trigger.
            tool_name: The name of the tool to remove.

        Returns:
            The updated trigger object.

        Raises:
            ValidationError: If parameters are invalid.
            ResourceNotFoundError: If trigger or tool is not found.
            MCPError: If update fails.
        """
        if not trigger_name:
            raise ValidationError("trigger_name is required", field="trigger_name")
        if not tool_name:
            raise ValidationError("tool_name is required", field="tool_name")

        trigger = self.get_trigger(trigger_name)
        if trigger.get("kind") != "mcp":
            raise MCPError(f"'{trigger_name}' is not an MCP trigger", trigger_name=trigger_name)

        mcp_info = trigger.get("mcpTriggerInfo", {})
        tool_instances = mcp_info.get("toolInstances", [])

        updated_tools = [
            t for t in tool_instances
            if t.get("overrides", {}).get("name") != tool_name
        ]

        if len(updated_tools) == len(tool_instances):
            raise ResourceNotFoundError("Tool", tool_name)

        return self.update_mcp_trigger(trigger_name, tool_instances=updated_tools)

    # =========================================================================
    # MCP Protocol Testing
    # =========================================================================

    def test_mcp_protocol(
        self,
        mcp_url: str,
        api_token: str,
        *,
        tool_name: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Test an MCP server by initializing, listing tools, and executing.

        Args:
            mcp_url: The MCP server URL.
            api_token: The API token for authentication.
            tool_name: Specific tool to execute (optional).

        Returns:
            Test results including initialization, tools list, and execution.
        """
        if not mcp_url:
            raise ValidationError("mcp_url is required", field="mcp_url")
        if not api_token:
            raise ValidationError("api_token is required", field="api_token")

        headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
        }

        results: dict[str, Any] = {
            "initialize": None,
            "tools": None,
            "execution": None,
            "success": False,
        }

        # 1. Initialize
        init_request = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "0.1.0",
                "capabilities": {},
                "clientInfo": {"name": "OpsBeacon Python SDK", "version": self.SDK_VERSION},
            },
            "id": 1,
        }

        try:
            response = requests.post(mcp_url, json=init_request, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            results["initialize"] = response.json()
        except requests.RequestException as e:
            results["initialize"] = {"error": str(e)}
            return results

        # 2. List tools
        list_request = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {},
            "id": 2,
        }

        try:
            response = requests.post(mcp_url, json=list_request, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            tools_response = response.json()
            results["tools"] = tools_response

            tools = []
            if "result" in tools_response and "tools" in tools_response["result"]:
                tools = tools_response["result"]["tools"]
        except requests.RequestException as e:
            results["tools"] = {"error": str(e)}
            return results

        # 3. Execute a tool
        if tools:
            tool_to_execute = None
            if tool_name:
                tool_to_execute = next((t for t in tools if t["name"] == tool_name), None)
            if not tool_to_execute:
                tool_to_execute = tools[0]

            if tool_to_execute:
                exec_request = {
                    "jsonrpc": "2.0",
                    "method": "tools/call",
                    "params": {"name": tool_to_execute["name"], "arguments": {}},
                    "id": 3,
                }

                try:
                    response = requests.post(mcp_url, json=exec_request, headers=headers, timeout=self.timeout)
                    response.raise_for_status()
                    results["execution"] = response.json()
                    results["success"] = "result" in results["execution"]
                except requests.RequestException as e:
                    results["execution"] = {"error": str(e)}
        else:
            results["execution"] = {"message": "No tools available to execute"}

        return results

    # =========================================================================
    # Policies
    # =========================================================================

    def policies(self) -> list[dict[str, Any]]:
        """
        Fetch execution policies in the workspace.

        Returns:
            A list of policy objects.

        Raises:
            APIError: If the request fails.
        """
        response = self._request("GET", "/workspace/v2/policy")
        return response.json().get("policies", [])

    def create_policy(
        self,
        name: str,
        *,
        description: str = "",
        commands: Optional[list[str]] = None,
        connections: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        """
        Create a new execution policy.

        Args:
            name: The name of the policy.
            description: Description of the policy.
            commands: List of allowed command names.
            connections: List of allowed connection names.

        Returns:
            The created policy object.

        Raises:
            ValidationError: If name is empty.
            APIError: If the request fails.
        """
        if not name:
            raise ValidationError("name is required", field="name")

        payload = {
            "name": name,
            "description": description,
            "commands": commands or [],
            "connections": connections or [],
        }

        response = self._request("POST", "/workspace/v2/policy", json_data=payload)
        return response.json()

    def get_policy(self, name: str) -> dict[str, Any]:
        """
        Get details of a specific policy.

        Args:
            name: The name of the policy.

        Returns:
            The policy details.

        Raises:
            ValidationError: If name is empty.
            ResourceNotFoundError: If policy is not found.
        """
        if not name:
            raise ValidationError("name is required", field="name")

        try:
            response = self._request("GET", f"/workspace/v2/policy/{name}")
            return response.json()
        except APIError as e:
            all_policies = self.policies()
            for policy in all_policies:
                if policy.get("name") == name:
                    return policy
            raise ResourceNotFoundError("Policy", name) from e

    def delete_policy(self, name: str) -> bool:
        """
        Delete a policy.

        Args:
            name: The name of the policy to delete.

        Returns:
            True if successfully deleted.

        Raises:
            ValidationError: If name is empty.
            APIError: If deletion fails.
        """
        if not name:
            raise ValidationError("name is required", field="name")
        self._request("DELETE", f"/workspace/v2/policy/{name}")
        return True

    # =========================================================================
    # Context Manager Support
    # =========================================================================

    def __enter__(self) -> OpsBeaconClient:
        """Enter context manager."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit context manager and close session."""
        self._session.close()

    def close(self) -> None:
        """Close the underlying HTTP session."""
        self._session.close()
