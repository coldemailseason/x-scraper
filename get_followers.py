"""
Twitter Followers Scraper

This script fetches followers from Twitter/X profiles using twscrape.

USAGE EXAMPLES:
---------------

1. Basic usage - single target, ALL followers (default), overwrite mode:
   python get_followers.py elonmusk

2. Get ALL followers with timestamp:
   python get_followers.py elonmusk --timestamp
   python get_followers.py elonmusk -t

3. Get specific number of followers:
   python get_followers.py elonmusk --limit 500
   python get_followers.py elonmusk -l 500

4. Multiple targets with timestamp:
   python get_followers.py elonmusk BillGates BarackObama --timestamp
   python get_followers.py elonmusk BillGates BarackObama -t

5. Multiple targets, 1000 followers each, with timestamp:
   python get_followers.py user1 user2 user3 --limit 1000 --timestamp

6. Using proxy (set PROXY variable below first):
   python get_followers.py elonmusk --proxy
   python get_followers.py elonmusk -l 500 -t -p

FLAGS:
------
--limit, -l    : Number of followers to fetch (default: 0 = ALL followers)
                 Use 0 for unlimited, or specify a number like 500

--timestamp, -t: Add timestamp to output filenames
                 Without: followers_USERNAME.json (overwrites)
                 With: followers_USERNAME_20251102_213045.json (never overwrites)

--proxy, -p    : Use proxy (set PROXY variable in script first)
                 Format: http://user:pass@domain:port

OUTPUT FILES:
-------------
For each target user:
  - followers_USERNAME[_TIMESTAMP].json  (detailed data)
  - followers_USERNAME[_TIMESTAMP].csv   (same data, spreadsheet format)

For multiple targets:
  - followers_summary[_TIMESTAMP].csv    (stats for all targets)

NOTES:
------
- Requires accounts in accounts.db (use add_account.py first)
- Rate limits are handled automatically by twscrape
- Default fetches ALL followers (limit=0) - may take hours for large accounts
- Large accounts with millions of followers will hit rate limits quickly
- Consider using -l flag to limit results for testing
"""

import argparse
import asyncio
import csv
import json
from datetime import datetime

from twscrape import API, gather

# =============================================================================
# PROXY CONFIGURATION
# =============================================================================
# Set your proxy here in the format: http://user:pass@domain:port
# Leave as None to not use proxy
PROXY = None  # Example: "http://myuser:mypass@proxy.example.com:8080"
# =============================================================================


async def get_followers(username, limit=0, use_timestamp=False, use_proxy=False):
    """
    Get followers from a target Twitter profile

    Args:
        username: Twitter username (without @)
        limit: Maximum number of followers to fetch (0 or -1 = unlimited)
        use_timestamp: Add timestamp to filename
        use_proxy: Use proxy if configured

    Returns:
        dict with follower data and metadata
    """

    # Initialize API with or without proxy
    proxy = PROXY if use_proxy else None
    api = API(proxy=proxy) if proxy else API()

    print(f"\n{'=' * 60}")
    print(f"Getting followers for: @{username}")
    print(f"Limit: {'ALL (unlimited)' if limit <= 0 else limit}")
    if proxy:
        # Hide credentials in output
        proxy_display = proxy.split("@")[1] if "@" in proxy else proxy
        print(f"Proxy: {proxy_display}")
    print(f"{'=' * 60}\n")

    try:
        # First, get the user to verify they exist
        print("Looking up user...")
        user = await api.user_by_login(username)
        print(f"✓ Found: {user.displayname} (@{user.username})")
        print(f"  Total followers: {user.followersCount:,}")
        print(f"  Following: {user.friendsCount:,}")
        print(f"  Tweets: {user.statusesCount:,}\n")

        # Get followers (None = unlimited)
        fetch_limit = None if limit <= 0 else limit
        print("Fetching followers...\n")

        followers = await gather(api.followers(user.id, limit=fetch_limit))

        print(f"\n✓ Retrieved {len(followers)} followers\n")

        # Process followers
        results = []
        for i, follower in enumerate(followers, 1):
            follower_data = {
                "rank": i,
                "username": follower.username,
                "display_name": follower.displayname,
                "user_id": follower.id,
                "followers": follower.followersCount,
                "following": follower.friendsCount,
                "tweets": follower.statusesCount,
                "verified": getattr(follower, "verified", False),
                "created_at": str(getattr(follower, "created", "N/A")),
                "description": getattr(follower, "rawDescription", ""),
            }
            results.append(follower_data)

            # Print progress every 10 followers
            if i % 10 == 0 or i == len(followers):
                print(f"Processed: {i}/{len(followers)} followers", end="\r")

        print()  # New line after progress

        # Generate filename with optional timestamp
        timestamp_str = (
            f"_{datetime.now().strftime('%Y%m%d_%H%M%S')}" if use_timestamp else ""
        )
        base_filename = f"followers_{username}{timestamp_str}"

        # Prepare output data
        output_data = {
            "target_user": username,
            "target_display_name": user.displayname,
            "target_followers_total": user.followersCount,
            "fetched_count": len(followers),
            "fetched_at": datetime.now().isoformat(),
            "followers": results,
        }

        # Save JSON
        json_file = f"{base_filename}.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        print(f"✓ JSON saved to: {json_file}")

        # Save CSV
        csv_file = f"{base_filename}.csv"
        if results:
            with open(csv_file, "w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=results[0].keys())
                writer.writeheader()
                writer.writerows(results)
            print(f"✓ CSV saved to: {csv_file}")

        return {
            "username": username,
            "display_name": user.displayname,
            "total_followers": user.followersCount,
            "fetched_count": len(followers),
            "timestamp": datetime.now().isoformat(),
            "status": "success",
            "json_file": json_file,
            "csv_file": csv_file,
        }

    except Exception as e:
        print(f"✗ ERROR: {e}")
        import traceback

        traceback.print_exc()

        return {
            "username": username,
            "display_name": "N/A",
            "total_followers": 0,
            "fetched_count": 0,
            "timestamp": datetime.now().isoformat(),
            "status": f"error: {str(e)}",
            "json_file": None,
            "csv_file": None,
        }


async def get_followers_multiple(
    usernames, limit=0, use_timestamp=False, use_proxy=False
):
    """
    Get followers from multiple target profiles

    Args:
        usernames: List of Twitter usernames
        limit: Max followers to fetch per user (0 = unlimited)
        use_timestamp: Add timestamp to filenames
        use_proxy: Use proxy if configured

    Returns:
        List of result dictionaries
    """

    all_results = []

    for i, username in enumerate(usernames, 1):
        print(f"\n{'#' * 60}")
        print(f"# Processing {i}/{len(usernames)}: @{username}")
        print(f"{'#' * 60}")

        result = await get_followers(
            username, limit=limit, use_timestamp=use_timestamp, use_proxy=use_proxy
        )
        all_results.append(result)

        # Small delay between users to be respectful
        if i < len(usernames):
            print("\nWaiting 2 seconds before next user...")
            await asyncio.sleep(2)

    # Create summary file
    timestamp_str = (
        f"_{datetime.now().strftime('%Y%m%d_%H%M%S')}" if use_timestamp else ""
    )
    summary_file = f"followers_summary{timestamp_str}.csv"

    with open(summary_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=all_results[0].keys())
        writer.writeheader()
        writer.writerows(all_results)

    print(f"\n{'=' * 60}")
    print("Summary:")
    print(f"{'=' * 60}")
    for result in all_results:
        status_icon = "✓" if result["status"] == "success" else "✗"
        print(
            f"{status_icon} @{result['username']}: {result['fetched_count']} followers fetched"
        )
    print(f"\n✓ Summary saved to: {summary_file}")

    return all_results


def main():
    """
    CLI entry point
    """
    parser = argparse.ArgumentParser(
        description="Scrape followers from Twitter/X profiles",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s elonmusk
  %(prog)s elonmusk --limit 500 --timestamp
  %(prog)s elonmusk BillGates BarackObama -l 1000 -t
  %(prog)s user1 user2 -t  (fetch ALL followers with timestamp)
  %(prog)s elonmusk --proxy  (use proxy configured in script)
        """,
    )

    parser.add_argument(
        "usernames",
        nargs="+",
        help="Twitter username(s) to scrape followers from (without @)",
    )

    parser.add_argument(
        "-l",
        "--limit",
        type=int,
        default=0,
        help="Number of followers to fetch per user (default: 100, use 0 for unlimited)",
    )

    parser.add_argument(
        "-t",
        "--timestamp",
        action="store_true",
        help="Add timestamp to output filenames (prevents overwriting)",
    )

    parser.add_argument(
        "-p",
        "--proxy",
        action="store_true",
        help="Use proxy (configure PROXY variable in script first)",
    )

    args = parser.parse_args()

    # Run the scraper
    if len(args.usernames) == 1:
        # Single user
        asyncio.run(
            get_followers(
                args.usernames[0],
                limit=args.limit,
                use_timestamp=args.timestamp,
                use_proxy=args.proxy,
            )
        )
    else:
        # Multiple users
        asyncio.run(
            get_followers_multiple(
                args.usernames,
                limit=args.limit,
                use_timestamp=args.timestamp,
                use_proxy=args.proxy,
            )
        )


if __name__ == "__main__":
    main()
