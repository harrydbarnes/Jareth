import unittest
from unittest.mock import MagicMock, patch
import sys
import logging
import datetime
import io

# Mock win32com.client before importing the module under test
sys.modules["win32com"] = MagicMock()
sys.modules["win32com.client"] = MagicMock()

from src.local_email_fetcher import LocalEmailFetcher, OL_MAIL_ITEM

class TestLocalEmailFetcherSecurity(unittest.TestCase):
    def setUp(self):
        # Setup logging capture
        self.logger = logging.getLogger("src.local_email_fetcher")
        self.log_capture_string = io.StringIO()
        self.ch = logging.StreamHandler(self.log_capture_string)
        self.ch.setLevel(logging.ERROR)
        self.logger.addHandler(self.ch)

    def tearDown(self):
        self.logger.removeHandler(self.ch)

    @patch("src.local_email_fetcher.win32com.client")
    def test_sensitive_data_logging(self, mock_win32):
        """
        Test that sensitive data (email subject) is NOT logged when an error occurs.
        """
        # Mock Outlook structure
        mock_outlook = MagicMock()
        mock_namespace = MagicMock()
        mock_folder = MagicMock()

        mock_win32.GetActiveObject.return_value = mock_outlook
        mock_outlook.GetNamespace.return_value = mock_namespace
        mock_namespace.GetDefaultFolder.return_value = mock_folder

        # Create a mock mail item that fails when Body is accessed
        mock_item = MagicMock()
        mock_item.Class = OL_MAIL_ITEM
        mock_item.Subject = "Confidential Project Takeover"
        mock_item.EntryID = "00000000ABCDEF1234567890" # Mock EntryID
        mock_item.ReceivedTime = datetime.datetime.now()

        # Configure Body access to raise an exception
        # We need to set the side effect on the property access
        type(mock_item).Body = unittest.mock.PropertyMock(side_effect=Exception("Simulated Body Access Error"))

        # Setup folder items
        mock_items = MagicMock()
        mock_items.Restrict.return_value = mock_items # Mock Restrict returning self or another mock
        mock_items.__iter__.return_value = iter([mock_item])
        mock_folder.Items = mock_items
        mock_folder.Folders = [] # No subfolders

        fetcher = LocalEmailFetcher()

        # Run fetch_emails
        fetcher.fetch_emails(folder_name="Inbox")

        # Check logs
        log_contents = self.log_capture_string.getvalue()

        # 1. Verify that the SENSITIVE subject is NOT in the logs
        self.assertNotIn("Confidential Project Takeover", log_contents, "Security Fix Failed: Subject was logged!")

        # 2. Verify that the generic error or ID is in the logs
        self.assertIn("EntryID: 00000000ABCDEF123456...", log_contents, "Expected EntryID to be logged")
        self.assertIn("Simulated Body Access Error", log_contents, "Expected the exception message to be logged")

if __name__ == "__main__":
    unittest.main()
