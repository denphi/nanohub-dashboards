#!/usr/bin/env python3
"""
Debug script to diagnose dashboard access and query permission issues.

This script helps identify why queries are failing with 403 errors even when
you should have access to the dashboard.
"""
import json
import nanohubremote as nr
from nanohubdashboard.dashboard import Dashboard
from nanohubdashboard.client import DashboardClient
from nanohubdashboard.datasource import DataSource

# Authentication
auth_data = {
    "grant_type": "personal_token",
    "token": "03b43cd742efa6591d24eca3920b652080467680",
}
session = nr.Session(auth_data, url="https://dev.nanohub.org/api")

print("=" * 80)
print("DASHBOARD ACCESS DEBUGGING")
print("=" * 80)

# Step 1: Check session authentication
print("\n1. Checking session authentication...")
print(f"   Session URL: {session.url}")
print(f"   Headers: {dict(session.headers)}")

try:
    # Try a simple API call to verify authentication
    response = session.requestGet('dashboards/dashboard/list')
    if response.status_code == 200:
        print("   ✓ Authentication successful")
        dashboards = response.json()
        print(f"   Found {len(dashboards)} accessible dashboards")
    else:
        print(f"   ✗ Authentication issue: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
except Exception as e:
    print(f"   ✗ Error during authentication check: {e}")

# Step 2: Load dashboard metadata
print("\n2. Loading dashboard 19 metadata...")
client = DashboardClient(session=session)

try:
    dashboard_config = client.get_dashboard(19)
    print(f"   ✓ Dashboard loaded: {dashboard_config.title}")
    print(f"   Description: {dashboard_config.description}")
    print(f"   Data Source ID: {dashboard_config.datasource_id}")
    print(f"   Template ID: {dashboard_config.template_id}")
    print(f"   Number of queries: {len(dashboard_config.queries)}")
    print(f"   Number of graphs: {len(dashboard_config.graphs)}")
    print(f"   Group ID: {getattr(dashboard_config, 'group_id', 'N/A')}")
    print(f"   Created by: {getattr(dashboard_config, 'created_by', 'N/A')}")
    print(f"   State: {getattr(dashboard_config, 'state', 'N/A')}")
except Exception as e:
    print(f"   ✗ Error loading dashboard: {e}")
    exit(1)

# Step 3: Check datasource access directly
print(f"\n3. Testing direct datasource access (ID: {dashboard_config.datasource_id})...")
ds = DataSource(datasource_id=dashboard_config.datasource_id, session=session)

print(f"   Testing simple query: SELECT 1 as test")
try:
    result = ds.query("SELECT 1 as test", format="columns")
    print(f"   ✓ Basic query successful: {result}")
except Exception as e:
    print(f"   ✗ Basic query failed: {e}")
    print(f"   This indicates a datasource permission issue")

# Step 4: Check datasource metadata/info
print(f"\n4. Checking datasource information...")
try:
    # Try to get datasource info
    response = session.requestGet(f'dashboards/datasource/read/{dashboard_config.datasource_id}')
    if response.status_code == 200:
        ds_info = response.json()
        print(f"   ✓ Datasource info retrieved")
        print(f"   Datasource: {json.dumps(ds_info, indent=2)}")
    else:
        print(f"   ✗ Could not retrieve datasource info: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
except Exception as e:
    print(f"   ✗ Error getting datasource info: {e}")

# Step 5: Test each query individually
print(f"\n5. Testing individual queries...")
for i, query in enumerate(dashboard_config.queries):
    query_name = query.name if hasattr(query, 'name') else f"Query {i}"
    query_sql = query.sql if hasattr(query, 'sql') else str(query)

    print(f"\n   Query: {query_name}")
    print(f"   SQL: {query_sql[:100]}...")

    try:
        result = ds.query(query_sql, format="columns")
        num_rows = len(next(iter(result.values()))) if result else 0
        print(f"   ✓ Success: {num_rows} rows returned")
    except Exception as e:
        print(f"   ✗ Failed: {e}")

        # Try to get more details about the error
        if "403" in str(e):
            print(f"   → This is a PERMISSION ERROR")
            print(f"   → You may not have direct query access to this datasource")

# Step 6: Check user permissions
print(f"\n6. Checking user information...")
try:
    # Try to get current user info
    response = session.requestGet('users/current')
    if response.status_code == 200:
        user_info = response.json()
        print(f"   ✓ User info retrieved")
        print(f"   User: {json.dumps(user_info, indent=2)}")
    else:
        print(f"   ⚠ Could not retrieve user info: {response.status_code}")
except Exception as e:
    print(f"   ⚠ Error getting user info: {e}")

# Step 7: Check group membership
print(f"\n7. Checking group permissions...")
group_id = getattr(dashboard_config, 'group_id', None)
if group_id:
    print(f"   Dashboard group ID: {group_id}")
    try:
        # Check if user has access to this group
        response = session.requestGet(f'groups/{group_id}/members')
        if response.status_code == 200:
            members = response.json()
            print(f"   ✓ Group members retrieved: {len(members)} members")
        else:
            print(f"   ⚠ Could not retrieve group members: {response.status_code}")
    except Exception as e:
        print(f"   ⚠ Error checking group: {e}")
else:
    print(f"   ⚠ No group ID found for dashboard")

# Step 8: Test preview endpoint
print(f"\n8. Testing preview endpoint (server-side rendering)...")
try:
    # Extract query dict
    queries_dict = {}
    for query in dashboard_config.queries:
        if hasattr(query, 'name') and hasattr(query, 'sql'):
            queries_dict[query.name] = query.sql

    # Extract graphs list
    graphs_list = []
    for graph in dashboard_config.graphs:
        graph_dict = {
            'query': graph.query,
            'zone': graph.zone if hasattr(graph, 'zone') else 'main',
            'priority': graph.priority if hasattr(graph, 'priority') else 0,
        }
        graphs_list.append(graph_dict)

    params_dict = dashboard_config.params if hasattr(dashboard_config, 'params') else {}
    if isinstance(params_dict, str):
        params_dict = json.loads(params_dict) if params_dict else {}

    html_content = client.preview_dashboard(
        datasource_id=dashboard_config.datasource_id,
        template_id=dashboard_config.template_id,
        queries=queries_dict,
        graphs=graphs_list,
        params=params_dict
    )

    if html_content and len(html_content) > 100:
        print(f"   ✓ Preview endpoint successful ({len(html_content)} bytes)")
        print(f"   → This means the SERVER has access to execute queries")
        print(f"   → But YOUR USER may not have direct query permissions")
    else:
        print(f"   ✗ Preview returned empty or small response")
except Exception as e:
    print(f"   ✗ Preview failed: {e}")

# Summary and recommendations
print("\n" + "=" * 80)
print("SUMMARY AND RECOMMENDATIONS")
print("=" * 80)

print("""
If you see:
  ✓ Dashboard loads successfully
  ✗ Direct queries fail with 403
  ✓ Preview endpoint works

Then the issue is:
  - The datasource has restricted query permissions
  - Your user account does not have direct SQL query access
  - However, the server-side rendering (preview) has elevated permissions

SOLUTION:
  Use dashboard.preview() instead of dashboard.visualize()

  Example:
    dashboard = Dashboard(session)
    dashboard.load(19)
    dashboard.preview(open_browser=True)  # Use this
    # NOT: dashboard.visualize(open_browser=True)

ALTERNATIVE:
  If you need direct query access, contact the datasource administrator to:
  - Grant your user account query permissions on datasource {datasource_id}
  - Or make the datasource publicly queryable
""".format(datasource_id=dashboard_config.datasource_id))
