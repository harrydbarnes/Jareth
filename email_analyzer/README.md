# Email Analyzer Tool

A powerful, locally-running Python tool designed to analyze your Outlook emails and extract actionable insights.

## ⚡ Overview

Email Analyzer connects to your local Outlook instance (via `pywin32`) to fetch emails and uses intelligent pattern matching to identify:

*   **🔴 Outstanding Tasks / To-Dos**: Automatically finds action items like "please complete", "action item", "task:", etc.
*   **⏰ Upcoming Deadlines**: Detects deadline phrases (e.g., "by EOD Friday", "due by next week") and specific dates.
*   **📣 Name Mentions**: Finds where you or others are mentioned in email threads.

The tool provides a user-friendly GUI built with `tkinter` to configure settings, run analysis, and view results.

## ✨ Features

*   **Local Processing**: All analysis happens on your machine. Your email data never leaves your computer.
*   **Smart Parsing**: Uses optimized regular expressions to cut through the noise and find what matters.
*   **Performance Focused**: Recently optimized with regex caching and loop efficiency improvements for faster analysis of large inboxes.
*   **Customizable**:
    *   Filter by folder (Inbox, Sent Items, etc.).
    *   Include/exclude subfolders.
    *   Select date range (Today, Last 7/14/30 Days).
    *   Search for mentions of specific names.

## 🛠️ Requirements

*   **OS**: Windows (Required for Outlook integration via `pywin32`)
*   **Software**: Microsoft Outlook (Desktop App)
*   **Python**: 3.8+
*   **Dependencies**: `pywin32`

## 🚀 Installation & Usage

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd email_analyzer
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the application:**
    ```bash
    python main.py
    ```

4.  **Using the Tool:**
    *   Enter your name in the "Your Name" field (to track mentions).
    *   Select the folder to analyze (e.g., Inbox).
    *   Choose a date range.
    *   Click "Analyze Emails".

## 🏎️ Performance Optimizations

This project implements several performance strategies to ensure responsiveness:
*   **Regex Caching (`lru_cache`)**: Dynamic patterns (like name mentions) are compiled once and cached, preventing overhead in large loops.
*   **Optimized Loops**: String operations are minimized inside critical processing loops.
*   **Module-Level compilation**: Static regexes are pre-compiled at the module level.

## 🤝 Contributing

1.  Fork the repository.
2.  Create a feature branch (`git checkout -b feature/amazing-feature`).
3.  Commit your changes (`git commit -m 'Add some amazing feature'`).
4.  Push to the branch (`git push origin feature/amazing-feature`).
5.  Open a Pull Request.

## 🧪 Testing

Run the test suite with `pytest`:

```bash
pytest
```
