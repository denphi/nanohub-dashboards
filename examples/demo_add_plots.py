"""
Example: Add new plots to dashboard zones

Shows how to add new graphs/plots to specific zones in the dashboard.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import nanohubremote as nr
from nanohubdashboard import Dashboard, Graph

def main():
    print("="*70)
    print("ADD PLOTS DEMO")
    print("="*70)

    # 1. Create session
    print("\n1. Creating session...")
    # TODO: Add your authentication credentials here
    # Example:
    # auth_data = {
    #     "grant_type": "personal_token",
    #     "token": "your_token_here",
    # }
    auth_data = {}
    session = nr.Session(auth_data, url="https://dev.nanohub.org/api")
    print("   ✓ Session created")

    # 2. Load dashboard
    print("\n2. Loading dashboard...")
    dashboard = Dashboard(session)
    dashboard.load(dashboard_id=8)
    print(f"   ✓ Loaded: {dashboard}")

    # 3. Find COLUMN zones
    print("\n3. Finding COLUMN zones...")
    column_zones = set()
    for graph in dashboard.graphs:
        if "COLUMN" in graph.zone:
            column_zones.add(graph.zone)
    
    print(f"   ✓ Found zones: {column_zones}")

    # 4. Add new graphs to these zones
    print("\n4. Adding new graphs...")
    
    for zone in column_zones:
        print(f"   Adding graphs to {zone}...")
        
        # Create a new bar chart
        bar_graph = Graph(
            query="_tbl.users", # Using an existing query for data
            plot_type="bar",
            zone=zone,
            priority=10, # Show after existing graphs
            plot_config={
                "type": "bar",
                "x": "%DATE",
                "y": "%TOTAL_MONTH",  # Use actual column name
                "name": f"New Bar in {zone}"
            },
            layout_config={
                "title": f"New Bar Chart ({zone})"
            }
        )
        bar_graph.id = f"new_bar_{zone}"
        dashboard.add_graph(bar_graph)
        
        # Create a new scatter plot
        scatter_graph = Graph(
            query="_tbl.resources",
            plot_type="scatter",
            zone=zone,
            priority=11,
            plot_config={
                "type": "scatter",
                "mode": "lines+markers",
                "x": "%DATE",
                "y": "%TOTAL_MONTH",  # Use actual column name
                "name": f"New Scatter in {zone}"
            },
            layout_config={
                "title": f"New Scatter Plot ({zone})"
            }
        )
        scatter_graph.id = f"new_scatter_{zone}"
        dashboard.add_graph(scatter_graph)

    print(f"   ✓ Added {len(column_zones) * 2} new graphs")
    print(f"   Total graphs: {len(dashboard.graphs)}")

    # 5. Visualize
    print("\n5. Generating visualization...")
    output_file = dashboard.visualize(
        output_file="dashboard_add_plots.html",
        open_browser=True
    )
    print(dashboard.preview(open_browser=True))

    print(f"\n{'='*70}")
    print(f"✓ DONE! Dashboard saved to: {output_file}")
    print(f"{'='*70}")
 
    try:
        dashboard.save()
        print("   ✓ Dashboard uploaded successfully")
    except Exception as e:
        print(f"   ✗ Failed to upload dashboard: {e}")

if __name__ == "__main__":
    main()
