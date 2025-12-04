
import re
import json

def test_regex(name, template_str):
    print(f"--- Testing {name} ---")
    print(f"Original: {template_str}")
    
    # Current implementation in client.py
    fixed_template = re.sub(r':\s*(%[A-Z_]+)', r': "\1"', template_str)
    fixed_template = re.sub(r',\s*(%[A-Z_]+)', r', "\1"', fixed_template)
    
    print(f"Current Fix: {fixed_template}")
    try:
        json.loads(fixed_template)
        print("Current: SUCCESS")
    except json.JSONDecodeError as e:
        print(f"Current: FAILED - {e}")

    # Proposed implementation
    proposed_template = re.sub(r':\s*(%[a-zA-Z0-9_]+)', r': "\1"', template_str)
    proposed_template = re.sub(r',\s*(%[a-zA-Z0-9_]+)', r', "\1"', proposed_template)
    
    # Also handle cases where it might be in a list without a preceding comma if it's the first item? 
    # But usually it follows [ or , so let's check.
    # Actually, the user's examples show "value": %groupcount, so it follows :
    
    print(f"Proposed Fix: {proposed_template}")
    try:
        json.loads(proposed_template)
        print("Proposed: SUCCESS")
    except json.JSONDecodeError as e:
        print(f"Proposed: FAILED - {e}")
    print("\n")

# Test cases from user report
test_cases = [
    ("Graph 0 (lowercase)", '{"value": %groupcount}'),
    ("Graph 2 (uppercase)", '{"x": %TOOL, "y": %WALLTIME}'),
    ("Graph 5 (lowercase no space)", '{"x":%date, "y":%monthly_count}'),
    ("Mixed", '{"a": %UPPER, "b": %lower}'),
    ("List", '{"list": [%ITEM1, %item2]}') # This might fail with current logic if not handled well
]

for name, case in test_cases:
    test_regex(name, case)
