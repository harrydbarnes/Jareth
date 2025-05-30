"""
Email Analyzer CLI Tool

This script authenticates with Microsoft Graph, fetches emails for a specified
date range, and analyzes them for to-do items, deadlines, and name mentions.
"""
import datetime
import sys

# Adjusting path to import from src directory
# This is a common way to handle imports when running a script from the project root
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

try:
    from src.auth_manager import get_graph_request_adapter
    from src.email_fetcher import fetch_emails_by_date_range
    from src.insight_analyzer import find_todos, find_deadlines, find_name_mentions
except ModuleNotFoundError:
    print("ERROR: Could not import necessary modules from 'src' directory.")
    print("Please ensure that 'auth_manager.py', 'email_fetcher.py', and 'insight_analyzer.py' exist in the 'src' directory.")
    print("And that you are running this script from the 'email_analyzer' project root directory.")
    sys.exit(1)

def parse_date_input(date_str: str) -> datetime.datetime | None:
    """Parses a YYYY-MM-DD string into a datetime object (start of day)."""
    try:
        return datetime.datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        print(f"Error: Invalid date format '{date_str}'. Please use YYYY-MM-DD.")
        return None

def main():
    """
    Main function to run the email analyzer CLI.
    """
    print("--- Email Analyzer Tool ---")

    # 1. Authentication
    print("\nAttempting to authenticate with Microsoft Graph...")
    # Note: get_graph_request_adapter returns GraphRequestAdapter,
    # and fetch_emails_by_date_range internally creates GraphServiceClient.
    request_adapter = get_graph_request_adapter()
    if not request_adapter:
        print("Authentication failed. Please check console messages from auth_manager.")
        print("Ensure YOUR_CLIENT_ID_HERE is replaced in src/auth_manager.py and you complete the device code flow.")
        return
    print("Authentication successful.")

    # 2. User Input
    print("\nPlease provide the following information:")
    user_name = input("Your first name (for tracking mentions, e.g., 'John'): ").strip()
    while not user_name:
        print("Name cannot be empty.")
        user_name = input("Your first name (for tracking mentions, e.g., 'John'): ").strip()

    start_date_str = input("Enter start date for email search (YYYY-MM-DD): ").strip()
    start_date = parse_date_input(start_date_str)
    while not start_date:
        start_date_str = input("Enter start date for email search (YYYY-MM-DD): ").strip()
        start_date = parse_date_input(start_date_str)

    end_date_str = input("Enter end date for email search (YYYY-MM-DD): ").strip()
    end_date = parse_date_input(end_date_str)
    while not end_date:
        end_date_str = input("Enter end date for email search (YYYY-MM-DD): ").strip()
        end_date = parse_date_input(end_date_str)

    # Adjust end_date to include the whole day
    end_date = end_date.replace(hour=23, minute=59, second=59)

    if start_date > end_date:
        print("Error: Start date cannot be after end date.")
        return

    # 3. Fetch Emails
    print(f"\nFetching emails from {start_date_str} to {end_date_str}...")
    try:
        # Ensure dates are timezone-aware if required by fetch_emails or Graph API,
        # or that fetch_emails_by_date_range handles UTC conversion.
        # The current fetch_emails_by_date_range appends 'Z', assuming naive datetimes are UTC.
        # For consistency, let's make them timezone-aware UTC.
        start_date_utc = start_date.replace(tzinfo=datetime.timezone.utc)
        end_date_utc = end_date.replace(tzinfo=datetime.timezone.utc)

        emails = fetch_emails_by_date_range(request_adapter, start_date_utc, end_date_utc)
    except Exception as e:
        print(f"An unexpected error occurred during email fetching: {e}")
        emails = None # Ensure emails is None if fetching fails catastrophically

    if emails is None: # fetch_emails_by_date_range returns None on API error
        print("Failed to fetch emails. Check console for specific error messages from email_fetcher.")
        return
    if not emails:
        print("No emails found in the specified date range.")
        return
    
    print(f"Fetched {len(emails)} emails.")

    # 4. Analyze Emails and Print Results
    print("\nAnalyzing emails for insights...")
    all_todos: list[str] = []
    all_deadlines: list[str] = []
    all_mentions: list[str] = []

    for i, email in enumerate(emails):
        print(f"  Processing email {i+1}/{len(emails)}: Subject: {email.get('subject', 'N/A')}")
        body = email.get("plain_text_body", "")
        if not body:
            print(f"    Skipping email ID {email.get('id', 'N/A')} due to empty body.")
            continue

        todos_found = find_todos(body)
        if todos_found:
            all_todos.extend([f"[From email: {email.get('subject', 'N/A')[:30]}...] {todo}" for todo in todos_found])

        deadlines_found = find_deadlines(body)
        if deadlines_found:
            all_deadlines.extend([f"[From email: {email.get('subject', 'N/A')[:30]}...] {deadline}" for deadline in deadlines_found])
        
        if user_name: # Only search for name if provided
            mentions_found = find_name_mentions(body, user_name)
            if mentions_found:
                all_mentions.extend([f"[From email: {email.get('subject', 'N/A')[:30]}...] {mention}" for mention in mentions_found])

    print("\n--- Analysis Complete ---")

    print("\n--- To-Do Items ---")
    if all_todos:
        for item in all_todos:
            print(f"- {item}")
    else:
        print("None found.")

    print("\n--- Deadlines Mentioned ---")
    if all_deadlines:
        for item in all_deadlines:
            print(f"- {item}")
    else:
        print("None found.")

    print(f"\n--- Mentions of '{user_name}' ---")
    if all_mentions:
        for item in all_mentions:
            print(f"- {item}")
    else:
        print(f"No mentions of '{user_name}' found.")
    
    print("\n--- End of Report ---")

if __name__ == "__main__":
    # Before running main, check if dependent libraries are installed.
    # This is a rudimentary check. A proper setup.py or requirements.txt install is better.
    try:
        import azure.identity
        import microsoft_graph_core
        import msgraph_sdk
        import kiota_authentication_azure
    except ImportError as e:
        print(f"ERROR: Missing one or more required libraries: {e.name}")
        print("Please install them by running: pip install azure-identity microsoft-graph-core msgraph-sdk kiota-authentication-azure")
        print("Ensure you have also populated 'requirements.txt' and installed from it if needed.")
        sys.exit(1)
        
    main()
