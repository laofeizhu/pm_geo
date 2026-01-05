#!/usr/bin/env python3
"""
Polymarket Geoblock Checker

This script checks if your current location is blocked from accessing Polymarket
by querying the Polymarket geoblock API endpoint and measures API latency.
"""

import requests
import sys
import time
import statistics
from typing import Dict, Any, List, Tuple


def check_geoblock() -> Tuple[Dict[str, Any], float]:
    """
    Check if the current location is blocked by Polymarket.

    Returns:
        tuple: (response_data, latency_ms) where:
            - response_data: Dict with blocked, ip, country, region
            - latency_ms: Roundtrip latency in milliseconds

    Raises:
        requests.RequestException: If the API request fails
    """
    endpoint = "https://polymarket.com/api/geoblock"

    try:
        start_time = time.perf_counter()
        response = requests.get(endpoint, timeout=10)
        end_time = time.perf_counter()

        response.raise_for_status()
        latency_ms = (end_time - start_time) * 1000
        return response.json(), latency_ms
    except requests.RequestException as e:
        print(f"Error: Failed to check geoblock status - {e}", file=sys.stderr)
        sys.exit(1)


def measure_latency(num_calls: int = 10) -> List[float]:
    """
    Measure API latency over multiple calls.

    Args:
        num_calls: Number of API calls to make (default: 10)

    Returns:
        list: List of latency measurements in milliseconds
    """
    endpoint = "https://polymarket.com/api/geoblock"
    latencies = []

    print(f"Measuring latency over {num_calls} calls...", end="", flush=True)

    for i in range(num_calls):
        try:
            start_time = time.perf_counter()
            response = requests.get(endpoint, timeout=10)
            end_time = time.perf_counter()

            response.raise_for_status()
            latency_ms = (end_time - start_time) * 1000
            latencies.append(latency_ms)

            print(".", end="", flush=True)
        except requests.RequestException as e:
            print(f"\nWarning: Call {i+1} failed - {e}", file=sys.stderr)
            continue

    print(" Done!\n")
    return latencies


def display_results(geo_data: Dict[str, Any], latencies: List[float]) -> None:
    """
    Display the geoblock check results in a formatted way.

    Args:
        geo_data: Dictionary containing geoblock information
        latencies: List of latency measurements in milliseconds
    """
    print("="*50)
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

    # Display latency statistics
    if latencies:
        median_latency = statistics.median(latencies)
        min_latency = min(latencies)
        max_latency = max(latencies)
        avg_latency = statistics.mean(latencies)

        print(f"\n{'─'*50}")
        print("Latency Measurements (ms)")
        print(f"{'─'*50}")
        print(f"  Calls:      {len(latencies)}")
        print(f"  Median:     {median_latency:.2f} ms")
        print(f"  Average:    {avg_latency:.2f} ms")
        print(f"  Min:        {min_latency:.2f} ms")
        print(f"  Max:        {max_latency:.2f} ms")

        print(f"\n  Individual measurements:")
        for i, lat in enumerate(latencies, 1):
            print(f"    Call {i:2d}:  {lat:7.2f} ms")

    print("="*50 + "\n")


def main():
    """Main function to run the geoblock checker."""
    print("Checking Polymarket geoblock status...\n")

    # Get initial geoblock status
    geo_data, _ = check_geoblock()

    # Measure latency over 20 calls
    latencies = measure_latency(num_calls=20)

    # Display results
    display_results(geo_data, latencies)

    # Exit with appropriate code
    sys.exit(1 if geo_data.get('blocked', False) else 0)


if __name__ == "__main__":
    main()
