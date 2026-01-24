import pytest
from src.insight_analyzer import find_todos, split_sentences, find_deadlines

@pytest.mark.parametrize("text, expected_todo", [
    ("Task: investigate the issue.", "Task: investigate the issue."),
    ("We need to ensure that this works.", "We need to ensure that this works."),
    ("Here is a task:", "Here is a task:")
])
def test_symbol_todo_boundaries(text, expected_todo):
    """
    Test various TODO patterns including symbol boundaries and standard keywords.
    """
    # Fix #2: "task:" should match "Task: investigate"
    todos = find_todos(text)
    assert expected_todo in todos

@pytest.mark.parametrize("text, expected_sentences", [
    (
        "Dr. Smith is here. Mr. Jones is too. Ms. Doe agrees.",
        ["Dr. Smith is here.", "Mr. Jones is too.", "Ms. Doe agrees."]
    ),
    (
        "Hello world. This is a test.",
        ["Hello world.", "This is a test."]
    )
])
def test_robust_sentence_splitting(text, expected_sentences):
    """
    Test that abbreviations do not split sentences, but actual sentence boundaries do.
    """
    # Fix #4: abbreviations should not split sentences
    sentences = split_sentences(text)
    assert sentences == expected_sentences

@pytest.mark.parametrize("text_with_deadline", [
    "This needs to be done ASAP.",
    "This needs to be done Action Required.",
    "This needs to be done COB.",
    "This needs to be done EOD.",
    "This needs to be done strict deadline.",
    "There is a strict deadline for this.",
])
def test_expanded_deadline_keywords(text_with_deadline):
    """
    Test that new deadline keywords are detected in various sentences.
    """
    # Fix #6: New keywords
    deadlines = find_deadlines(text_with_deadline)
    assert deadlines, f"Failed to find deadline in: '{text_with_deadline}'"
