"""
This module provides functions to analyze email content and extract
actionable insights such as to-do items, deadlines, and name mentions.
"""
import re
from typing import List, Union

# Compile regex at module level to avoid recompilation and reuse across functions
# Split email into sentences. A more robust sentence tokenizer could be used for complex cases.
# This basic split works for many common email formats.
SENTENCE_SPLIT_REGEX = re.compile(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s')

# Compiled regex for find_todos
TODO_KEYWORDS = [
    "action item", "please complete", "task:", "to do:", "i need you to",
    "can you", "could you please", "ensure that", "make sure to", "follow up on",
    "let's aim to", "we need to", "important to do", "kindly address"
]
TODO_REGEX = re.compile(r'\b(?:' + '|'.join(map(re.escape, TODO_KEYWORDS)) + r')\b', re.IGNORECASE)

# Compiled regex for find_deadlines
DEADLINE_KEYWORDS = [
    "due by", "deadline is", "by next week", "by EOD", "by COB", "by close of business",
    "by tomorrow", "by end of day", "by end of the week", "by end of month",
    "by Monday", "by Tuesday", "by Wednesday", "by Thursday", "by Friday",
    "by Saturday", "by Sunday",
    "by January", "by February", "by March", "by April", "by May", "by June",
    "by July", "by August", "by September", "by October", "by November", "by December",
    "by [0-9]{1,2}(st|nd|rd|th)? of", # e.g., by 1st of, by 2nd of, by 10th of
    "within [0-9]+ days", "in the next [0-9]+ hours", "complete by"
]
# Pre-process keywords to handle [0-9] replacement for regex
# We map keywords to their regex equivalent.
DEADLINE_KEYWORDS_REGEX = [k.replace("[0-9]", "\\d") for k in DEADLINE_KEYWORDS]
DEADLINE_REGEX = re.compile(r'\b(?:' + '|'.join(DEADLINE_KEYWORDS_REGEX) + r')\b', re.IGNORECASE)

# More complex patterns for specific dates like MM/DD/YYYY, YYYY-MM-DD
DEADLINE_DATE_PATTERNS = [
    r"\bby\s+\d{1,2}/\d{1,2}(?:/\d{2,4})?\b", # by 12/25, by 12/25/2023
    r"\bby\s+\d{4}-\d{2}-\d{2}\b",          # by 2023-12-25
    r"\b(?:on|before)\s+\w+\s+\d{1,2}(?:st|nd|rd|th)?\b" # on March 15th
]
DEADLINE_DATE_REGEX = re.compile('|'.join(DEADLINE_DATE_PATTERNS), re.IGNORECASE)


def split_sentences(text: str) -> List[str]:
    """
    Splits text into sentences using a regex.
    """
    if not text:
        return []
    return SENTENCE_SPLIT_REGEX.split(text)

def _ensure_sentences(email_body_or_sentences: Union[str, List[str]]) -> List[str]:
    """
    Helper to ensure we have a list of sentences.
    """
    if isinstance(email_body_or_sentences, list):
        return email_body_or_sentences
    if isinstance(email_body_or_sentences, str):
        return split_sentences(email_body_or_sentences)
    raise TypeError(f"Expected str or list, but got {type(email_body_or_sentences).__name__}")

def find_todos(email_body: Union[str, List[str]]) -> List[str]:
    """
    Identifies potential to-do items from the email body text.

    Args:
        email_body: The text content of the email or a list of sentences.

    Returns:
        A list of sentences or lines identified as potential to-do items.
        Returns an empty list if no to-do items are found.
    """
    if not email_body:
        return []

    found_todos: List[str] = []
    sentences = _ensure_sentences(email_body)

    for sentence in sentences:
        if not sentence.strip():
            continue
        # Use compiled regex for performance
        if TODO_REGEX.search(sentence):
            found_todos.append(sentence.strip())

    return found_todos

def find_deadlines(email_body: Union[str, List[str]]) -> List[str]:
    """
    Identifies mentions of potential deadlines from the email body text.

    Args:
        email_body: The text content of the email or a list of sentences.

    Returns:
        A list of sentences or lines identified as mentioning a potential deadline.
        Returns an empty list if no deadlines are found.
    """
    if not email_body:
        return []

    found_deadlines: List[str] = []
    sentences = _ensure_sentences(email_body)

    for sentence in sentences:
        if not sentence.strip():
            continue

        # Check compiled keyword regex
        if DEADLINE_REGEX.search(sentence):
            found_deadlines.append(sentence.strip())
            continue

        # Check compiled date patterns regex
        if DEADLINE_DATE_REGEX.search(sentence):
            found_deadlines.append(sentence.strip())
    
    return found_deadlines

def find_name_mentions(email_body: Union[str, List[str]], user_name: str) -> List[str]:
    """
    Finds sentences where a specific user_name is mentioned.

    Args:
        email_body: The text content of the email or a list of sentences.
        user_name: The name to search for (case-insensitive).

    Returns:
        A list of sentences or lines where the user_name is mentioned.
        Returns an empty list if the name is not found or inputs are invalid.
    """
    if not email_body or not user_name or not user_name.strip():
        return []

    found_mentions: List[str] = []
    # Use word boundaries to match whole words
    # Escape the user_name in case it contains special regex characters
    pattern = r'\b' + re.escape(user_name) + r'\b'
    
    sentences = _ensure_sentences(email_body)

    for sentence in sentences:
        if not sentence.strip():
            continue
        if re.search(pattern, sentence, re.IGNORECASE):
            found_mentions.append(sentence.strip())
            
    return found_mentions


if __name__ == "__main__":
    sample_email_body = """
    Hello team,

    Just a reminder about a few things. First, can you please complete the report by EOD Friday?
    This is a critical action item. John, I need you to look into the server logs.
    The deadline is next Wednesday for the phase 1 rollout.
    Also, could you please send me the presentation slides? Task: Review feedback by tomorrow.
    Let's aim to finish the prototype by August 15th.
    We need to ensure that all bugs are fixed.
    
    Alice, please follow up on the client query. The client expects a response by 2024-09-30.
    Bob, your task: prepare the demo script.
    Remember, the absolute final cut-off is by September 1st.
    Thanks!
    """

    print("--- Testing find_todos ---")
    todos = find_todos(sample_email_body)
    if todos:
        for i, todo in enumerate(todos):
            print(f"Todo {i+1}: {todo}")
    else:
        print("No to-do items found.")

    print("\n--- Testing find_deadlines ---")
    deadlines = find_deadlines(sample_email_body)
    if deadlines:
        for i, deadline in enumerate(deadlines):
            print(f"Deadline {i+1}: {deadline}")
    else:
        print("No deadlines found.")

    print("\n--- Testing find_name_mentions (User: John) ---")
    john_mentions = find_name_mentions(sample_email_body, "John")
    if john_mentions:
        for i, mention in enumerate(john_mentions):
            print(f"Mention {i+1}: {mention}")
    else:
        print("No mentions of John found.")

    print("\n--- Testing find_name_mentions (User: Alice) ---")
    alice_mentions = find_name_mentions(sample_email_body, "Alice")
    if alice_mentions:
        for i, mention in enumerate(alice_mentions):
            print(f"Mention {i+1}: {mention}")
    else:
        print("No mentions of Alice found.")
        
    print("\n--- Testing find_name_mentions (User: NonExistent) ---")
    non_existent_mentions = find_name_mentions(sample_email_body, "NonExistent")
    if non_existent_mentions:
        for i, mention in enumerate(non_existent_mentions):
            print(f"Mention {i+1}: {mention}")
    else:
        print("No mentions of NonExistent found.")

    empty_body = ""
    print("\n--- Testing with empty body ---")
    print(f"Todos: {find_todos(empty_body)}")
    print(f"Deadlines: {find_deadlines(empty_body)}")
    print(f"Name mentions (User: John): {find_name_mentions(empty_body, 'John')}")

    name_only_body = "Hey Alex, how are you?"
    print("\n--- Testing name mention in simple sentence ---")
    alex_mentions = find_name_mentions(name_only_body, "Alex")
    if alex_mentions:
        for i, mention in enumerate(alex_mentions):
            print(f"Mention {i+1}: {mention}")
    else:
        print("No mentions of Alex found.")

    todo_example_2 = "Another task: investigate the issue. And please ensure that the documentation is updated."
    print("\n--- Testing find_todos (Example 2) ---")
    todos_2 = find_todos(todo_example_2)
    if todos_2:
        for i, todo in enumerate(todos_2):
            print(f"Todo {i+1}: {todo}")
    else:
        print("No to-do items found.")

    deadline_example_2 = "The project is due by next week, specifically by Tuesday EOD. Also, another part is due by 25th of July."
    print("\n--- Testing find_deadlines (Example 2) ---")
    deadlines_2 = find_deadlines(deadline_example_2)
    if deadlines_2:
        for i, deadline in enumerate(deadlines_2):
            print(f"Deadline {i+1}: {deadline}")
    else:
        print("No deadlines found.")
