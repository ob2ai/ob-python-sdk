#!/usr/bin/env python3
"""
Example script demonstrating MCP (Model Context Protocol) trigger operations using the OpsBeacon Python SDK.

This script shows how to:
- List existing MCP triggers
- Create a new MCP trigger with tools
- Add tools to an existing trigger
- Update trigger configurations
- Delete triggers
"""

import argparse
import os
import random
import string
import sys
import time
from datetime import datetime

from dotenv import load_dotenv

# Add parent directory to path for development
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from opsbeacon import OpsBeaconClient


def generate_unique_name(prefix="demo-mcp"):
    """Generate a unique name using timestamp and random suffix."""
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
    return f"{prefix}-{timestamp}-{random_suffix}"

def main(args=None):
    # Load environment variables
    load_dotenv()

    # Initialize client
    api_domain = os.getenv('OPSBEACON_API_DOMAIN', 'api.console.opsbeacon.com')
    api_token = os.getenv('OPSBEACON_API_TOKEN')

    if not api_token:
        print("Error: OPSBEACON_API_TOKEN environment variable is required")
        sys.exit(1)

    client = OpsBeaconClient(api_domain, api_token)

    print("OpsBeacon MCP Trigger Operations Example")
    print("=" * 50)

    # 1. List all triggers
    print("\n1. Listing all triggers:")
    triggers = client.triggers()
    print(f"   Found {len(triggers)} total triggers")

    # 2. List MCP triggers specifically
    print("\n2. Listing MCP triggers:")
    mcp_triggers = client.mcp_triggers()
    for trigger in mcp_triggers:
        print(f"   - {trigger['name']}: {trigger.get('description', 'No description')}")
        if trigger.get('triggerUrl'):
            print(f"     URL: {trigger['triggerUrl']}")

    # 3. Create a new MCP trigger with tools
    print("\n3. Creating a new MCP trigger:")

    # Single test tool configuration for dev environment
    # Using devcontroller connection and df command as specified
    tool_instances = [
        {
            "instanceId": "disk-usage",
            "templateId": "disk-usage",
            "overrides": {
                "name": "disk_usage",  # Simple name as requested
                "description": "Check disk usage on the devcontroller server",
                "connection": "devcontroller",  # Using devcontroller for dev environment
                "command": "df",                 # Using df command
                "argumentOverrides": {}          # No additional arguments needed
            }
        }
    ]

    # Generate a unique name for this test run
    new_trigger_name = generate_unique_name("demo-mcp")
    print(f"   Using unique name: {new_trigger_name}")

    # Create the trigger with unique name
    result = client.create_mcp_trigger(
        name=new_trigger_name,
        description="Demo MCP server with system monitoring tools (auto-generated)",
        tool_instances=tool_instances
    )

    if "error" in result:
        print(f"   Error creating trigger: {result['error']}")
        if "details" in result:
            print(f"   Details: {result['details']}")
        # Exit early if creation failed
        print("\nNote: Skipping remaining tests due to trigger creation failure")
        return
    else:
        # Check if we got the expected response
        if not result or not isinstance(result, dict):
            print(f"   Warning: Unexpected response format: {result}")
            print("\nNote: Skipping remaining tests due to unexpected response")
            return

        print(f"   ✓ Created trigger: {result.get('name', new_trigger_name)}")

        # Small delay to allow trigger to propagate
        print("   Waiting for trigger to be available...")
        time.sleep(2)

        # Display the MCP server URL and API token
        mcp_url = None
        mcp_token = None
        if result.get('url'):
            mcp_url = result['url']
            print(f"   MCP Server URL: {mcp_url}")
        if result.get('apiToken'):
            mcp_token = result['apiToken']
            print(f"   API Token: {mcp_token}")  # Full token for AI applications
            print("\n   IMPORTANT: Save these credentials! The API token is only shown once.")

        # Also try to get URL from the trigger itself
        if not mcp_url:
            trigger_url = client.get_mcp_trigger_url(new_trigger_name)
            if trigger_url:
                mcp_url = trigger_url
                print(f"   MCP Server URL (from trigger): {mcp_url}")

        # Test the MCP protocol if we have credentials
        if mcp_url and mcp_token:
            print("\n   Testing MCP Protocol with disk_usage tool...")
            test_result = client.test_mcp_protocol(mcp_url, mcp_token, tool_name="disk_usage")
            if test_result.get('success'):
                print("   ✓ MCP Protocol test successful!")
                if test_result.get('execution') and 'result' in test_result['execution']:
                    exec_result = test_result['execution']['result']
                    if 'content' in exec_result:
                        for content in exec_result.get('content', []):
                            if content.get('type') == 'text':
                                output = content['text']
                                # Show first 200 chars of output
                                if len(output) > 200:
                                    print(f"   Output preview: {output[:200]}...")
                                else:
                                    print(f"   Output: {output}")
                                break
            else:
                print("   ⚠ MCP Protocol test failed")
                if test_result.get('initialize', {}).get('error'):
                    print(f"     Initialize error: {test_result['initialize']['error']}")
                if test_result.get('tools', {}).get('error'):
                    print(f"     Tools list error: {test_result['tools']['error']}")
                if test_result.get('execution', {}).get('error'):
                    print(f"     Execution error: {test_result['execution']['error']}")

    # 4. Add a tool to existing trigger
    print("\n4. Adding a new tool to the trigger:")

    new_tool = {
        "name": "memory_usage",
        "description": "Check memory usage on the devcontroller server",
        "connection": "devcontroller",
        "command": "free",
        "arguments": {}
    }

    result = client.add_tool_to_mcp_trigger(new_trigger_name, new_tool)
    if "error" in result:
        print(f"   Error adding tool: {result['error']}")
    else:
        print("   Successfully added tool 'memory_usage'")
        mcp_info = result.get('mcpTriggerInfo', {})
        tools = mcp_info.get('toolInstances', [])
        print(f"   Trigger now has {len(tools)} tools")

    # 5. Get trigger details
    print("\n5. Getting trigger details:")
    trigger = client.get_trigger(new_trigger_name)
    if trigger and trigger.get('kind') == 'mcp':
        print(f"   Name: {trigger.get('name', new_trigger_name)}")
        print(f"   Kind: {trigger.get('kind', 'mcp')}")
        print(f"   Description: {trigger.get('description', 'N/A')}")
        if trigger.get('triggerUrl'):
            print(f"   URL: {trigger['triggerUrl']}")
        mcp_info = trigger.get('mcpTriggerInfo', {})
        tools = mcp_info.get('toolInstances', [])
        print(f"   Tools ({len(tools)}):")
        for tool in tools:
            overrides = tool.get('overrides', {})
            print(f"     - {overrides.get('name', 'Unnamed')}: {overrides.get('description', 'No description')}")
    else:
        print(f"   Failed to get trigger details for '{new_trigger_name}'")

    # 6. Update trigger description
    print("\n6. Updating trigger description:")
    result = client.update_mcp_trigger(
        name=new_trigger_name,
        description="Updated demo MCP server with enhanced system monitoring capabilities"
    )
    if "error" in result:
        print(f"   Error updating trigger: {result['error']}")
    else:
        print("   Successfully updated trigger description")

    # 7. Remove a tool from trigger
    print("\n7. Removing a tool from the trigger:")
    result = client.remove_tool_from_mcp_trigger(new_trigger_name, "memory_usage")
    if "error" in result:
        print(f"   Error removing tool: {result['error']}")
    else:
        print("   Successfully removed tool 'memory_usage'")
        mcp_info = result.get('mcpTriggerInfo', {})
        tools = mcp_info.get('toolInstances', [])
        print(f"   Trigger now has {len(tools)} tools")

    # 8. Clean up - delete the demo trigger
    print("\n8. Cleaning up:")
    print(f"   Trigger name: {new_trigger_name}")

    # Check if we should auto-delete or ask
    if hasattr(args, 'auto_delete') and args.auto_delete:
        print("   Auto-deleting trigger (--auto-delete flag set)")
        success = client.delete_trigger(new_trigger_name)
        if success:
            print(f"   ✓ Successfully deleted trigger '{new_trigger_name}'")
        else:
            print(f"   ✗ Failed to delete trigger '{new_trigger_name}'")
    elif hasattr(args, 'skip_delete') and args.skip_delete:
        print("   Skipping deletion (--skip-delete flag set)")
        print(f"   Trigger '{new_trigger_name}' has been kept")
    else:
        user_input = input("   Delete the demo trigger? (y/n): ")
        if user_input.lower() == 'y':
            success = client.delete_trigger(new_trigger_name)
            if success:
                print(f"   ✓ Successfully deleted trigger '{new_trigger_name}'")
            else:
                print(f"   ✗ Failed to delete trigger '{new_trigger_name}'")
        else:
            print(f"   Keeping trigger '{new_trigger_name}'")

    print("\n" + "=" * 50)
    print("MCP operations example completed!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="OpsBeacon MCP Trigger Operations Example - Demonstrates CRUD operations for MCP triggers"
    )
    parser.add_argument(
        '--list-only',
        action='store_true',
        help='Only list existing MCP triggers without creating/modifying'
    )
    parser.add_argument(
        '--skip-delete',
        action='store_true',
        help='Skip the deletion step at the end'
    )
    parser.add_argument(
        '--auto-delete',
        action='store_true',
        help='Automatically delete the created trigger without prompting'
    )

    args = parser.parse_args()

    # If --list-only, just show existing triggers and exit
    if args.list_only:
        load_dotenv()
        api_domain = os.getenv('OPSBEACON_API_DOMAIN', 'api.console.opsbeacon.com')
        api_token = os.getenv('OPSBEACON_API_TOKEN')

        if not api_token:
            print("Error: OPSBEACON_API_TOKEN environment variable is required")
            sys.exit(1)

        client = OpsBeaconClient(api_domain, api_token)
        mcp_triggers = client.mcp_triggers()

        print("Existing MCP Triggers:")
        print("=" * 50)
        for trigger in mcp_triggers:
            print(f"- {trigger['name']}: {trigger.get('description', 'No description')}")
            if trigger.get('triggerUrl'):
                print(f"  URL: {trigger['triggerUrl']}")
        sys.exit(0)

    # Otherwise run the full demo
    main(args)
