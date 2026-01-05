#!/usr/bin/env python3
"""
Polymarket Token ID Fetcher

This script fetches the latest BTC 15-minute up/down token IDs
from Polymarket's Gamma API.
"""

import requests
import sys
import time
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional


def get_markets(search_term: Optional[str] = None, limit: int = 100, closed: bool = False) -> List[Dict[str, Any]]:
    """
    Fetch markets from Polymarket Gamma API.

    Args:
        search_term: Optional search term to filter markets
        limit: Maximum number of markets to fetch (default: 100)
        closed: Whether to include closed markets (default: False)

    Returns:
        list: List of market dictionaries

    Raises:
        requests.RequestException: If the API request fails
    """
    base_url = "https://gamma-api.polymarket.com/markets"

    params = {
        "limit": limit,
        "closed": str(closed).lower()  # Filter by closed status
    }

    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        markets = response.json()

        if search_term:
            # Filter markets by search term in question or slug
            markets = [
                m for m in markets
                if search_term.lower() in m.get('question', '').lower()
                or search_term.lower() in m.get('slug', '').lower()
            ]

        return markets
    except requests.RequestException as e:
        print(f"Error: Failed to fetch markets - {e}", file=sys.stderr)
        sys.exit(1)


def get_latest_15m_timestamp() -> int:
    """
    Get the Unix timestamp for the latest 15-minute mark.

    Returns:
        int: Unix timestamp rounded down to the nearest 15-minute interval
    """
    now = datetime.now(timezone.utc)

    # Round down to nearest 15 minutes
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

    print(f"Looking for market with slug: {slug}")
    print(f"Timestamp: {timestamp} ({datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')})")

    try:
        # Query by slug
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


def find_btc_15m_markets() -> List[Dict[str, Any]]:
    """
    Find the latest BTC 15-minute up/down market.

    Returns:
        list: List of matching markets
    """
    print("Calculating latest 15-minute interval...")

    markets_found = []

    # Try current 15-minute interval
    current_timestamp = get_latest_15m_timestamp()
    market = get_btc_15m_market_by_timestamp(current_timestamp)

    if market:
        markets_found.append(market)
    else:
        print(f"No market found for current interval.")
        print("Trying previous intervals...")

        # Try previous 15-minute intervals (up to 2 hours back)
        for i in range(1, 9):  # Check up to 8 intervals (2 hours)
            prev_timestamp = current_timestamp - (i * 15 * 60)
            print(f"\nTrying interval {i} ({datetime.fromtimestamp(prev_timestamp, tz=timezone.utc).strftime('%H:%M UTC')})...")
            market = get_btc_15m_market_by_timestamp(prev_timestamp)

            if market:
                markets_found.append(market)
                break

    return markets_found


def display_market_info(market: Dict[str, Any]) -> None:
    """
    Display detailed information about a market including token IDs.

    Args:
        market: Market dictionary from Gamma API
    """
    print("\n" + "="*60)
    print(f"Market: {market.get('question', 'N/A')}")
    print("="*60)

    print(f"\nSlug:           {market.get('slug', 'N/A')}")
    print(f"Market ID:      {market.get('id', 'N/A')}")
    print(f"Condition ID:   {market.get('conditionId', 'N/A')}")
    print(f"Active:         {market.get('active', 'N/A')}")
    print(f"Closed:         {market.get('closed', 'N/A')}")
    print(f"End Date:       {market.get('endDate', 'N/A')}")

    # Display tokens (outcomes)
    tokens = market.get('tokens', [])
    if tokens:
        print(f"\n{'─'*60}")
        print("Tokens (Outcomes):")
        print(f"{'─'*60}")

        for i, token in enumerate(tokens):
            outcome = token.get('outcome', 'Unknown')
            token_id = token.get('token_id', 'N/A')
            winner = token.get('winner', False)
            print(f"\n  Outcome {i+1}: {outcome}")
            print(f"  Token ID:  {token_id}")
            if winner:
                print(f"  Winner:    ✓")
    else:
        # Try alternative field names
        ctoken_id = market.get('clobTokenIds', [])
        if ctoken_id:
            print(f"\nCLOB Token IDs: {ctoken_id}")
        else:
            print("\nNo token information available")

    print("\n" + "="*60)


def main():
    """Main function to find and display BTC 15m token IDs."""
    print("="*60)
    print("BTC 15-Minute Up/Down Market Token ID Fetcher")
    print("="*60)
    print()

    btc_markets = find_btc_15m_markets()

    if not btc_markets:
        print("\n" + "!"*60)
        print("No BTC 15-minute up/down markets found")
        print("!"*60)
        print("\nThe market may not be active yet or the interval hasn't started.")
        print("Markets typically appear at the start of each 15-minute interval.")
        sys.exit(1)

    print(f"\n✓ Found {len(btc_markets)} BTC 15-minute market(s)\n")

    # Display the market(s)
    for market in btc_markets:
        display_market_info(market)


if __name__ == "__main__":
    main()
