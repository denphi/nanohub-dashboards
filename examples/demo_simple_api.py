"""
Example: Clean demonstration of the simple OO API

Shows how to load and manipulate dashboard plots using the simple API.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import nanohubremote as nr
from nanohubdashboard import Dashboard


def main():
    """Demonstrate the simple API for plot manipulation."""

    print("="*70)
    print("SIMPLE DASHBOARD MANIPULATION API DEMO")
    print("="*70)

    # Create session
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

    # Load the dashboard
    print("\n2. Loading dashboard...")
    dashboard = Dashboard(session)
    dashboard.load(dashboard_id=8)
    print(f"   ✓ Loaded: {dashboard}")

    # Print summary
    print("\n3. Dashboard summary:")
    dashboard.print_graphs()

    # Example: Swap all bar and scatter plots
    print("\n4. Swapping all bar ↔ scatter plots...")
    dashboard.swap_all_bar_scatter()
    print("   ✓ Done")

    # Show a few examples
    print("\n5. Examples of modified plots:")
    for i in [9, 10, 11]:
        try:
            graph = dashboard.get_graph(i)
            print(f"   Graph {i}: {[p.type for p in graph.plots]}")
        except IndexError:
            print(f"   Graph {i}: Not found")

    # Visualize
    print("\n6. Generating visualization...")
    output_file = dashboard.visualize(
        output_file="dashboard_demo.html",
        open_browser=True
    )
    
    print(dashboard.preview(open_browser=True))
    print(f"\n{'='*70}")
    print(f"✓ DONE! Dashboard saved to: {output_file}")
    print(f"{'='*70}")
    print("\nAll bar plots are now scatter, all scatter are now bar!")
    

if __name__ == "__main__":
    main()
