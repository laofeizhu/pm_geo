#!/usr/bin/env python3
"""
Polymarket CLOB Client Latency Test

This script measures API latency using the official py-clob-client library
for the Polymarket CLOB price endpoint.
"""

import sys
import time
import json
import statistics
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

import requests
from py_clob_client.client import ClobClient


def get_latest_15m_timestamp() -> int:
    """
    Get the Unix timestamp for the latest 15-minute mark.

    Returns:
        int: Unix timestamp rounded down to the nearest 15-minute interval
    """
    now = datetime.now(timezone.utc)
    minutes = (now.minute // 15) * 15
    rounded_time = now.replace(minute=minutes, second=0, microsecond=0)
    return int(rounded_time.timestamp())


def get_btc_15m_market_by_timestamp(timestamp: int) -> Optional[Dict[str, Any]]:
    """
    Get a specific BTC 15m up/down market by timestamp.

    Args:
        timestamp: Unix timestamp for the 15-minute interval

    Returns:
        dict: Market information or None if not found
    """
    slug = f"btc-updown-15m-{timestamp}"

    try:
        base_url = "https://gamma-api.polymarket.com/markets"
        params = {"slug": slug}
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        markets = response.json()

        if markets and len(markets) > 0:
            return markets[0]
        return None
    except requests.RequestException as e:
        print(f"Error querying market: {e}", file=sys.stderr)
        return None


def find_latest_btc_market() -> Optional[Dict[str, Any]]:
    """
    Find the latest BTC 15-minute up/down market.

    Returns:
        dict: Market information or None if not found
    """
    current_timestamp = get_latest_15m_timestamp()
    market = get_btc_15m_market_by_timestamp(current_timestamp)

    if market:
        return market

    # Try previous intervals
    for i in range(1, 9):
        prev_timestamp = current_timestamp - (i * 15 * 60)
        market = get_btc_15m_market_by_timestamp(prev_timestamp)
        if market:
            return market

    return None


def get_up_token_id(market: Dict[str, Any]) -> Optional[str]:
    """
    Extract the "Up" token ID from a market.

    Args:
        market: Market dictionary

    Returns:
        str: The token ID for the "Up" outcome, or None if not found
    """
    tokens = market.get('tokens', [])

    if tokens:
        for token in tokens:
            outcome = token.get('outcome', '').lower()
            if 'yes' in outcome or 'up' in outcome:
                return token.get('token_id')
        if tokens:
            return tokens[0].get('token_id')

    clob_token_ids = market.get('clobTokenIds')
    if clob_token_ids:
        if isinstance(clob_token_ids, str):
            try:
                clob_token_ids = json.loads(clob_token_ids)
            except json.JSONDecodeError:
                return None

        if isinstance(clob_token_ids, list) and len(clob_token_ids) > 0:
            return clob_token_ids[0]

    return None


def measure_clob_client_latency(client: ClobClient, token_id: str, num_calls: int = 20) -> List[float]:
    """
    Measure CLOB client price API latency over multiple calls.

    Args:
        client: ClobClient instance
        token_id: The token ID to query
        num_calls: Number of API calls to make (default: 20)

    Returns:
        list: List of latency measurements in milliseconds
    """
    latencies = []

    print(f"Measuring CLOB client latency over {num_calls} calls...", end="", flush=True)

    for i in range(num_calls):
        try:
            start_time = time.perf_counter()
            price = client.get_price(token_id, side="BUY")
            end_time = time.perf_counter()

            latency_ms = (end_time - start_time) * 1000
            latencies.append(latency_ms)

            print(".", end="", flush=True)
        except Exception as e:
            print(f"\nWarning: Call {i+1} failed - {e}", file=sys.stderr)
            continue

    print(" Done!\n")
    return latencies


def measure_binance_latency(num_calls: int = 20) -> List[float]:
    """
    Measure Binance API latency over multiple calls.

    Args:
        num_calls: Number of API calls to make (default: 20)

    Returns:
        list: List of latency measurements in milliseconds
    """
    endpoint = "https://api.binance.com/api/v3/ping"
    latencies = []

    print(f"Measuring Binance API latency over {num_calls} calls...", end="", flush=True)

    with requests.Session() as session:
        for i in range(num_calls):
            try:
                start_time = time.perf_counter()
                response = session.get(endpoint, timeout=10)
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


def display_results(market: Dict[str, Any], token_id: str,
                   clob_latencies: List[float], binance_latencies: List[float]) -> None:
    """
    Display latency test results.

    Args:
        market: Market information
        token_id: The Up token ID
        clob_latencies: CLOB client latency measurements
        binance_latencies: Binance latency measurements
    """
    print("="*60)
    print("CLOB Client Latency Test Results")
    print("="*60)

    print(f"\nMarket:      {market.get('question', 'N/A')}")
    print(f"Slug:        {market.get('slug', 'N/A')}")
    print(f"Up Token ID: {token_id[:20]}...{token_id[-20:]}")

    print(f"\n{'─'*60}")
    print("Latency Measurements (ms)")
    print(f"{'─'*60}")

    if clob_latencies:
        print(f"\nPolymarket CLOB Client (py-clob-client):")
        print(f"  Calls:      {len(clob_latencies)}")
        print(f"  Median:     {statistics.median(clob_latencies):.2f} ms")
        print(f"  Average:    {statistics.mean(clob_latencies):.2f} ms")
        print(f"  Min:        {min(clob_latencies):.2f} ms")
        print(f"  Max:        {max(clob_latencies):.2f} ms")

    if binance_latencies:
        print(f"\nBinance API:")
        print(f"  Calls:      {len(binance_latencies)}")
        print(f"  Median:     {statistics.median(binance_latencies):.2f} ms")
        print(f"  Average:    {statistics.mean(binance_latencies):.2f} ms")
        print(f"  Min:        {min(binance_latencies):.2f} ms")
        print(f"  Max:        {max(binance_latencies):.2f} ms")

    print("="*60 + "\n")


def main():
    """Main function to run latency tests."""
    print("="*60)
    print("Polymarket CLOB Client Latency Test")
    print("="*60)
    print()

    # Find latest BTC 15m market
    print("Finding latest BTC 15-minute market...")
    market = find_latest_btc_market()

    if not market:
        print("Error: Could not find BTC 15-minute market")
        sys.exit(1)

    print(f"✓ Found: {market.get('question', 'N/A')}\n")

    # Get Up token ID
    token_id = get_up_token_id(market)
    if not token_id:
        print("Error: Could not extract Up token ID")
        sys.exit(1)

    print(f"Up Token ID: {token_id}\n")

    # Initialize CLOB client
    print("Initializing CLOB client...")
    host = "https://clob.polymarket.com"
    client = ClobClient(host=host)
    print("✓ Client initialized\n")

    # Measure CLOB client latency
    clob_latencies = measure_clob_client_latency(client, token_id, num_calls=20)

    # Measure Binance API latency
    binance_latencies = measure_binance_latency(num_calls=20)

    # Display results
    display_results(market, token_id, clob_latencies, binance_latencies)


if __name__ == "__main__":
    main()
