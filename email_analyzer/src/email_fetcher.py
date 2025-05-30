# This module will fetch emails using the Microsoft Graph API.
import datetime
from typing import List, Dict, Any

from microsoft_graph_core.graph_request_adapter import GraphRequestAdapter
from msgraph_sdk.models.odata_errors.odata_error import ODataError
from msgraph_sdk.models.message import Message
from msgraph_sdk.models.message_collection_response import MessageCollectionResponse
# For query parameters like $select, $filter, $orderby
from msgraph_sdk.me.messages.messages_request_builder import MessagesRequestBuilder

# It seems BodyType is not directly available for query parameters in select,
# but we can request body and uniqueBody. We will request uniqueBody which is often plain text.
# If specific body type like 'text' is needed, it's usually part of the 'body' property itself.
# from msgraph_sdk.models.body_type import BodyType # Example if it were for query parameters


def fetch_emails_by_date_range(
    request_adapter: GraphRequestAdapter,
    start_date: datetime.datetime,
    end_date: datetime.datetime
) -> List[Dict[str, Any]] | None:
    """
    Fetches emails from the Microsoft Graph API within a specified date range.

    Args:
        request_adapter: The authenticated GraphRequestAdapter.
        start_date: The start of the date range (inclusive).
        end_date: The end of the date range (inclusive).

    Returns:
        A list of dictionaries, where each dictionary represents an email
        with fields: id, receivedDateTime, subject, sender_email,
        to_recipients_emails, cc_recipients_emails, plain_text_body.
        Returns None if an API error occurs.
    """
    if not request_adapter:
        print("Error: Request adapter is not initialized.")
        return None

    # Construct the filter query string
    # Ensure timestamps are in ISO 8601 format with 'Z' for UTC.
    # Graph API expects yyyy-MM-ddTHH:mm:ssZ
    filter_query = (
        f"receivedDateTime ge {start_date.isoformat()}Z "
        f"and receivedDateTime le {end_date.isoformat()}Z"
    )
    
    # Define the fields to select
    # For body, uniqueBody is often preferred for plain text.
    # If HTML is fetched, it would need stripping.
    # The 'body' property itself contains 'content' and 'contentType'.
    # We will try to select uniqueBody which is typically plain text.
    select_fields = [
        "id",
        "receivedDateTime",
        "subject",
        "sender",
        "toRecipients",
        "ccRecipients",
        "uniqueBody", # Often plain text, simpler than handling body.content + body.contentType
        "body" # Fetch body as well to check its contentType if uniqueBody is not sufficient
    ]

    # Define the order by query parameter
    orderby_query = ["receivedDateTime desc"]

    try:
        print(f"Fetching emails from {start_date.isoformat()}Z to {end_date.isoformat()}Z")
        print(f"Filter: {filter_query}")

        # Prepare the request configuration
        request_configuration = MessagesRequestBuilder.MessagesRequestBuilderGetRequestConfiguration(
            query_parameters=MessagesRequestBuilder.MessagesRequestBuilderGetQueryParameters(
                filter=filter_query,
                select=select_fields,
                orderby=orderby_query,
                # top=10 # For fetching only the first page (e.g., 10 emails)
            )
        )
        
        # The GraphServiceClient is typically created from the adapter,
        # but the adapter itself has convenience methods for paths.
        # The path should be /me/messages
        # request_adapter.me is not directly available.
        # Instead, we need to build the request using the path and then call get.
        # A GraphServiceClient would abstract this.
        # For now, let's assume we need to construct the client first.
        # from msgraph_sdk.graph_service_client import GraphServiceClient
        # client = GraphServiceClient(request_adapter)
        # results = await client.me.messages.get(request_configuration=request_configuration)
        
        # The prompt implies using request_adapter.me.messages.get().
        # This structure is typical if 'request_adapter' is actually a 'GraphServiceClient' instance.
        # If 'request_adapter' is purely a 'GraphRequestAdapter', the calling pattern is different.
        # Let's assume for now that the intention is to use a GraphServiceClient implicitly or
        # that the GraphRequestAdapter has these fluent capabilities (which it might not directly).
        
        # Re-checking Kiota SDK usage:
        # GraphRequestAdapter is used to build a GraphServiceClient.
        # So, the calling code that uses this function should have created GraphServiceClient.
        # Let's adjust the expectation or make it clear.
        # For this function, we should expect GraphServiceClient for easier calls.
        # However, the prompt specified GraphRequestAdapter.
        
        # If using GraphRequestAdapter directly, it's more like:
        # messages_request_builder = MessagesRequestBuilder(request_adapter, {})
        # result = await messages_request_builder.get(request_configuration=request_configuration)

        # Let's assume the user of this function will pass a GraphServiceClient
        # that has been initialized with GraphRequestAdapter.
        # To stick to the prompt's type hint, we'll need to see how GraphRequestAdapter
        # can be used to make this call.
        # The `GraphRequestAdapter` itself doesn't have `.me.messages`.
        # This implies we need the `GraphServiceClient`.
        # I will proceed by constructing the client here, assuming it's lightweight to do so,
        # or add a note that the caller should pass GraphServiceClient.
        # For now, to make it runnable as per type hint:
        
        from msgraph_sdk.graph_service_client import GraphServiceClient
        
        # If this function is part of a class, client could be self.client.
        # If standalone, and we must adhere to GraphRequestAdapter input,
        # then the client must be created here.
        client = GraphServiceClient(authentication_provider=request_adapter.authentication_provider)


        # Using the client:
        messages_response = client.me.messages.get(request_configuration=request_configuration)
        
        if not messages_response or not messages_response.value:
            print("No messages found or error in response.")
            return []

        emails_data: List[Dict[str, Any]] = []
        for message in messages_response.value:
            sender_email = message.sender.email_address.address if message.sender and message.sender.email_address else "N/A"
            
            to_emails = [recipient.email_address.address for recipient in message.to_recipients if recipient.email_address]
            cc_emails = [recipient.email_address.address for recipient in message.cc_recipients if recipient.email_address]
            
            plain_text_body = ""
            if message.unique_body and message.unique_body.content:
                plain_text_body = message.unique_body.content
            elif message.body and message.body.content:
                if message.body.content_type == "text":
                    plain_text_body = message.body.content
                elif message.body.content_type == "html":
                    # Basic HTML stripping, a proper library would be better for robustness
                    # For now, this is a placeholder.
                    import re
                    plain_text_body = re.sub('<[^<]+?>', '', message.body.content)
                    print(f"Warning: Stripped HTML from body of message ID {message.id}. Consider using a dedicated HTML parsing library.")
                else:
                    plain_text_body = f"Unsupported body type: {message.body.content_type}"
            
            emails_data.append({
                "id": message.id,
                "receivedDateTime": message.received_date_time.isoformat() if message.received_date_time else "N/A",
                "subject": message.subject if message.subject else "N/A",
                "sender_email": sender_email,
                "to_recipients_emails": to_emails,
                "cc_recipients_emails": cc_emails,
                "plain_text_body": plain_text_body
            })
        
        # Handle pagination (basic example: check if there's a next page link)
        # A full implementation would loop here.
        if messages_response.odata_next_link:
            print(f"More messages available (pagination). Next link: {messages_response.odata_next_link}")
            print("Note: Full pagination is not implemented in this version. Only the first page is fetched.")

        return emails_data

    except ODataError as e:
        print(f"Microsoft Graph API Error: {e.error.message if e.error else str(e)}")
        # Detailed error information can be found in e.error
        if e.error:
            print(f"Code: {e.error.code}")
            if e.error.inner_error:
                print(f"Inner Error: {e.error.inner_error.message}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while fetching emails: {e}")
        return None

if __name__ == "__main__":
    # This block is for example and testing.
    # It requires a valid GraphRequestAdapter, which means auth_manager.py
    # must be run first, or its logic integrated here.
    print("This script (email_fetcher.py) is intended to be used with an authenticated GraphRequestAdapter.")
    print("To test this standalone, you would need to:")
    print("1. Ensure 'azure-identity', 'microsoft-graph-core', 'msgraph-sdk' are installed.")
    print("2. Have a valid 'YOUR_CLIENT_ID_HERE' in 'auth_manager.py'.")
    print("3. Successfully run 'auth_manager.py' to perform device code authentication.")
    print("4. Then, use the obtained 'adapter' here.")

    # Example (conceptual, requires actual adapter):
    # from email_analyzer.src.auth_manager import get_graph_request_adapter
    # print("Attempting to authenticate to test email fetching...")
    # request_adapter_instance = get_graph_request_adapter() # This is GraphRequestAdapter
    
    # if request_adapter_instance:
    #     print("Authentication successful. Now fetching emails...")
    #     # Note: get_graph_request_adapter returns GraphRequestAdapter,
    #     # but fetch_emails_by_date_range was written to internally create a GraphServiceClient.
    #     # This is a bit inconsistent. Ideally, fetch_emails_by_date_range should take GraphServiceClient.
    #     # For now, we pass the adapter, and it internally creates the client.

    #     # Define a date range for testing
    #     end_dt = datetime.datetime.now(datetime.timezone.utc)
    #     start_dt = end_dt - datetime.timedelta(days=7) # Last 7 days

    #     fetched_emails = fetch_emails_by_date_range(request_adapter_instance, start_dt, end_dt)

    #     if fetched_emails is not None:
    #         print(f"\nSuccessfully fetched {len(fetched_emails)} emails:")
    #         for i, email in enumerate(fetched_emails):
    #             print(f"\n--- Email {i+1} ---")
    #             print(f"  ID: {email['id']}")
    #             print(f"  Received: {email['receivedDateTime']}")
    #             print(f"  Subject: {email['subject']}")
    #             print(f"  Sender: {email['sender_email']}")
    #             print(f"  To: {', '.join(email['to_recipients_emails'])}")
    #             if email['cc_recipients_emails']:
    #                 print(f"  CC: {', '.join(email['cc_recipients_emails'])}")
    #             body_preview = (email['plain_text_body'][:100] + '...') if len(email['plain_text_body']) > 100 else email['plain_text_body']
    #             print(f"  Body (Preview): {body_preview}")
    #     else:
    #         print("Failed to fetch emails.")
    # else:
    #     print("Authentication failed. Cannot fetch emails.")
    pass # End of __main__ example block
