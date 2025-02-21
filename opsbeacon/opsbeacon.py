import requests
from typing import List, Dict, Any, Optional

class OpsBeaconClient:
    """
    Client library to interact with the OpsBeacon API for managing commands, connections, users, groups, files, and apps.

    Attributes:
        api_domain (str): The domain of the OpsBeacon API.
        api_token (str): The token used for authenticating API requests.
        headers (dict): The default headers for API requests, including the authorization token.
    """
    
    def __init__(self, api_domain: str, api_token: str):
        """
        Initializes the OpsBeaconClient with the specified API domain and token.

        Args:
            api_domain (str): The domain of the OpsBeacon API.
            api_token (str): The API token for authenticating requests.
        """
        self.api_domain = api_domain
        self.api_token = api_token
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }

    def commands(self) -> List[Dict[str, Any]]:
        """
        Fetch a list of available commands in the workspace.

        Returns:
            List[Dict[str, Any]]: A list of command objects.
        """
        url = f'https://{self.api_domain}/workspace/v2/commands'
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json().get("commands", [])
        except requests.RequestException as e:
            print(f"Error fetching commands: {e}")
            return []
    
    def connections(self) -> List[Dict[str, Any]]:
        """
        Retrieve a list of connections in the workspace.

        Returns:
            List[Dict[str, Any]]: A list of connection objects.
        """
        url = f'https://{self.api_domain}/workspace/v2/connections'
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json().get("connections", [])
        except requests.RequestException as e:
            print(f"Failed to fetch connections: {e}")
            return []
        
    def users(self) -> List[Dict[str, Any]]:
        """
        Fetch a list of users in the workspace.

        Returns:
            List[Dict[str, Any]]: A list of user objects.
        """
        url = f'https://{self.api_domain}/workspace/v2/users'
        try: 
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json().get("users", [])
        except requests.RequestException as e:
            print(f"Failed to fetch users: {e}")
            return []
    
    def add_user(self, user: Dict[str, Any]) -> bool:
        """
        Add a new user to the workspace.

        Args:
            user (Dict[str, Any]): User details to be added.

        Returns:
            bool: True if the user was successfully added, False otherwise.
        """
        url = f'https://{self.api_domain}/workspace/v2/users'
        try:
            response = requests.post(url, headers=self.headers, json=user)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Failed to add user: {e}")
            return False

    def delete_user(self, user_id: str) -> bool:
        """
        Delete a user from the workspace by user ID.

        Args:
            user_id (str): The ID of the user to delete.

        Returns:
            bool: True if the user was successfully deleted, False otherwise.
        """
        url = f'https://{self.api_domain}/workspace/v2/users/{user_id}'
        try:
            response = requests.delete(url, headers=self.headers)
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            print(f"Failed to delete user: {e}")
            return False
        
    def groups(self) -> List[Dict[str, Any]]:
        """
        Fetch a list of groups defined in the workspace.

        Returns:
            List[Dict[str, Any]]: A list of group objects.
        """
        url = f'https://{self.api_domain}/workspace/v2/policy/group'
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json().get("groups", [])
        except requests.RequestException as e:
            print(f"Failed to fetch groups: {e}")
            return []
    
    def add_group(self, group: Dict[str, Any]) -> bool:
        """
        Add a new group to the workspace.

        Args:
            group (Dict[str, Any]): Group details to be added.

        Returns:
            bool: True if the group was successfully added, False otherwise.
        """
        url = f'https://{self.api_domain}/workspace/v2/policy/group'
        try:
            response = requests.post(url, headers=self.headers, json=group)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Failed to add group: {e}")
            return False
    
    def delete_group(self, group_name: str) -> bool:
        """
        Delete a group from the workspace by group name.

        Args:
            group_name (str): The name of the group to delete.

        Returns:
            bool: True if the group was successfully deleted, False otherwise.
        """
        url = f'https://{self.api_domain}/workspace/v2/policy/group/{group_name}'
        try:
            response = requests.delete(url, headers=self.headers)
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            print(f"Failed to delete group: {e}")
            return False

    def file_upload(self, file_content: str = None, file_name: str = None, input_file: str = None) -> bool:
        """
        Upload a file to the OpsBeacon workspace.

        Args:
            file_content (str, optional): Content of the file as a string.
            file_name (str, optional): Name of the file.
            input_file (str, optional): Path to the file for uploading.

        Returns:
            bool: True if the file was uploaded successfully, False otherwise.
        """
        url = f'https://{self.api_domain}/workspace/v2/files'
        self.headers.pop("Content-Type", None)

        if file_content:
            if not file_name:
                raise ValueError("File name is required for file upload")
            files = {
                'file': (file_name, file_content, 'text/csv')
            }
            body = {"filename": file_name}
            try:
                response = requests.post(url, headers=self.headers, files=files, data=body)
                response.raise_for_status()
                return response.text
            except requests.RequestException as e:
                print(f"Failed to upload file: {e}")
                return False
        elif input_file:
            if not file_name:
                file_name = input_file.split("/")[-1]

            files = {
                'file': (file_name, open(input_file, "rb"), "application/octet-stream")
            }
            
            body = {"filename": file_name}
            try:
                response = requests.post(url, headers=self.headers, files=files, data=body)
                response.raise_for_status()
                return response.text
            except requests.RequestException as e:
                print(f"Failed to upload file: {e}")
                return False
        else:
            raise ValueError("Invalid input for file upload")
    
    def get_file_download_url(self, file_id: str) -> str:
        """
        Get a download URL for a specified file.

        Args:
            file_id (str): The ID of the file.

        Returns:
            str: The download URL for the file.
        """
        url = f'https://{self.api_domain}/workspace/v2/file-url/{file_id}'
        response = requests.get(url, headers=self.headers)
        success = response.json().get("success", False)
        if not success:
            raise ValueError(response.json().get("err"))
        
        return response.json().get("url")
    
    def file_download(self, file_name: str, destination_path: str = None) -> bool:
        """
        Download a file from OpsBeacon and save it to the specified destination.

        Args:
            file_name (str): Name of the file to download.
            destination_path (str, optional): Path to save the file.

        Returns:
            bool: True if the file was successfully downloaded, False otherwise.
        """
        download_url = self.get_file_download_url(file_name)
        response = requests.get(download_url)
        if not destination_path:
            destination_path = file_name

        with open(destination_path, "wb") as f:
            f.write(response.content)

        return True

    def run(self, command_text: str = "", connection: str = "", command: str = "", args: str = "") -> Dict[str, Any]:
        """
        Execute a command in the OpsBeacon workspace.

        Args:
            command_text (str, optional): The command line text.
            connection (str, optional): Connection identifier.
            command (str, optional): Command name.
            args (str, optional): Arguments for the command.

        Returns:
            Dict[str, Any]: The command execution response.
        """
        if command_text:
            body = {"commandLine": command_text}
        elif command and connection:
            body = {"command": command, "connection": connection, "arguments": args}
        else:
            raise ValueError("Invalid input for command execution")
        
        url = f'https://{self.api_domain}/trigger/v1/api'

        try:
            response = requests.post(url, headers=self.headers, json=body)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Failed to execute command: {e}")
            return {"error": str(e)}
