import unittest
import sys
import os

# Ensure src is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from email_analyzer.src.insight_analyzer import find_todos, split_sentences, find_deadlines

class TestInsightImprovements(unittest.TestCase):

    def test_symbol_todo_boundaries(self):
        # Fix #2: "task:" should match "Task: investigate"
        text = "Task: investigate the issue."
        todos = find_todos(text)
        self.assertIn("Task: investigate the issue.", todos)

        # Should also match standard keywords
        text2 = "We need to ensure that this works."
        todos2 = find_todos(text2)
        self.assertIn("We need to ensure that this works.", todos2)

        # Should match symbol keywords at end of sentence
        text3 = "Here is a task:"
        todos3 = find_todos(text3)
        self.assertIn("Here is a task:", todos3)

    def test_robust_sentence_splitting(self):
        # Fix #4: abbreviations should not split sentences
        text = "Dr. Smith is here. Mr. Jones is too. Ms. Doe agrees."
        sentences = split_sentences(text)
        self.assertEqual(len(sentences), 3)
        self.assertEqual(sentences[0], "Dr. Smith is here.")
        self.assertEqual(sentences[1], "Mr. Jones is too.")
        self.assertEqual(sentences[2], "Ms. Doe agrees.")

        # Should still split on actual sentences
        text2 = "Hello world. This is a test."
        sentences2 = split_sentences(text2)
        self.assertEqual(len(sentences2), 2)

    def test_expanded_deadline_keywords(self):
        # Fix #6: New keywords
        keywords = ["ASAP", "Action Required", "COB", "EOD", "strict deadline"]
        for kw in keywords:
            text = f"This needs to be done {kw}."
            deadlines = find_deadlines(text)
            self.assertTrue(deadlines, f"Failed to match keyword: {kw}")

        # Check "strict deadline"
        text = "There is a strict deadline for this."
        deadlines = find_deadlines(text)
        self.assertTrue(deadlines)

if __name__ == '__main__':
    unittest.main()
