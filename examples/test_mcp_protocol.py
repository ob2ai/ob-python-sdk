#!/usr/bin/env python3
"""
Test MCP protocol directly - Initialize, list tools, and execute a command.
This script creates an MCP trigger and then tests it using the MCP protocol.
"""

import os
import sys
import json
import requests
from datetime import datetime
import random
import string
from dotenv import load_dotenv

# Add parent directory to path for development
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from opsbeacon import OpsBeaconClient

def generate_unique_name(prefix="test-mcp-protocol"):
    """Generate a unique name using timestamp and random suffix."""
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
    return f"{prefix}-{timestamp}-{random_suffix}"

def test_mcp_protocol(mcp_url, api_token):
    """Test MCP protocol operations - initialize, list tools, and execute."""
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    
    print("\n" + "=" * 50)
    print("Testing MCP Protocol")
    print("=" * 50)
    
    # 1. Initialize
    print("\n1. Sending initialize request...")
    init_request = {
        "jsonrpc": "2.0",
        "method": "initialize",
        "params": {
            "protocolVersion": "0.1.0",
            "capabilities": {},
            "clientInfo": {
                "name": "OpsBeacon Python SDK Test",
                "version": "1.0.0"
            }
        },
        "id": 1
    }
    
    try:
        response = requests.post(mcp_url, json=init_request, headers=headers)
        response.raise_for_status()
        result = response.json()
        print(f"   ✓ Initialize response: {json.dumps(result, indent=2)}")
    except Exception as e:
        print(f"   ✗ Initialize failed: {e}")
        return False
    
    # 2. List tools
    print("\n2. Sending tools/list request...")
    list_request = {
        "jsonrpc": "2.0",
        "method": "tools/list",
        "params": {},
        "id": 2
    }
    
    tools = []
    try:
        response = requests.post(mcp_url, json=list_request, headers=headers)
        response.raise_for_status()
        result = response.json()
        print(f"   ✓ Tools list response received")
        
        if 'result' in result and 'tools' in result['result']:
            tools = result['result']['tools']
            print(f"   Found {len(tools)} tools:")
            for tool in tools:
                print(f"     - {tool['name']}: {tool.get('description', 'No description')}")
        else:
            print("   No tools found in response")
    except Exception as e:
        print(f"   ✗ List tools failed: {e}")
        return False
    
    # 3. Execute the disk_usage tool
    if tools:
        # Find the disk_usage tool specifically
        disk_usage_tool = None
        for tool in tools:
            if tool['name'] == 'disk_usage':
                disk_usage_tool = tool
                break
        
        if not disk_usage_tool:
            print("\n3. ✗ 'disk_usage' tool not found!")
            print(f"   Available tools: {[t['name'] for t in tools]}")
            return False
        
        print(f"\n3. Executing tool 'disk_usage'...")
        
        # Build the execution request
        exec_request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "disk_usage",
                "arguments": {}  # Empty arguments for df command
            },
            "id": 3
        }
        
        try:
            response = requests.post(mcp_url, json=exec_request, headers=headers)
            response.raise_for_status()
            result = response.json()
            
            if 'result' in result:
                print(f"   ✓ Tool executed successfully!")
                if 'content' in result['result']:
                    for content in result['result']['content']:
                        if content.get('type') == 'text':
                            print(f"\n   Output:\n{content['text'][:500]}...")  # Show first 500 chars
                else:
                    print(f"   Result: {json.dumps(result['result'], indent=2)}")
            elif 'error' in result:
                print(f"   ✗ Execution error: {result['error']}")
            else:
                print(f"   Response: {json.dumps(result, indent=2)}")
        except Exception as e:
            print(f"   ✗ Tool execution failed: {e}")
            if hasattr(e, 'response'):
                print(f"   Response: {e.response.text}")
            return False
    else:
        print("\n3. No tools available to execute")
    
    return True

def main():
    """Create an MCP trigger and test it with the MCP protocol."""
    load_dotenv()
    
    api_domain = os.getenv('OPSBEACON_API_DOMAIN', 'api.console-dev.opsbeacon.com')
    api_token = os.getenv('OPSBEACON_API_TOKEN')
    
    if not api_token:
        print("Error: OPSBEACON_API_TOKEN environment variable is required")
        sys.exit(1)
    
    client = OpsBeaconClient(api_domain, api_token)
    
    print("MCP Protocol Test")
    print("=" * 50)
    
    # Create an MCP trigger with df command on devcontroller
    trigger_name = generate_unique_name("mcp-protocol-test")
    print(f"\n1. Creating MCP trigger: {trigger_name}")
    
    # Single tool configuration for disk_usage on devcontroller
    tool_instances = [
        {
            "instanceId": "disk-usage",
            "templateId": "disk-usage",
            "overrides": {
                "name": "disk_usage",  # Simple name for testing
                "description": "Check disk usage on the devcontroller server",
                "connection": "devcontroller",  # Using devcontroller for dev environment
                "command": "df",
                "argumentOverrides": {}
            }
        }
    ]
    
    result = client.create_mcp_trigger(
        name=trigger_name,
        description="Test MCP trigger for protocol validation",
        tool_instances=tool_instances
    )
    
    if 'error' in result:
        print(f"   ✗ Failed to create trigger: {result['error']}")
        sys.exit(1)
    
    if not result.get('url') or not result.get('apiToken'):
        print(f"   ✗ Missing URL or API token in response: {result}")
        sys.exit(1)
    
    mcp_url = result['url']
    mcp_token = result['apiToken']
    
    print(f"   ✓ Trigger created successfully!")
    print(f"   URL: {mcp_url}")
    print(f"   Token: {mcp_token[:8]}...")
    
    # Test the MCP protocol
    success = test_mcp_protocol(mcp_url, mcp_token)
    
    # Clean up
    print("\n" + "=" * 50)
    print("Cleaning up...")
    if client.delete_trigger(trigger_name):
        print(f"✓ Deleted trigger '{trigger_name}'")
    else:
        print(f"✗ Failed to delete trigger '{trigger_name}'")
    
    if success:
        print("\n✅ MCP Protocol test completed successfully!")
    else:
        print("\n❌ MCP Protocol test failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()