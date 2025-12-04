
import re
import json

def test_regex(name, template_str):
    print(f"--- Testing {name} ---")
    print(f"Original: {template_str}")
    
    # Refined proposed implementation
    # Match colon, comma, or open bracket, followed by optional whitespace, then the placeholder
    # We capture the delimiter in group 1 and the placeholder in group 2
    proposed_template = re.sub(r'([:,\[])\s*(%[a-zA-Z0-9_]+)', r'\1 "\2"', template_str)
    
    print(f"Refined Fix: {proposed_template}")
    try:
        json.loads(proposed_template)
        print("Refined: SUCCESS")
    except json.JSONDecodeError as e:
        print(f"Refined: FAILED - {e}")
    print("\n")

# Test cases from user report
test_cases = [
    ("Graph 0 (lowercase)", '{"value": %groupcount}'),
    ("Graph 2 (uppercase)", '{"x": %TOOL, "y": %WALLTIME}'),
    ("Graph 5 (lowercase no space)", '{"x":%date, "y":%monthly_count}'),
    ("Mixed", '{"a": %UPPER, "b": %lower}'),
    ("List", '{"list": [%ITEM1, %item2]}'),
    ("List start", '{"list": [%ITEM1]}'),
    ("Nested List", '{"colors": [[0, %COLOR1], [1, %COLOR2]]}')
]

for name, case in test_cases:
    test_regex(name, case)
