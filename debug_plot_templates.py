#!/usr/bin/env python3
"""
Debug script to examine plot templates that are failing to parse.
"""
import json
import nanohubremote as nr
from nanohubdashboard.client import DashboardClient

auth_data = {
    "grant_type": "personal_token",
    "token": "03b43cd742efa6591d24eca3920b652080467680",
}
session = nr.Session(auth_data, url="https://dev.nanohub.org/api")
client = DashboardClient(session=session)

print("Fetching dashboard 19 to examine plot templates...")
response = session.requestGet('dashboards/dashboard/read/19')
raw_data = response.json()
dashboard_data = raw_data.get('dashboard', raw_data)
raw_graphs = json.loads(dashboard_data.get('graphs', '[]'))

print(f"\nFound {len(raw_graphs)} graphs")
print("="*80)

for idx, graph in enumerate(raw_graphs):
    plot_str = graph.get('plot', '[]')

    if not plot_str or plot_str.strip() == '[]':
        print(f"\nGraph {idx}: No plot template")
        continue

    print(f"\nGraph {idx}:")
    print(f"  Query: {graph.get('query', 'N/A')}")
    print(f"  Zone: {graph.get('zone', 'N/A')}")
    print(f"  Plot template (raw):")
    print(f"  {plot_str[:500]}")  # First 500 chars

    # Try to parse it
    try:
        parsed = json.loads(plot_str)
        print(f"  ✓ Parses as valid JSON")
        print(f"  Plot config: {json.dumps(parsed, indent=2)[:300]}")
    except json.JSONDecodeError as e:
        print(f"  ✗ JSON parse error at line {e.lineno}, col {e.colno}: {e.msg}")

        # Show the problematic line
        lines = plot_str.split('\n')
        if e.lineno <= len(lines):
            error_line = lines[e.lineno - 1]
            print(f"  Error line: {error_line}")
            print(f"  " + " " * (e.colno - 1) + "^")

        # Look for common issues
        if '%' in plot_str:
            print(f"  → Contains placeholders: ", end="")
            import re
            placeholders = re.findall(r'%[A-Z_]+', plot_str)
            print(f"{placeholders}")

        if 'group' in plot_str.lower():
            print(f"  → Contains 'group' field")
            # Find the group field
            import re
            group_matches = re.findall(r'"group":\s*([^,\}]+)', plot_str)
            if group_matches:
                print(f"  → group value: {group_matches}")

print("\n" + "="*80)
print("COMMON PATTERNS:")
print("="*80)

# Check for patterns across all graphs
all_plots = [g.get('plot', '') for g in raw_graphs if g.get('plot')]
group_pattern_count = sum(1 for p in all_plots if 'group' in p.lower())
print(f"Graphs with 'group' field: {group_pattern_count}/{len(all_plots)}")

# Show one example of a failing plot
for idx, graph in enumerate(raw_graphs):
    plot_str = graph.get('plot', '[]')
    if plot_str and plot_str.strip() != '[]':
        try:
            json.loads(plot_str)
        except:
            print(f"\nExample failing plot (graph {idx}):")
            print(plot_str)
            break
