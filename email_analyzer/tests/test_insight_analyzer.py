import pytest
from src.insight_analyzer import find_todos, find_deadlines, find_name_mentions

def test_find_todos():
    sample_text = """
    First, can you please complete the report by EOD Friday?
    This is a critical action item.
    John, I need you to look into the server logs.
    Also, could you please send me the presentation slides?
    Let's aim to finish the prototype by August 15th.
    We need to ensure that all bugs are fixed.
    Alice, please follow up on the client query.
    """
    todos = find_todos(sample_text)
    expected_substrings = [
        "please complete the report",
        "action item",
        "i need you to look",
        "could you please send",
        "aim to finish",
        "need to ensure that",
        "please follow up on"
    ]

    assert len(todos) == 7
    for todo in todos:
        # Check if the extracted sentence contains one of the expected keywords/phrases implicitly
        # (This is a bit loose, but verifies we caught the lines)
        assert any(sub in todo.lower() for sub in ["please complete", "action item", "need you to", "could you please", "aim to", "need to ensure", "please follow up"])

def test_find_deadlines():
    sample_text = """
    First, can you please complete the report by EOD Friday?
    The deadline is next Wednesday for the phase 1 rollout.
    Task: Review feedback by tomorrow.
    Let's aim to finish the prototype by August 15th.
    The client expects a response by 2024-09-30.
    Remember, the absolute final cut-off is by September 1st.
    """
    deadlines = find_deadlines(sample_text)
    assert len(deadlines) == 6
    assert any("by eod friday" in d.lower() for d in deadlines)
    assert any("deadline is next wednesday" in d.lower() for d in deadlines)
    assert any("by tomorrow" in d.lower() for d in deadlines)
    assert any("by august 15th" in d.lower() for d in deadlines)
    assert any("by 2024-09-30" in d.lower() for d in deadlines)
    assert any("by september 1st" in d.lower() for d in deadlines)

def test_find_name_mentions():
    sample_text = """
    John, I need you to look into the server logs.
    Alice, please follow up.
    """
    mentions_john = find_name_mentions(sample_text, "John")
    assert len(mentions_john) == 1
    assert "John" in mentions_john[0]

    mentions_alice = find_name_mentions(sample_text, "Alice")
    assert len(mentions_alice) == 1
    assert "Alice" in mentions_alice[0]

    mentions_bob = find_name_mentions(sample_text, "Bob")
    assert len(mentions_bob) == 0

def test_empty_input():
    assert find_todos("") == []
    assert find_deadlines("") == []
    assert find_name_mentions("", "John") == []

def test_todo_edge_cases():
    # Test edge case for keywords ending in non-word characters like ':'.
    # Previous implementation failed to match "Task: investigate" due to regex boundary issues.
    # The new implementation should handle this correctly.

    text_success = "Task: investigate"
    assert len(find_todos(text_success)) == 1

    # But "action item" works because it ends with 'm' (word char).
    text_pass = "This is an action item."
    assert len(find_todos(text_pass)) == 1
