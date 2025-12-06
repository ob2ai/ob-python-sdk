def lambda_handler(ob, event):
    """
    AWS Lambda handler that uses OpsBeacon SDK to execute commands.
    
    Args:
        ob: Pre-initialized OpsBeaconClient instance
        event: Lambda event containing command execution parameters
        
    Expected event structure:
    {
        "command": "restart-service",
        "connection": "prod-server-1",
        "arguments": ["--service", "nginx", "--force"]
    }
    
    Or for command line execution:
    {
        "commandLine": "restart-service prod-server-1 --service nginx --force"
    }
    """

    # Extract parameters from event
    command_line = event.get("commandLine")

    if command_line:
        # Execute using command line syntax
        response = ob.run(command_text=command_line)
    else:
        # Execute using structured parameters
        command = event.get("command", "")
        connection = event.get("connection", "")
        arguments = event.get("arguments", [])

        if not command or not connection:
            return {
                "statusCode": 400,
                "body": {"error": "Missing required parameters: command and connection"}
            }

        response = ob.run(
            command=command,
            connection=connection,
            args=arguments  # Note: parameter is 'args' not 'arguments'
        )

    # Check if execution was successful
    if "error" in response:
        return {
            "statusCode": 500,
            "body": {
                "error": response["error"],
                "message": "Command execution failed"
            }
        }

    # Check if the API returned success: false
    if response.get("success") is False:
        return {
            "statusCode": 400,
            "body": {
                "error": response.get("response", "Command execution failed"),
                "message": "Command execution was not successful",
                "result": response
            }
        }

    return {
        "statusCode": 200,
        "body": {
            "message": "Command executed successfully",
            "result": response
        }
    }


# Example usage scenarios:

# Scenario 1: Restart a service
example_event_1 = {
    "command": "restart-service",
    "connection": "prod-web-server",
    "arguments": ["--service", "nginx", "--graceful"]
}

# Scenario 2: Deploy application
example_event_2 = {
    "command": "deploy-app",
    "connection": "staging-server",
    "arguments": ["--version", "2.1.0", "--rollback-on-failure"]
}

# Scenario 3: Run system diagnostics
example_event_3 = {
    "commandLine": "run-diagnostics prod-db-server --verbose --output json"
}

# Scenario 4: Database backup
example_event_4 = {
    "command": "backup-database",
    "connection": "prod-db-master",
    "arguments": ["--database", "customers", "--compression", "gzip", "--destination", "s3://backups/"]
}
