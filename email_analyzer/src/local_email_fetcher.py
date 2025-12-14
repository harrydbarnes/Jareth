import datetime
import win32com.client
from typing import List, Dict, Any

import logging

# Configure logger for this module
logger = logging.getLogger(__name__)

OL_FOLDER_SENT_MAIL = 5
OL_FOLDER_INBOX = 6
OL_MAIL_ITEM = 43

class LocalEmailFetcher:
    def __init__(self):
        try:
            try:
                self.outlook = win32com.client.GetActiveObject("Outlook.Application")
            except Exception:
                self.outlook = win32com.client.Dispatch("Outlook.Application")

            self.namespace = self.outlook.GetNamespace("MAPI")
        except Exception as e:
            logger.error(f"Failed to connect to Outlook: {e}")
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
        folder = None
        try:
            # Default to Inbox if not specified or "Inbox"
            if folder_name.lower() == "inbox":
                folder = self.namespace.GetDefaultFolder(OL_FOLDER_INBOX)
            elif folder_name.lower() == "sent items":
                folder = self.namespace.GetDefaultFolder(OL_FOLDER_SENT_MAIL)
            else:
                # Try to find the folder in the default store
                default_folder = self.namespace.GetDefaultFolder(OL_FOLDER_INBOX)
                parent = default_folder.Parent
                folder = self._find_folder(parent, folder_name)

            if not folder:
                raise ValueError(f"Folder '{folder_name}' not found.")

        except ValueError:
            raise # Re-raise known errors
        except Exception as e:
            # Wrap COM errors
            logger.exception(f"Error accessing folder {folder_name}")
            raise ValueError(f"Error accessing folder '{folder_name}': {e}")

        # Calculate date range
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=date_range_days)
        cutoff_date = cutoff_date.replace(hour=0, minute=0, second=0, microsecond=0)

        emails = []
        self._process_folder(folder, recursive, cutoff_date, emails)
        return emails

    def _find_folder(self, parent_folder, folder_name):
        """
        Finds a folder by name or path (e.g., "Archive/2023").
        """
        # Handle path separators
        path_parts = folder_name.replace("\\", "/").split("/")

        current_parent = parent_folder
        target_folder = None

        for part in path_parts:
            if not part:
                continue

            found_sub = None
            try:
                for folder in current_parent.Folders:
                    if folder.Name == part:
                        found_sub = folder
                        break
            except Exception as e:
                 logger.warning(f"Error while searching for folder '{part}' in '{getattr(current_parent, 'Name', 'Unknown')}': {e}")
                 return None

            if found_sub:
                current_parent = found_sub
                target_folder = found_sub
            else:
                return None

        return target_folder

    def _process_folder(self, folder, recursive, cutoff_date, emails_list):
        items = folder.Items
        sorted_success = False

        # Attempt to Restrict by date first for performance
        try:
            cutoff_str = cutoff_date.strftime('%m/%d/%Y %I:%M %p')
            # Using simple format, hoping system locale accepts it or OLE handles it.
            # If it fails, we fall back to manual filtering.
            filtered_items = items.Restrict(f"[ReceivedTime] >= '{cutoff_str}'")
            items = filtered_items
        except Exception as e:
            logger.warning(f"Could not Restrict items in folder '{folder.Name}'. Falling back to manual filtering. Error: {e}")
            # items remains folder.Items (all items)

        try:
            items.Sort("[ReceivedTime]", True) # Descending
            sorted_success = True
        except Exception as e:
            logger.warning(f"Could not sort items in folder '{folder.Name}'. Performance may be affected. Error: {e}")

        for item in items:
            try:
                # Check if it's a MailItem
                if item.Class != OL_MAIL_ITEM:
                    continue

                # Check date
                received_time = item.ReceivedTime

                if received_time.tzinfo is not None:
                     received_time = received_time.astimezone(None).replace(tzinfo=None)

                if received_time < cutoff_date:
                    if sorted_success:
                        # Since we sorted descending, and found an old email, we can stop processing this folder.
                        break
                    else:
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
                logger.error(f"Error processing item with subject '{getattr(item, 'Subject', '[unretrievable]')}: {e}")
                continue

        if recursive:
            try:
                for subfolder in folder.Folders:
                    self._process_folder(subfolder, True, cutoff_date, emails_list)
            except Exception as e:
                 logger.warning(f"Error accessing subfolders of '{folder.Name}': {e}")
