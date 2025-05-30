# Handles OAuth2 authentication with Microsoft Graph API
"""
This module handles OAuth2 authentication with the Microsoft Graph API
using the device code flow.
"""

from azure.identity import DeviceCodeCredential
from azure.core.exceptions import AuthenticationError
from kiota_authentication_azure.azure_identity_authentication_provider import AzureIdentityAuthenticationProvider
from microsoft_graph_core import GraphRequestAdapter


# TODO: Replace with your actual Client ID from Azure AD app registration.
# Instructions for App Registration:
# 1. Go to the Azure portal (portal.azure.com).
# 2. Navigate to "Azure Active Directory".
# 3. Go to "App registrations" and click "New registration".
# 4. Give your app a name (e.g., "EmailAnalyzerApp").
# 5. Select "Accounts in this organizational directory only (Default Directory only - Single tenant)"
#    or "Accounts in any organizational directory (Any Azure AD directory - Multitenant)"
#    depending on your needs. For personal use, single tenant is often simpler.
#    For applications intended for wider use, multitenant might be necessary.
# 6. Under "Redirect URI (optional)", you can leave this blank for device code flow,
#    or select "Public client/native (mobile & desktop)" and enter `http://localhost`.
# 7. Click "Register".
# 8. Once registered, copy the "Application (client) ID" and paste it below.
# 9. Ensure the necessary API permissions are granted to this app registration.
#    Go to "API permissions" -> "Add a permission" -> "Microsoft Graph".
#    Select "Delegated permissions" and add "Mail.Read" and "User.Read".
#    Click "Grant admin consent for [Your Directory]" if available and appropriate.
CLIENT_ID = "YOUR_CLIENT_ID_HERE"
SCOPES = ["Mail.Read", "User.Read"]

def get_graph_request_adapter() -> GraphRequestAdapter | None:
    """
    Authenticates with Microsoft Graph API using device code flow and returns
    a GraphRequestAdapter.

    The user will be prompted to open a URL in their browser and enter a code.

    Returns:
        GraphRequestAdapter: An adapter instance if authentication is successful.
        None: If authentication fails.
    """
    try:
        credential = DeviceCodeCredential(client_id=CLIENT_ID)
        
        # The AzureIdentityAuthenticationProvider requires scopes during its initialization.
        # DeviceCodeCredential itself will use its own configured scopes (if any)
        # or default scopes when get_token is called.
        # For clarity and to ensure correct scopes are used by the provider,
        # we pass them here.
        auth_provider = AzureIdentityAuthenticationProvider(credential, scopes=SCOPES)
        
        adapter = GraphRequestAdapter(auth_provider)
        print("GraphRequestAdapter successfully created.")
        print("Attempting to fetch a token to confirm authentication (this will trigger device flow if not cached)...")
        
        # To verify authentication and trigger the device flow immediately for the user,
        # we can try to get a token. This step is implicitly handled by Kiota when a request is made,
        # but doing it here provides immediate feedback to the user.
        # Note: The actual token is managed internally by the credential and auth_provider.
        # We're calling this to ensure the device flow is initiated if needed.
        
        # This is a bit of a workaround to trigger the device flow message.
        # The `DeviceCodeCredential` itself prompts the user when `get_token` is called.
        # The `AzureIdentityAuthenticationProvider` will call `get_token` internally
        # when the first Graph API call is made.
        # To force the prompt *before* the first API call, we can try to get a token here.
        # However, `auth_provider.get_authorization_token()` is an async method.
        # For a synchronous approach, the prompt will appear upon the first actual API call.
        # Let's rely on the first API call to trigger this, or the user can pre-authenticate.

        # A more direct way to trigger device flow for DeviceCodeCredential
        # if we weren't using the full adapter stack yet:
        test_token = credential.get_token(*SCOPES) # Pass scopes here
        if test_token:
            print(f"Successfully obtained a token for scopes: {SCOPES}")
            print("Device flow authentication likely completed or token was cached.")
        else:
            # This case should ideally not be reached if get_token raises an exception on failure.
            print("Failed to obtain a token, but no exception was raised.")
            return None

        return adapter

    except AuthenticationError as e:
        print(f"Authentication failed: {e}")
        print("Please ensure:")
        print(f"1. The Client ID '{CLIENT_ID}' is correct and the App Registration exists in Azure AD.")
        print("2. The required permissions (Mail.Read, User.Read) are granted in the App Registration.")
        print("3. You have completed the device code authentication flow in your browser.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

if __name__ == "__main__":
    print("Attempting to authenticate and get a GraphRequestAdapter...")
    adapter = get_graph_request_adapter()
    if adapter:
        print("Successfully obtained GraphRequestAdapter.")
        # Here you would typically proceed to make Graph API calls
        # For example:
        # from msgraph import GraphServiceClient
        # client = GraphServiceClient(adapter)
        # me = await client.me.get() # if using async adapter and client
        # print(f"Hello, {me.display_name}")
        print("You can now use the 'adapter' to interact with Microsoft Graph API.")
    else:
        print("Failed to obtain GraphRequestAdapter. Check the error messages above.")
