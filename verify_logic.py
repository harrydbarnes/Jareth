
import re

DEADLINE_KEYWORDS = ["urgent"]
DEADLINE_DATE_PATTERNS = [r"\d{4}-\d{2}-\d{2}"]

deadline_keyword_pattern = r'\b(?:' + '|'.join(DEADLINE_KEYWORDS) + r')\b'
deadline_date_pattern = '|'.join(DEADLINE_DATE_PATTERNS)
DEADLINE_REGEX = re.compile(f'{deadline_keyword_pattern}|{deadline_date_pattern}', re.IGNORECASE)

# Logic in code:
# if DEADLINE_REGEX.search(sentence):
#    found.append()
#    continue
# if DEADLINE_DATE_REGEX.search(sentence): # Assumed to be re.compile(deadline_date_pattern)
#    found.append()

def test_logic(sentence):
    print(f"Testing: '{sentence}'")
    matched_first = False
    if DEADLINE_REGEX.search(sentence):
        print("  Matched DEADLINE_REGEX (Union)")
        matched_first = True

    if not matched_first:
        print("  Did NOT match Union. Checking Date only...")
        # Simulate what DEADLINE_DATE_REGEX would do
        date_regex = re.compile(deadline_date_pattern, re.IGNORECASE)
        if date_regex.search(sentence):
            print("  Matched Date Regex! (This contradicts logic)")
        else:
            print("  Did not match Date Regex either.")

test_logic("This is urgent")
test_logic("Due by 2023-12-25")
test_logic("Nothing here")
