
import pytest
from src.insight_analyzer import find_name_mentions

def test_find_name_mentions_whitespace():
    sample_text = "Hello John, how are you?"

    # Test with standard name
    mentions = find_name_mentions(sample_text, "John")
    assert len(mentions) == 1
    assert "Hello John" in mentions[0]

    # Test with leading/trailing whitespace in user_name
    # Without strip(), this would create regex r'\b John \b' which fails to match " John,"
    mentions_spaced = find_name_mentions(sample_text, " John ")
    assert len(mentions_spaced) == 1
    assert "Hello John" in mentions_spaced[0]

    # Test with just whitespace
    mentions_empty = find_name_mentions(sample_text, "   ")
    assert len(mentions_empty) == 0
