import unittest
from unittest.mock import MagicMock, patch
import sys
import logging

# Mock tkinter before importing main
sys.modules["tkinter"] = MagicMock()
sys.modules["tkinter.ttk"] = MagicMock()
sys.modules["tkinter.messagebox"] = MagicMock()
sys.modules["tkinter.scrolledtext"] = MagicMock()

# Mock win32com just in case local_email_fetcher is imported and tries to use it
sys.modules["win32com"] = MagicMock()
sys.modules["win32com.client"] = MagicMock()

# We need to ensure src is in path if main imports it?
# main.py does sys.path.insert, so it should handle it.
# But we are in email_analyzer/tests/ ..
# If we run from email_analyzer/ directory, main is in ., src is in ./src
# We will run `python3 -m unittest tests/test_main_security.py` from email_analyzer/

import main
from main import EmailAnalyzerGUI, MAX_BODY_LENGTH

class TestEmailAnalyzerSecurity(unittest.TestCase):

    @patch("main.split_sentences")
    @patch("main.LocalEmailFetcher")
    def test_dos_prevention_large_body(self, mock_fetcher_cls, mock_split):
        """
        Test that large email bodies are truncated to MAX_BODY_LENGTH.
        """
        # Setup mock fetcher
        mock_fetcher_instance = mock_fetcher_cls.return_value

        # Create a huge body
        huge_body = "A" * (MAX_BODY_LENGTH + 5000)

        mock_fetcher_instance.fetch_emails.return_value = [
            {
                "subject": "Huge Email",
                "body": huge_body,
                "sender": "spammer@example.com",
                "received_time": "2023-01-01"
            }
        ]

        # Mock split_sentences to just return empty list (we only care about input)
        mock_split.return_value = []

        # Initialize GUI (mocked)
        root = MagicMock()
        app = EmailAnalyzerGUI(root)

        # Setup UI variables that are accessed in run_analysis
        app.folder_var = MagicMock()
        app.folder_var.get.return_value = "Inbox"
        app.recursive_var = MagicMock()
        app.recursive_var.get.return_value = False
        app.date_range_var = MagicMock()
        app.date_range_var.get.return_value = 0

        # Mock the analyzer functions, prevent side effects, and capture logs
        with patch("main.find_todos", return_value=[]), \
             patch("main.find_deadlines", return_value=[]), \
             patch("main.find_name_mentions", return_value=[]), \
             self.assertLogs(level='WARNING') as cm:

            # Run analysis directly
            app.run_analysis("Test User")

            # Verify that a warning was logged for truncation
            self.assertEqual(len(cm.output), 1)
            expected_log = f"Email 'Huge Email...' body too large ({len(huge_body)} chars). Truncating to {MAX_BODY_LENGTH}."
            self.assertIn(expected_log, cm.output[0])

        # Verify split_sentences was called with truncated body
        self.assertTrue(mock_split.called)
        args, _ = mock_split.call_args
        called_body = args[0]

        self.assertEqual(len(called_body), MAX_BODY_LENGTH)
        self.assertEqual(called_body, huge_body[:MAX_BODY_LENGTH])

if __name__ == "__main__":
    unittest.main()
