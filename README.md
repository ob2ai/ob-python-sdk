# OpsBeaconClient Python Library

## Overview

`OpsBeaconClient` is a Python library that provides a simple interface to interact with the OpsBeacon API. This client allows you to manage commands, connections, users, groups, files, and applications within an OpsBeacon workspace.

## Installation

To use `OpsBeaconClient`, you need to have Python installed along with the `requests` library. Install `requests` with:

```bash
pip install requests
```

## Getting Started

### Initialize the Client

To start using the `OpsBeaconClient`, instantiate the client with your API domain and API token:

```python
from opsbeacon_client import OpsBeaconClient

client = OpsBeaconClient(api_domain="api.yourdomain.com", api_token="your_api_token")
```

## API Methods

### Commands

- **Fetch commands**: `client.commands()`

  commands = client.commands()

### Connections

- **Fetch connections**: `client.connections()`

  connections = client.connections()

### Users

- **Fetch users**: `client.users()`

  users = client.users()

- **Add user**: `client.add_user(user: Dict[str, Any])`

  new_user = {"username": "jdoe", "email": "jdoe@example.com"}
  success = client.add_user(new_user)

- **Delete user**: `client.delete_user(user_id: str)`

  success = client.delete_user("user_id_123")

### Groups

- **Fetch groups**: `client.groups()`

  groups = client.groups()

- **Add group**: `client.add_group(group: Dict[str, Any])`

  new_group = {"name": "admin_group", "permissions": ["read", "write"]}
  success = client.add_group(new_group)

- **Delete group**: `client.delete_group(group_name: str)`

  success = client.delete_group("admin_group")

### File Management

- **Upload file**: `client.file_upload(file_content: str, file_name: str)`

  success = client.file_upload(file_content="data", file_name="data.csv")

- **Download file**: `client.file_download(file_name: str, destination_path: str)`

  success = client.file_download("report.csv", destination_path="/path/to/save")

### Command Execution

- **Run command**: `client.run(command_text: str, connection: str, command: str, args: str)`

  response = client.run(command_text="ls -l")

### Applications

- **Create or Update an Application**: `client.create_or_update_app(app_json: Dict[str, Any])`

  app_details = {"name": "MyApp", "version": "1.0"}
  response = client.create_or_update_app(app_details)

## Error Handling

The library catches `requests.RequestException` errors and outputs them to the console. Each method returns `False` or an empty list if the request fails. Make sure to handle these cases in your implementation.

## Example Usage

```python
from opsbeacon_client import OpsBeaconClient
```

# Initialize the client
```python
client = OpsBeaconClient(api_domain="api.yourdomain.com", api_token="your_api_token")
```

# Fetch and print commands
```python
commands = client.commands()
print("Commands:", commands)
```

# Add a new user
```python
new_user = {"username": "jdoe", "email": "jdoe@example.com"}
success = client.add_user(new_user)
if success:
    print("User added successfully.")
else:
    print("Failed to add user.")
```

## License

This project is licensed under the MIT License. See the LICENSE file for more details.

## Contributing

Feel free to submit issues or pull requests to improve this library.
