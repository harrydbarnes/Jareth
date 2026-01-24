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

def test_robust_sentence_splitting():
    """
    Test that abbreviations do not split sentences, but actual sentence boundaries do.
    """
    # Fix #4: abbreviations should not split sentences
    text = "Dr. Smith is here. Mr. Jones is too. Ms. Doe agrees."
    sentences = split_sentences(text)
    assert len(sentences) == 3
    assert sentences[0] == "Dr. Smith is here."
    assert sentences[1] == "Mr. Jones is too."
    assert sentences[2] == "Ms. Doe agrees."

    # Should still split on actual sentences
    text2 = "Hello world. This is a test."
    sentences2 = split_sentences(text2)
    assert len(sentences2) == 2

@pytest.mark.parametrize("keyword", ["ASAP", "Action Required", "COB", "EOD", "strict deadline"])
def test_expanded_deadline_keywords(keyword):
    """
    Test that new deadline keywords are detected.
    """
    # Fix #6: New keywords
    text = f"This needs to be done {keyword}."
    deadlines = find_deadlines(text)
    assert deadlines, f"Failed to match keyword: {keyword}"

def test_strict_deadline_phrase():
    """
    Test specifically for 'strict deadline' phrase in a sentence.
    """
    # Check "strict deadline"
    text = "There is a strict deadline for this."
    deadlines = find_deadlines(text)
    assert deadlines
