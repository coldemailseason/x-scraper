import asyncio

from twscrape import API

"""

How to use:

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
11. Run this script. Enjoy.

"""


async def add_account_with_cookies(username, cookies):
    """Add Twitter account with complete cookies to twscrape"""

    api = API()  # Uses default accounts.db

    # Uses empty placeholders, since the API call still expects them
    password = ""
    email = ""
    email_password = ""

    print(f"\nProcessing account: {username}")

    # First, try to delete the existing account if it exists
    print("Removing old account if it exists...")
    try:
        await api.pool.delete_accounts(username)
        print(f"✓ Removed old account '{username}'")
    except Exception as e:
        print(f"  (No old account to remove: {e})")

    print("\nAdding account with cookies...")
    await api.pool.add_account(
        username=username,
        password=password,
        email=email,
        email_password=email_password,
        cookies=cookies,
    )
    print(f"✓ Account '{username}' added")

    # CRITICAL STEP: Login the account to activate it
    print("\nAttempting to login account...")
    try:
        await api.pool.login_all()
        print("✓ Login process completed")
    except Exception as e:
        print(f"⚠ Login error: {e}")

    # Check account status
    print("\n" + "=" * 60)
    print("Account Status:")
    print("=" * 60)
    accounts = await api.pool.accounts_info()
    for acc in accounts:
        print(f"Username:   {acc['username']}")
        print(f"Logged in:  {acc['logged_in']}")
        print(f"Active:     {acc['active']}")
        print(f"Last used:  {acc.get('last_used', 'Never')}")
        print(f"Total req:  {acc['total_req']}")
        print(f"Error:      {acc.get('error_msg', 'None')}")

    # Only test if account is active
    if accounts and accounts[0]["active"]:
        print("\n" + "=" * 60)
        print("Testing Account:")
        print("=" * 60)
        try:
            user = await api.user_by_login(username)
            print("✓ SUCCESS! Account is working!")
            print(f"  Username:    @{user.username}")
            print(f"  Display:     {user.displayname}")
            print(f"  Followers:   {user.followersCount:,}")
            print(f"  Following:   {user.friendsCount:,}")
            print(f"  Tweets:      {user.statusesCount:,}")
        except Exception as e:
            print(f"✗ ERROR testing account: {e}")
    else:
        print("\n⚠ Account is not active. Cannot test.")
        print("\nTroubleshooting:")
        print("1. Make sure you have BOTH auth_token AND ct0 cookies")
        print("2. Get fresh cookies from browser (F12 > Application > Cookies)")
        print("3. The ct0 cookie is the CSRF token and is REQUIRED")
        print("4. Cookies expire - extract fresh ones if needed")


async def add_all_from_file(filepath="accounts.txt"):
    """Parse username:auth_token:ct0 from file and run login for each"""

    with open(filepath, "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    for line in lines:
        try:
            username, auth_token, ct0 = line.split(":")
        except ValueError:
            print(f"✗ Skipping malformed line: {line}")
            continue

        cookies = f"auth_token={auth_token}; ct0={ct0}"
        await add_account_with_cookies(username, cookies)


if __name__ == "__main__":
    asyncio.run(add_all_from_file())
