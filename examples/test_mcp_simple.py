#!/usr/bin/env python3
"""
Simple MCP test - Create trigger with proper configuration and test it.
"""

import os
import sys
import json
import time
import argparse
from datetime import datetime
import random
import string
from dotenv import load_dotenv

# Add parent directory to path for development
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from opsbeacon import OpsBeaconClient

def generate_unique_name(prefix="simple-mcp"):
    """Generate a unique name using timestamp and random suffix."""
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
    return f"{prefix}-{timestamp}-{random_suffix}"

def main(args):
    load_dotenv()
    
    api_domain = os.getenv('OPSBEACON_API_DOMAIN', 'api.console-dev.opsbeacon.com')
    api_token = os.getenv('OPSBEACON_API_TOKEN')
    
    if not api_token:
        print("Error: OPSBEACON_API_TOKEN environment variable is required")
        sys.exit(1)
    
    # Enable debug mode if requested
    client = OpsBeaconClient(api_domain, api_token, debug=args.debug)
    
    print("Simple MCP Test with Policy Creation")
    print("=" * 50)
    
    # First create a policy for the specified command and connection
    policy_name = generate_unique_name("mcp-test-policy")
    print(f"\n1. Creating execution policy: {policy_name}")
    print(f"   This policy allows '{args.command}' command on '{args.connection}' connection")
    
    policy_result = client.create_policy(
        name=policy_name,
        description=f"Policy for MCP test - allows {args.command} command on {args.connection}",
        commands=[args.command],
        connections=[args.connection]
    )
    
    if 'error' in policy_result:
        print(f"   ✗ Failed to create policy: {policy_result['error']}")
        if 'details' in policy_result:
            print(f"   Details: {policy_result['details']}")
        sys.exit(1)
    
    print(f"   ✓ Policy created successfully!")
    
    # Create trigger with explicit configuration
    trigger_name = generate_unique_name("simple-mcp")
    print(f"\n2. Creating MCP trigger: {trigger_name}")
    
    tool_instances = [
        {
            "instanceId": "disk-usage",
            "templateId": "disk-usage",
            "overrides": {
                "name": "disk_usage",
                "description": f"Execute {args.command} on the {args.connection} server",
                "connection": args.connection,
                "command": args.command,
                "argumentOverrides": {}
            }
        }
    ]
    
    # Create with commands, connections, and policy explicitly set
    result = client.create_mcp_trigger(
        name=trigger_name,
        description="Simple test MCP trigger with disk_usage tool",
        tool_instances=tool_instances,
        policies=[policy_name]  # Include the policy we just created
    )
    
    if 'error' in result:
        print(f"   ✗ Failed to create trigger: {result['error']}")
        if 'details' in result:
            print(f"   Details: {result['details']}")
        sys.exit(1)
    
    print(f"   ✓ Created successfully!")
    
    mcp_url = result.get('url')
    mcp_token = result.get('apiToken')
    
    if not mcp_url or not mcp_token:
        print(f"   ✗ Missing URL or token in response")
        print(f"   Response: {json.dumps(result, indent=2)}")
        sys.exit(1)
    
    print(f"   URL: {mcp_url}")
    print(f"   Token: {mcp_token}")  # Full token for AI applications
    
    # Wait for propagation
    print(f"\n3. Waiting {args.wait_time} seconds for trigger to propagate...")
    time.sleep(args.wait_time)
    
    # Verify trigger exists
    print("\n4. Verifying trigger exists...")
    trigger = client.get_trigger(trigger_name)
    if trigger:
        print(f"   ✓ Trigger found: {trigger.get('name')}")
        print(f"   Commands: {trigger.get('commands', [])}")
        print(f"   Connections: {trigger.get('connections', [])}")
        print(f"   Policies: {trigger.get('policies', [])}")
    else:
        print(f"   ✗ Trigger not found!")
    
    # Test MCP protocol (unless skipped)
    test_result = {'success': False}
    if args.skip_test:
        print("\n5. Skipping MCP protocol test as requested")
        test_result = {'success': True, 'skipped': True}
    else:
        print("\n5. Testing MCP protocol...")
        test_result = client.test_mcp_protocol(mcp_url, mcp_token, tool_name="disk_usage")
    
    if test_result.get('success'):
        print("   ✓ MCP protocol test successful!")
        
        # Show execution result
        if test_result.get('execution') and 'result' in test_result['execution']:
            exec_result = test_result['execution']['result']
            if 'content' in exec_result:
                for content in exec_result.get('content', []):
                    if content.get('type') == 'text':
                        output = content['text']
                        lines = output.split('\n')
                        print(f"\n   Command output (first 5 lines):")
                        for line in lines[:5]:
                            print(f"     {line}")
                        if len(lines) > 5:
                            print(f"     ... ({len(lines) - 5} more lines)")
                        break
    else:
        print("   ✗ MCP protocol test failed!")
        
        # Show detailed error information
        if test_result.get('initialize', {}).get('error'):
            print(f"   Initialize error: {test_result['initialize']['error']}")
        
        if test_result.get('tools'):
            if 'error' in test_result['tools']:
                print(f"   Tools error: {test_result['tools']['error']}")
            elif 'result' in test_result['tools']:
                tools = test_result['tools']['result'].get('tools', [])
                print(f"   Tools found: {[t['name'] for t in tools]}")
        
        if test_result.get('execution'):
            if 'error' in test_result['execution']:
                exec_error = test_result['execution']['error']
                if isinstance(exec_error, dict):
                    print(f"   Execution error: {exec_error.get('message', exec_error)}")
                else:
                    print(f"   Execution error: {exec_error}")
            elif 'error' in test_result.get('execution', {}):
                print(f"   Execution response error: {test_result['execution']['error']}")
    
    # Clean up (unless --keep-resources is specified)
    if args.keep_resources:
        print("\n6. Keeping resources for analysis")
        print(f"   Policy: {policy_name}")
        print(f"   Trigger: {trigger_name}")
        print(f"\n   MCP Server Credentials:")
        print(f"   URL: {mcp_url}")
        print(f"   Token: {mcp_token}")
        
        print("\n   To clean up manually later:")
        print(f"   client.delete_trigger('{trigger_name}')")
        print(f"   client.delete_policy('{policy_name}')")
    else:
        print("\n6. Cleaning up...")
        
        # Delete trigger
        if not args.keep_trigger:
            if client.delete_trigger(trigger_name):
                print(f"   ✓ Deleted trigger '{trigger_name}'")
            else:
                print(f"   ✗ Failed to delete trigger '{trigger_name}'")
        else:
            print(f"   Keeping trigger '{trigger_name}' as requested")
        
        # Delete policy  
        if not args.keep_policy:
            if client.delete_policy(policy_name):
                print(f"   ✓ Deleted policy '{policy_name}'")
            else:
                print(f"   ✗ Failed to delete policy '{policy_name}'")
        else:
            print(f"   Keeping policy '{policy_name}' as requested")
    
    print("\n" + "=" * 50)
    if test_result.get('success'):
        print("✅ Test completed successfully!")
    else:
        print("❌ Test failed - check configuration")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Test MCP trigger creation with policy and protocol validation"
    )
    
    # Debug options
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode to show HTTP requests/responses'
    )
    parser.add_argument(
        '--no-debug',
        dest='debug',
        action='store_false',
        help='Disable debug output (default)'
    )
    parser.set_defaults(debug=True)  # Default to debug mode for testing
    
    # Resource management options
    parser.add_argument(
        '--keep-resources',
        action='store_true',
        help='Keep all created resources (policy and trigger) for analysis'
    )
    parser.add_argument(
        '--keep-trigger',
        action='store_true',
        help='Keep only the trigger after test'
    )
    parser.add_argument(
        '--keep-policy',
        action='store_true',
        help='Keep only the policy after test'
    )
    
    # Execution options
    parser.add_argument(
        '--skip-test',
        action='store_true',
        help='Skip MCP protocol test, only create resources'
    )
    parser.add_argument(
        '--wait-time',
        type=int,
        default=3,
        help='Time to wait for trigger propagation in seconds (default: 3)'
    )
    
    # Connection/command options
    parser.add_argument(
        '--connection',
        default='devcontroller',
        help='Connection name to use (default: devcontroller)'
    )
    parser.add_argument(
        '--command',
        default='df',
        help='Command to execute (default: df)'
    )
    
    args = parser.parse_args()
    
    # Handle the wait time in the main function
    if hasattr(args, 'wait_time'):
        # Store original wait time
        original_wait = args.wait_time
        
    main(args)