#!/usr/bin/env python3
"""
Polymarket Token ID Fetcher

This script fetches the latest BTC 15-minute up/down token IDs
from Polymarket's Gamma API.
"""

import requests
import sys
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


def find_btc_15m_markets() -> List[Dict[str, Any]]:
    """
    Find BTC 15-minute up/down markets.

    Returns:
        list: List of matching markets
    """
    print("Fetching markets from Gamma API...")

    # First try to find markets with "15m" or "15 minute" in the name
    all_markets = get_markets(limit=500)

    # Filter for BTC/Bitcoin markets with 15m in the name
    btc_markets = []
    for market in all_markets:
        question = market.get('question', '').lower()
        slug = market.get('slug', '').lower()

        # Look for BTC + 15m/15 minute patterns
        has_btc = any(term in question or term in slug for term in ['btc', 'bitcoin'])
        has_15m = any(term in question or term in slug for term in ['15m', '15 minute', '15-minute', '15min'])

        if has_btc and has_15m:
            btc_markets.append(market)

    return btc_markets


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
    print("Searching for BTC 15-minute up/down markets...\n")

    btc_markets = find_btc_15m_markets()

    if not btc_markets:
        print("No BTC 15-minute markets found.")
        print("\nTrying broader search for any BTC markets (including closed)...")

        # Fallback: search for any BTC markets, including closed ones
        btc_markets = get_markets(search_term="btc", closed=True, limit=500)

        if not btc_markets:
            print("No BTC markets found at all.")
            print("\nFetching sample of recent markets to show structure...")
            sample_markets = get_markets(limit=3, closed=False)
            if sample_markets:
                print(f"\nShowing {len(sample_markets)} sample market(s) for reference:")
                for market in sample_markets:
                    display_market_info(market)
            sys.exit(1)
        else:
            print(f"\nFound {len(btc_markets)} BTC-related markets")

            # Filter for ones with token information
            markets_with_tokens = [m for m in btc_markets if m.get('tokens') or m.get('clobTokenIds')]
            if markets_with_tokens:
                print(f"{len(markets_with_tokens)} of them have token information")
                btc_markets = markets_with_tokens
    else:
        print(f"Found {len(btc_markets)} BTC 15-minute market(s)\n")

    # Display all matching markets
    for market in btc_markets[:5]:  # Limit to first 5 for readability
        display_market_info(market)

    if len(btc_markets) > 5:
        print(f"\n... and {len(btc_markets) - 5} more market(s)")


if __name__ == "__main__":
    main()
