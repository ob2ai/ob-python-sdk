#!/usr/bin/env python3
"""
Quick test script for MCP trigger operations.
"""

import os
import random
import string
import sys
from datetime import datetime

from dotenv import load_dotenv

# Add current directory to path for development
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from opsbeacon import OpsBeaconClient


def generate_unique_name(prefix="test-mcp"):
    """Generate a unique name using timestamp and random suffix."""
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
    return f"{prefix}-{timestamp}-{random_suffix}"

def test_mcp_operations():
    # Load environment variables
    load_dotenv()

    api_domain = os.getenv('OPSBEACON_API_DOMAIN', 'api.console.opsbeacon.com')
    api_token = os.getenv('OPSBEACON_API_TOKEN')

    if not api_token:
        print("Error: OPSBEACON_API_TOKEN environment variable is required")
        print("Please set it in your .env file or environment")
        return False

    print(f"Testing MCP operations with domain: {api_domain}")
    print("=" * 50)

    client = OpsBeaconClient(api_domain, api_token)

    # Test 1: List all triggers
    print("\n1. Testing triggers() method:")
    try:
        triggers = client.triggers()
        print(f"   ✓ Successfully fetched {len(triggers)} triggers")
        for trigger in triggers[:3]:  # Show first 3
            print(f"     - {trigger.get('name')} ({trigger.get('kind')})")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        return False

    # Test 2: List MCP triggers
    print("\n2. Testing mcp_triggers() method:")
    try:
        mcp_triggers = client.mcp_triggers()
        print(f"   ✓ Successfully fetched {len(mcp_triggers)} MCP triggers")
        for trigger in mcp_triggers[:3]:  # Show first 3
            print(f"     - {trigger.get('name')}")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        return False

    # Test 3: Get a specific trigger (if any exist)
    if mcp_triggers:
        print("\n3. Testing get_trigger() method:")
        trigger_name = mcp_triggers[0].get('name')
        try:
            trigger = client.get_trigger(trigger_name)
            print(f"   ✓ Successfully fetched trigger '{trigger_name}'")
            print(f"     - Kind: {trigger.get('kind')}")
            print(f"     - Description: {trigger.get('description', 'N/A')}")
            mcp_info = trigger.get('mcpTriggerInfo', {})
            tools = mcp_info.get('toolInstances', [])
            print(f"     - Tools: {len(tools)}")
        except Exception as e:
            print(f"   ✗ Failed: {e}")

    # Test 4: Get MCP URL
    if mcp_triggers:
        print("\n4. Testing get_mcp_trigger_url() method:")
        trigger_name = mcp_triggers[0].get('name')
        try:
            url = client.get_mcp_trigger_url(trigger_name)
            if url:
                print(f"   ✓ Successfully got URL for '{trigger_name}'")
                print(f"     - URL: {url}")
            else:
                print(f"   ⚠ No URL found for '{trigger_name}'")
        except Exception as e:
            print(f"   ✗ Failed: {e}")

    # Test 5: Create a test trigger
    print("\n5. Testing create_mcp_trigger() method:")
    test_trigger_name = generate_unique_name("test-mcp")
    print(f"   Creating test trigger: {test_trigger_name}")

    try:
        # Create a minimal test trigger with disk_usage tool
        result = client.create_mcp_trigger(
            name=test_trigger_name,
            description="Test MCP trigger (auto-generated)",
            tool_instances=[{
                "instanceId": "disk-usage",
                "templateId": "disk-usage",
                "overrides": {
                    "name": "disk_usage",
                    "description": "Check disk usage on the devcontroller server",
                    "connection": "devcontroller",
                    "command": "df",
                    "argumentOverrides": {}
                }
            }]
        )

        if result.get('success'):
            print(f"   ✓ Successfully created trigger '{test_trigger_name}'")
            if result.get('url'):
                print(f"     - URL: {result['url']}")
            if result.get('apiToken'):
                print(f"     - Token: {result['apiToken']}")  # Full token for testing

            # Clean up - delete the test trigger
            print("   Cleaning up - deleting test trigger...")
            if client.delete_trigger(test_trigger_name):
                print("   ✓ Successfully deleted test trigger")
            else:
                print(f"   ⚠ Failed to delete test trigger '{test_trigger_name}'")
        elif result.get('error'):
            print(f"   ⚠ Failed to create: {result['error']}")
        else:
            print(f"   ⚠ Unexpected response: {result}")
    except Exception as e:
        print(f"   ✗ Failed: {e}")

    print("\n" + "=" * 50)
    print("Basic MCP tests completed successfully!")
    return True

if __name__ == "__main__":
    success = test_mcp_operations()
    sys.exit(0 if success else 1)
