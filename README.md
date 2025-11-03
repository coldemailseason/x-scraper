# X Followers Scraper

A Python tool for scraping X followers using the twscrape library. This repository contains two main scripts: `get_followers.py` for scraping follower data and `add_account.py` for managing X accounts.

## Features

- **Follower Scraping**: Extract detailed follower information from X profiles
- **Multiple Output Formats**: Save data as JSON (structured) and CSV (spreadsheet-friendly)
- **Batch Processing**: Scrape multiple accounts simultaneously
- **Rate Limit Handling**: Automatic rate limit management via twscrape
- **Proxy Support**: Optional proxy configuration for enhanced privacy
- **Account Management**: Add and manage X accounts with cookie authentication

## Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/coldemailseason/x-scraper.git
   cd x-scraper
   ```

2. **Install uv**:

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. **Install dependencies**:

   ```bash
   uv sync
   ```

4. **Activate virtual environment**:

   ```bash
   source .venv/bin/activate
   ```

5. **Python Requirements**:
   - Python 3.12+
   - twscrape >= 0.17.0

## Setup

### 1. Add X Accounts

Before scraping, you need to add X accounts to the twscrape pool:

```bash
python add_account.py
```

This will read from `accounts.txt` with the format:

```
username:auth_token:ct0
```

#### How to Get Cookies

1. Purchase X accounts credentials with an auth_token included
2. Open a browser
3. Download the EditThisCookie(V3) extension
4. Navigate to https://x.com
5. Open the extension, clear all cookies
6. Click the plus (+) icon, set the name to 'auth_token' and the value to the token provided in the credentials
7. Reload the page. You should now be logged in.
8. Re-open the EditThisCookie extension. Extract the 'auth_token' and the 'ct0' tokens
9. Save them to your 'accounts.txt' file in this format: username:auth_token:ct0
10. Repeat for all credentials
11. Run the add_account.py script.

### 2. Configure Proxy (Optional)

Edit the `PROXY` variable in `get_followers.py`:

```python
PROXY = "http://user:pass@domain:port"
```

## Usage

### Basic Usage

Get all followers from a single account:

```bash
python get_followers.py elonmusk
```

### Advanced Options

```bash
# Get specific number of followers
python get_followers.py elonmusk --limit 500

# Add timestamp to prevent overwriting files
python get_followers.py elonmusk --timestamp

# Multiple accounts
python get_followers.py elonmusk BillGates BarackObama --limit 1000 --timestamp

# Use proxy
python get_followers.py elonmusk --proxy
```

### Command Line Flags

- `--limit, -l`: Number of followers to fetch (default: 100, use 0 for unlimited)
- `--timestamp, -t`: Add timestamp to output filenames
- `--proxy, -p`: Use configured proxy

## Output Files

For each target user:

- `followers_USERNAME.json` - Detailed follower data
- `followers_USERNAME.csv` - Same data in spreadsheet format

For multiple targets:

- `followers_summary.csv` - Statistics for all processed accounts

## Important Notes

⚠️ **Legal Disclaimer**:

- This tool is for educational and research purposes only
- Respect X's Terms of Service and robots.txt
- Do not use for harassment, spam, or unauthorized data collection
- Rate limits apply - large accounts may take significant time
- X may suspend accounts that violate their policies

## Troubleshooting

- **Account not active**: Ensure you have both `auth_token` and `ct0` cookies
- **Rate limits**: twscrape handles this automatically, but large requests may take time
- **Cookie expiration**: Refresh cookies periodically
- **Proxy issues**: Verify proxy format and credentials

## Dependencies

- twscrape: Twitter scraping library
- asyncio: Asynchronous operations
- argparse: Command line interface
- csv/json: Data export formats

---

**Note**: This tool requires valid X accounts and cookies. Use responsibly and in accordance with X's terms of service.</content>
