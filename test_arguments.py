#!/usr/bin/env python3
"""
Test script to demonstrate the new array arguments functionality in the OpsBeacon SDK.
"""

import os
import sys

from dotenv import load_dotenv

from opsbeacon import OpsBeaconClient

# Load environment variables from .env file
load_dotenv()

# Get API credentials from environment variables
api_domain = os.environ.get("OPSBEACON_API_DOMAIN")
api_token = os.environ.get("OPSBEACON_API_TOKEN")

if not api_domain or not api_token:
    print("Error: API domain and token must be set in environment variables or .env file")
    print("Set OPSBEACON_API_DOMAIN and OPSBEACON_API_TOKEN")
    sys.exit(1)

# Initialize the client
client = OpsBeaconClient(api_domain=api_domain, api_token=api_token)

# Test with string arguments (backward compatibility)
print("Testing with string arguments (backward compatibility):")
try:
    result = client.run(
        command="df",
        connection="ob",
        args="--human-readable",
        debug=True
    )
    print(f"Result: {result}")
except Exception as e:
    print(f"Error with string arguments: {e}")

print("\n" + "-" * 50 + "\n")

# Test with array arguments (new format)
print("Testing with array arguments (new format):")
try:
    result = client.run(
        command="df",
        connection="ob",
        args=["--human-readable", "--total"],
        debug=True
    )
    print(f"Result: {result}")
except Exception as e:
    print(f"Error with array arguments: {e}")
