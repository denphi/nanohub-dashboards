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

    # Visualize
    print("\n6. Generating visualization...")
    output_file = dashboard.visualize(
        output_file="dashboard_demo.html",
        open_browser=True
    )
    
    print(dashboard.preview(open_browser=True))
    print(f"\n{'='*70}")
    print(f"\n{'='*70}")
    print(f"✓ DONE! Dashboard saved to: {output_file}")
    print(f"{'='*70}")
    
    # Save back to server
    print("\n7. Uploading dashboard to server...")
    try:
        dashboard.save()
        print("   ✓ Dashboard uploaded successfully")
    except Exception as e:
        print(f"   ✗ Failed to upload dashboard: {e}")

    print("\nAll bar plots are now scatter, all scatter are now bar!")
    

if __name__ == "__main__":
    main()
