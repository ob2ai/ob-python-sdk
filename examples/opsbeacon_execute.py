#!/usr/bin/env python3
"""
Generic OpsBeacon command execution tool
Usage: python opsbeacon_execute.py --connection <connection> --command <command> [--args <arguments>]
"""

import argparse
import os
import sys
import json
from pathlib import Path
from opsbeacon import OpsBeaconClient

# Try to load .env file
try:
    from dotenv import load_dotenv
    env_path = Path('.') / '.env'
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    # dotenv not installed, will use system environment variables only
    pass


def main():
    parser = argparse.ArgumentParser(
        description="Execute commands on OpsBeacon connections",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python opsbeacon_execute.py --connection ob --command nvd-cpe-ecs-task
  python opsbeacon_execute.py --connection server1 --command restart-service --args --service nginx
  python opsbeacon_execute.py --connection server1 --command restart-service --args "--service" "nginx" "--timeout" "30"
  python opsbeacon_execute.py --command-line "ob run nvd-cpe-ecs-task"
        """
    )
    
    # Authentication arguments
    parser.add_argument(
        "--api-domain",
        default=os.environ.get("OPSBEACON_API_DOMAIN"),
        help="OpsBeacon API domain (or set OPSBEACON_API_DOMAIN env var)"
    )
    parser.add_argument(
        "--api-token",
        default=os.environ.get("OPSBEACON_API_TOKEN"),
        help="OpsBeacon API token (or set OPSBEACON_API_TOKEN env var)"
    )
    
    # Command execution arguments
    parser.add_argument(
        "--command-line",
        help="Full command line text to execute"
    )
    
    # Or structured command
    parser.add_argument(
        "--connection",
        help="Connection identifier"
    )
    parser.add_argument(
        "--command",
        help="Command name to execute"
    )
    parser.add_argument(
        "--args",
        nargs="*",  # Accept multiple arguments
        default=[],
        help="Arguments to pass to the command (multiple arguments can be provided)"
    )
    
    # Output options
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output raw JSON response"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress informational output"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug output"
    )
    
    args = parser.parse_args()
    
    # Validate authentication
    if not args.api_domain:
        print("Error: API domain not provided. Use --api-domain or set OPSBEACON_API_DOMAIN environment variable", file=sys.stderr)
        sys.exit(1)
    
    if not args.api_token:
        print("Error: API token not provided. Use --api-token or set OPSBEACON_API_TOKEN environment variable", file=sys.stderr)
        sys.exit(1)
    
    # Validate command arguments
    if not args.command_line and (not args.connection or not args.command):
        print("Error: Either --command-line or both --connection and --command must be provided", file=sys.stderr)
        sys.exit(1)
    
    # Initialize client
    client = OpsBeaconClient(api_domain=args.api_domain, api_token=args.api_token)
    
    # Execute command
    try:
        if not args.quiet:
            if args.command_line:
                print(f"Executing command line: {args.command_line}")
            else:
                print(f"Executing command '{args.command}' on connection '{args.connection}'")
                if args.args:
                    print(f"Arguments: {args.args}")
        
        if args.debug:
            print(f"\nDebug: API Domain: {args.api_domain}")
            print(f"Debug: API Token: {'*' * 10 + args.api_token[-4:] if len(args.api_token) > 4 else '***'}")
            print(f"Debug: Request details:")
            if args.command_line:
                print(f"  - Command line: {args.command_line}")
            else:
                print(f"  - Command: {args.command}")
                print(f"  - Connection: {args.connection}")
                print(f"  - Args: {args.args}")
        
        if args.command_line:
            result = client.run(command_text=args.command_line, debug=args.debug)
        else:
            result = client.run(
                command=args.command,
                connection=args.connection,
                args=args.args,
                debug=args.debug
            )
        
        if args.debug:
            print(f"\nDebug: Raw response: {result}")
            print(f"Debug: Response type: {type(result)}")
        
        # Handle response
        if "error" in result:
            print(f"Error: {result['error']}", file=sys.stderr)
            sys.exit(1)
        
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            # Pretty print the result
            if not args.quiet:
                print("\nExecution Result:")
                print("-" * 50)
            
            if isinstance(result, dict):
                for key, value in result.items():
                    if key == "output" and isinstance(value, str):
                        print(f"{key}:\n{value}")
                    else:
                        print(f"{key}: {value}")
            else:
                print(result)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
