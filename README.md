# OpsBeacon Python Client

## Installation

To install the OpsBeacon Python client, you can use pip:

```
pip install opsbeacon-client
```

## Usage

To use the OpsBeacon client, you need to have your API domain and API token. You can obtain these from the OpsBeacon dashboard.

```python
from opsbeacon_client import OpsBeaconClient

client = OpsBeaconClient(api_domain="your-api-domain.opsbeacon.com", api_token="your-api-token")

# Fetch a list of commands
commands = client.commands()
print(commands)

# Fetch a list of connections
connections = client.connections()
print(connections)

# Fetch a list of users
users = client.users()
print(users)

# Add a new user
new_user = {
    "name": "John Doe",
    "email": "john.doe@example.com"
}
client.add_user(new_user)

# Delete a user
client.delete_user("user-id")

# Fetch a list of groups
groups = client.groups()
print(groups)

# Add a new group
new_group = {
    "name": "Admin Group",
    "description": "Group for admin users"
}
client.add_group(new_group)

# Delete a group
client.delete_group("admin-group")

# Upload a file
client.file_upload(file_content="some,csv,data", file_name="example.csv")

# Download a file
client.file_download("example.csv", "downloaded_file.csv")

# Execute a command with string arguments (backward compatibility)
result = client.run(command="restart-server", connection="server-connection", args="--force")
print(result)

# Execute a command with array arguments (recommended)
result = client.run(command="restart-server", connection="server-connection", args=["--force", "--timeout", "30"])
print(result)
```

## API Reference

The OpsBeacon Python client provides the following methods:

- `commands()`: Fetch a list of available commands in the workspace.
- `connections()`: Retrieve a list of connections in the workspace.
- `users()`: Fetch a list of users in the workspace.
- `add_user(user: Dict[str, Any])`: Add a new user to the workspace.
- `delete_user(user_id: str)`: Delete a user from the workspace by user ID.
- `groups()`: Fetch a list of groups defined in the workspace.
- `add_group(group: Dict[str, Any])`: Add a new group to the workspace.
- `delete_group(group_name: str)`: Delete a group from the workspace by group name.
- `file_upload(file_content: str = None, file_name: str = None, input_file: str = None)`: Upload a file to the OpsBeacon workspace.
- `get_file_download_url(file_id: str)`: Get a download URL for a specified file.
- `file_download(file_name: str, destination_path: str = None)`: Download a file from OpsBeacon and save it to the specified destination.
- `run(command_text: str = "", connection: str = "", command: str = "", args: Union[List[str], str] = "")`: Execute a command in the OpsBeacon workspace. The `args` parameter can be either a list of strings or a space-separated string.

Please refer to the docstrings in the code for more detailed information about each method.
