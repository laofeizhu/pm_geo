# Polymarket Geo Checker (pm_geo)

A Python utility to check if your current machine/location is banned from accessing Polymarket and measure API latency.

## Purpose

This tool helps you:
1. **Check geo-restrictions**: Determine if your current location is blocked from accessing Polymarket
2. **Measure latency**: Find machines with the lowest latency to Polymarket's API endpoints
3. **Multi-region testing**: Useful for testing access across different geographic regions and cloud providers

## Features

- Real-time geolocation blocking status check
- IP address, country, and region detection
- Clear visual feedback (blocked/allowed status)
- Exit codes for scripting (0 = allowed, 1 = blocked)
- Built with UV for fast, modern Python dependency management

## Installation

This project uses [UV](https://github.com/astral-sh/uv) for dependency management.

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/pm_geo.git
cd pm_geo

# Install dependencies (UV will handle everything)
uv sync
```

## Usage

Run the geoblock checker:

```bash
uv run geoblock.py
```

### Example Output

```
Checking Polymarket geoblock status...

==================================================
Polymarket Geoblock Check Results
==================================================

IP Address:  52.19.85.35
Country:     IE
Region:      L

Status:      ✓ ALLOWED

Your location can access Polymarket!
==================================================
```

## Use Cases

### 1. Check if Your Region is Blocked

Quickly verify if your current location has access to Polymarket:
```bash
uv run geoblock.py
```

### 2. Multi-Region Cloud Testing

Deploy this script across different cloud regions (AWS, GCP, Azure) to find:
- Which regions have access to Polymarket
- Which regions have the lowest latency

### 3. Automated Monitoring

Use the exit codes in scripts:
```bash
if uv run geoblock.py; then
    echo "Access allowed - proceeding with operations"
else
    echo "Access blocked - switching to allowed region"
fi
```

## API Endpoint

This tool uses Polymarket's official geoblock API:
- **Endpoint**: `https://polymarket.com/api/geoblock`
- **Method**: GET
- **Response**: JSON with `blocked`, `ip`, `country`, `region` fields

## Blocked Regions (as of 2026)

Polymarket currently restricts access from:
- United States
- France, Belgium, Poland, Switzerland
- United Kingdom
- Singapore, Thailand, Taiwan
- Australia
- Ontario, Canada
- Romania
- US-sanctioned territories (Iran, Cuba, North Korea)

## Roadmap

- [ ] Add latency measurement functionality
- [ ] Multi-endpoint latency comparison
- [ ] CSV/JSON export of results
- [ ] Continuous monitoring mode
- [ ] Integration with cloud provider APIs for automated region testing

## Requirements

- Python 3.9+
- UV package manager
- Internet connection

## License

MIT

## Disclaimer

This tool is for testing and informational purposes only. Always comply with Polymarket's Terms of Service and applicable regulations in your jurisdiction.
