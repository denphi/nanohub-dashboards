#!/usr/bin/env python3
"""
Test script to verify unique trace handling and trace names.
"""
import json

# Simulate what happens with our current logic
plot_templates = [
    {"type": "bar", "x": "%TOOL", "y": "%VALUE", "name": "%TOOL"},
    {"type": "scatter", "x": "%TOOL", "y": "%TOTAL", "name": "Total", "unique": True}
]

data = {
    "TOOL": ["ToolA", "ToolA", "ToolB", "ToolB"],
    "VALUE": [10, 20, 30, 40],
    "TOTAL": [50, 50, 50, 50],
    "GROUP": ["G1", "G2", "G1", "G2"]
}

# Separate unique and regular templates
unique_templates = []
regular_templates = []

for template in plot_templates:
    if isinstance(template, dict) and template.get('unique') is True:
        unique_templates.append(template)
    else:
        regular_templates.append(template)

print(f"Regular templates: {len(regular_templates)}")
print(f"Unique templates: {len(unique_templates)}")
print(f"\nRegular: {regular_templates}")
print(f"Unique: {unique_templates}")

# Check if unique template has name
for template in unique_templates:
    print(f"\nUnique template has name: {'name' in template}")
    if 'name' in template:
        print(f"Name value: {template['name']}")
