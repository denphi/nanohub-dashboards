#!/usr/bin/env python3
"""
Test the original script that was failing.
"""
import json
import pandas as pd
import nanohubremote as nr
from nanohubdashboard.dashboard import Dashboard
from nanohubdashboard.client import DashboardClient

auth_data = {
    "grant_type": "personal_token",
    "token": "03b43cd742efa6591d24eca3920b652080467680",
}
session = nr.Session(auth_data, url="https://dev.nanohub.org/api")
dashboard = Dashboard(session)
dashboard.load(19)  # Load dashboard with ID 19

print("\n" + "="*80)
print("Testing visualize() method...")
print("="*80)

try:
    t = dashboard.visualize(open_browser=False, output_file="test_dashboard_19.html")
    print(f"\n✓ SUCCESS! Dashboard visualized to: {t}")
except Exception as e:
    print(f"\n✗ FAILED: {e}")
    print("\nTrying preview() as fallback...")
    try:
        t = dashboard.preview(open_browser=False, output_file="test_dashboard_19_preview.html")
        print(f"✓ Preview succeeded: {t}")
    except Exception as e2:
        print(f"✗ Preview also failed: {e2}")
