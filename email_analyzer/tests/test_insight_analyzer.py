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
    # "Another task: investigate" - The original code failed to find this due to regex \b issue with colon.
    # Our optimized code preserves this behavior (unfortunately, but correctly preserving behavior).
    # However, "Task: investigate" fails, but "This is a task: investigate" might match?
    # "task:" is the keyword. \btask:\b matches " task: " but not " task:foo".

    text = "This is a task: investigate."
    # \b matches between ' ' and 't'.
    # \b matches between ':' and ' '.
    # So "This is a task: investigate" should match!

    # Wait, earlier I tested `re.search(r'\btask:\b', 'Task: investigate')` and it failed.
    # Because 'Task:' at start of string. Boundary at start (before T).
    # Boundary after k (between k and :).
    # BUT \b requires boundary.
    # The regex is `\btask:\b`.
    # It matches `task:` literally.
    # And asserts boundary before `t` and after `:`.
    # After `:`, if we have space... `:` is non-word. ` ` is non-word. NO BOUNDARY.
    # So `\btask:\b` will NEVER match `task:` if followed by space.
    # It only matches if followed by a WORD char?
    # If followed by word char `a`, then `:` (non-word) -> `a` (word). Boundary exists!
    # So `task:foo` matches!

    text_fail = "Task: investigate"
    assert find_todos(text_fail) == []

    # But "action item" works because it ends with 'm' (word char).
    text_pass = "This is an action item."
    assert len(find_todos(text_pass)) == 1
