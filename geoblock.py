#!/usr/bin/env python3
"""
Polymarket Geoblock Checker

This script checks if your current location is blocked from accessing Polymarket
by querying the Polymarket geoblock API endpoint.
"""

import requests
import sys
from typing import Dict, Any


def check_geoblock() -> Dict[str, Any]:
    """
    Check if the current location is blocked by Polymarket.

    Returns:
        dict: Response from the Polymarket geoblock API containing:
            - blocked (bool): Whether the location is blocked
            - ip (str): The IP address being checked
            - country (str): The detected country
            - region (str): The detected region

    Raises:
        requests.RequestException: If the API request fails
    """
    endpoint = "https://polymarket.com/api/geoblock"

    try:
        response = requests.get(endpoint, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error: Failed to check geoblock status - {e}", file=sys.stderr)
        sys.exit(1)


def display_results(geo_data: Dict[str, Any]) -> None:
    """
    Display the geoblock check results in a formatted way.

    Args:
        geo_data: Dictionary containing geoblock information
    """
    print("\n" + "="*50)
    print("Polymarket Geoblock Check Results")
    print("="*50)

    blocked = geo_data.get('blocked', False)
    ip = geo_data.get('ip', 'Unknown')
    country = geo_data.get('country', 'Unknown')
    region = geo_data.get('region', 'Unknown')

    print(f"\nIP Address:  {ip}")
    print(f"Country:     {country}")
    print(f"Region:      {region}")
    print(f"\nStatus:      ", end="")

    if blocked:
        print("🚫 BLOCKED")
        print("\nYour location is restricted from accessing Polymarket.")
        print("This may be due to regulatory requirements or compliance")
        print("with international sanctions.")
    else:
        print("✓ ALLOWED")
        print("\nYour location can access Polymarket!")

    print("="*50 + "\n")


def main():
    """Main function to run the geoblock checker."""
    print("Checking Polymarket geoblock status...")

    geo_data = check_geoblock()
    display_results(geo_data)

    # Exit with appropriate code
    sys.exit(1 if geo_data.get('blocked', False) else 0)


if __name__ == "__main__":
    main()
