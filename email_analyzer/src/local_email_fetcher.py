import datetime
import win32com.client
from typing import List, Dict, Any, Optional

class LocalEmailFetcher:
    def __init__(self):
        try:
            self.outlook = win32com.client.Dispatch("Outlook.Application")
            self.namespace = self.outlook.GetNamespace("MAPI")
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Outlook: {e}. Is Outlook running?")

    def fetch_emails(self,
                     folder_name: str = "Inbox",
                     recursive: bool = False,
                     date_range_days: int = 0) -> List[Dict[str, Any]]:
        """
        Fetches emails from the specified folder.

        Args:
            folder_name: The name of the folder to search in (default: "Inbox").
            recursive: Whether to search subfolders recursively.
            date_range_days: Number of days back to search. 0 means "Today".

        Returns:
            A list of dictionaries containing email details.
        """

        # Resolve the folder
        try:
            # Default to Inbox if not specified or "Inbox"
            if folder_name.lower() == "inbox":
                folder = self.namespace.GetDefaultFolder(6) # 6 is olFolderInbox
            else:
                # Try to find the folder in the default store
                default_folder = self.namespace.GetDefaultFolder(6)
                parent = default_folder.Parent
                folder = self._find_folder(parent, folder_name)
                if not folder:
                    raise ValueError(f"Folder '{folder_name}' not found.")
        except Exception as e:
            raise ValueError(f"Error accessing folder: {e}")

        # Calculate date range
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=date_range_days)
        cutoff_date = cutoff_date.replace(hour=0, minute=0, second=0, microsecond=0)

        emails = []
        self._process_folder(folder, recursive, cutoff_date, emails)
        return emails

    def _find_folder(self, parent_folder, folder_name):
        try:
            folders = parent_folder.Folders
            for folder in folders:
                if folder.Name == folder_name:
                    return folder
        except Exception:
            pass
        return None

    def _process_folder(self, folder, recursive, cutoff_date, emails_list):
        items = folder.Items
        try:
            items.Sort("[ReceivedTime]", True) # Descending
        except Exception:
            pass

        for item in items:
            try:
                # Check if it's a MailItem (Class 43)
                if item.Class != 43:
                    continue

                # Check date
                received_time = item.ReceivedTime

                if received_time.tzinfo is not None:
                     received_time = received_time.replace(tzinfo=None)

                if received_time < cutoff_date:
                    # Since we sorted descending, we can stop processing this folder?
                    # Be careful if sort failed. Just continue for robustness.
                    continue

                email_data = {
                    "subject": item.Subject,
                    "body": item.Body,
                    "sender": item.SenderName,
                    "received_time": str(received_time)
                }
                emails_list.append(email_data)

            except Exception as e:
                # Skip individual items that cause errors
                print(f"Error processing item: {e}")
                continue

        if recursive:
            for subfolder in folder.Folders:
                self._process_folder(subfolder, True, cutoff_date, emails_list)
