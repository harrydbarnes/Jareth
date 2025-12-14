import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import datetime
import threading
import sys
import os
import logging

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

try:
    from src.local_email_fetcher import LocalEmailFetcher
    from src.insight_analyzer import find_todos, find_deadlines, find_name_mentions
except ImportError as e:
    messagebox.showerror("Import Error", f"Failed to import modules: {e}")
    sys.exit(1)

class EmailAnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Email Analyzer")
        self.root.geometry("800x600")

        self.analysis_thread = None
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # --- Settings Section ---
        settings_frame = ttk.LabelFrame(root, text="Settings", padding="10")
        settings_frame.pack(fill="x", padx=10, pady=5)

        # Row 0: User Name
        ttk.Label(settings_frame, text="Your Name (for mentions):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.user_name_var = tk.StringVar()
        ttk.Entry(settings_frame, textvariable=self.user_name_var, width=30).grid(row=0, column=1, sticky="w", padx=5, pady=5)

        # Row 1: Folder Selection
        ttk.Label(settings_frame, text="Folder (or path e.g. 'Inbox/MySubfolder'):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.folder_var = tk.StringVar(value="Inbox")
        folder_combo = ttk.Combobox(settings_frame, textvariable=self.folder_var, values=["Inbox", "Sent Items"])
        folder_combo.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        self.recursive_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(settings_frame, text="Include Subfolders", variable=self.recursive_var).grid(row=1, column=2, sticky="w", padx=5, pady=5)

        # Row 2: Date Range
        ttk.Label(settings_frame, text="Date Range:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.date_range_var = tk.IntVar(value=0) # 0=Today

        date_frame = ttk.Frame(settings_frame)
        date_frame.grid(row=2, column=1, columnspan=2, sticky="w")

        ttk.Radiobutton(date_frame, text="Today", variable=self.date_range_var, value=0).pack(side="left", padx=5)
        ttk.Radiobutton(date_frame, text="Last 7 Days", variable=self.date_range_var, value=7).pack(side="left", padx=5)
        ttk.Radiobutton(date_frame, text="Last 14 Days", variable=self.date_range_var, value=14).pack(side="left", padx=5)
        ttk.Radiobutton(date_frame, text="Last 30 Days", variable=self.date_range_var, value=30).pack(side="left", padx=5)

        # --- Action Section ---
        action_frame = ttk.Frame(root, padding="10")
        action_frame.pack(fill="x", padx=10)

        self.analyze_btn = ttk.Button(action_frame, text="Analyze Emails", command=self.start_analysis)
        self.analyze_btn.pack(side="left")

        self.status_lbl = ttk.Label(action_frame, text="Ready")
        self.status_lbl.pack(side="left", padx=10)

        # --- Results Section ---
        results_frame = ttk.LabelFrame(root, text="Results", padding="10")
        results_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.results_text = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD, state='disabled')
        self.results_text.pack(fill="both", expand=True)

        # Tag configuration for formatting
        self.results_text.tag_config("header", font=("Helvetica", 12, "bold"))
        self.results_text.tag_config("subheader", font=("Helvetica", 10, "bold"))
        self.results_text.tag_config("bullet", lmargin1=20, lmargin2=30)
        self.results_text.tag_config("email_ref", font=("Helvetica", 9, "italic"), foreground="gray")

    def start_analysis(self):
        user_name = self.user_name_var.get().strip()
        if not user_name:
            messagebox.showwarning("Input Required", "Please enter your name for mention tracking.")
            return

        self.analyze_btn.config(state="disabled")
        self.status_lbl.config(text="Analyzing... This may take a moment.")
        self.results_text.config(state='normal')
        self.results_text.delete(1.0, tk.END)
        self.results_text.config(state='disabled')

        # Run in a separate thread to keep UI responsive
        self.analysis_thread = threading.Thread(target=self.run_analysis, args=(user_name,), daemon=True)
        self.analysis_thread.start()

    def run_analysis(self, user_name):
        try:
            fetcher = LocalEmailFetcher()
            emails = fetcher.fetch_emails(
                folder_name=self.folder_var.get(),
                recursive=self.recursive_var.get(),
                date_range_days=self.date_range_var.get()
            )

            # Analyze
            todos = []
            deadlines = []
            mentions = []

            for email in emails:
                subject = email.get("subject", "(No Subject)")
                body = email.get("body", "")

                # Helper for formatting the reference
                ref = f"[Subject: {(subject[:75] + '...') if len(subject) > 75 else subject}]"

                found_todos = find_todos(body)
                for t in found_todos:
                    todos.append((t, ref))

                found_deadlines = find_deadlines(body)
                for d in found_deadlines:
                    deadlines.append((d, ref))

                found_mentions = find_name_mentions(body, user_name)
                for m in found_mentions:
                    mentions.append((m, ref))

            # Update UI
            self.root.after(0, self.display_results, todos, deadlines, mentions)

        except Exception as e:
            logging.exception("An error occurred during analysis")
            self.root.after(0, self.show_error, str(e))

    def _display_section(self, title: str, icon: str, items: list):
        """Helper to display a section of results in the text widget."""
        self.results_text.insert(tk.END, f"{icon} {title}\n", "subheader")
        if items:
            for item, ref in items:
                self.results_text.insert(tk.END, f"• {item}\n", "bullet")
                self.results_text.insert(tk.END, f"  {ref}\n\n", "email_ref")
        else:
            self.results_text.insert(tk.END, "  No items found.\n\n", "bullet")

    def display_results(self, todos, deadlines, mentions):
        self.results_text.config(state='normal')

        self.results_text.insert(tk.END, "Analysis Results\n\n", "header")

        self._display_section("Outstanding Tasks / To-Dos", "🔴", todos)
        self._display_section("Upcoming Deadlines", "⏰", deadlines)
        self._display_section("Name Mentions", "📣", mentions)

        self.results_text.config(state='disabled')
        self.status_lbl.config(text=f"Analysis Complete. Found {len(todos)} tasks, {len(deadlines)} deadlines, {len(mentions)} mentions.")
        self.analyze_btn.config(state="normal")

    def show_error(self, message):
        messagebox.showerror("Error", message)
        self.status_lbl.config(text="Error occurred.")
        self.analyze_btn.config(state="normal")

    def on_closing(self):
        """Handles the window close event."""
        if self.analysis_thread and self.analysis_thread.is_alive():
            messagebox.showwarning("Analysis in Progress", "Please wait for the analysis to complete before closing.")
            return
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = EmailAnalyzerGUI(root)
    root.mainloop()
