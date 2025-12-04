#!/usr/bin/env python3
"""
Debug script that shows the exact HTTP requests being sent to the server.
This will print equivalent curl commands for each request.
"""
import json
import nanohubremote as nr
from nanohubdashboard.datasource import DataSource
from nanohubdashboard.client import DashboardClient

# Authentication
auth_data = {
    "grant_type": "personal_token",
    "token": "03b43cd742efa6591d24eca3920b652080467680",
}
session = nr.Session(auth_data, url="https://dev.nanohub.org/api")

print("=" * 80)
print("CURL COMMAND DEBUGGING")
print("=" * 80)

# Print session details
print("\n1. Session Details:")
print(f"   URL: {session.url}")
print(f"   Headers: {json.dumps(dict(session.headers), indent=2)}")

# Test 1: Get dashboard metadata
print("\n2. GET Dashboard Metadata (dashboard 19):")
endpoint = 'dashboards/dashboard/read/19'
full_url = f"{session.url}/{endpoint}"
headers_str = " ".join([f'-H "{k}: {v}"' for k, v in session.headers.items()])

curl_cmd = f"""curl -X GET '{full_url}' \\
  {headers_str}"""
print(f"\n{curl_cmd}\n")

response = session.requestGet(endpoint)
print(f"   Response Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    dashboard_data = data.get('dashboard', data)
    print(f"   Dashboard: {dashboard_data.get('title', 'N/A')}")
    print(f"   Datasource ID: {dashboard_data.get('datasource_id', 'N/A')}")
else:
    print(f"   Error: {response.text[:200]}")

# Test 2: Query datasource directly
print("\n3. POST Query to Datasource (datasource 12):")
datasource_id = 12
endpoint = f'dashboards/datasource/query/{datasource_id}'
full_url = f"{session.url}/{endpoint}"

query_payload = {
    "query": "SELECT 1 as test",
    "format": "columns"
}
payload_json = json.dumps(query_payload)

# Build curl command with data
headers_str = " ".join([f'-H "{k}: {v}"' for k, v in session.headers.items()])

curl_cmd = f"""curl -X POST '{full_url}' \\
  {headers_str} \\
  -H 'Content-Type: application/json' \\
  -d '{payload_json}'"""
print(f"\n{curl_cmd}\n")

response = session.requestPost(endpoint, data=payload_json)
print(f"   Response Status: {response.status_code}")
print(f"   Response: {response.text[:300]}")

# Test 3: Query datasource with actual dashboard query
print("\n4. POST Dashboard Query to Datasource:")
client = DashboardClient(session=session)
dashboard_config = client.get_dashboard(19)

if dashboard_config.queries:
    query = dashboard_config.queries[0]
    query_name = query.name if hasattr(query, 'name') else "Unknown"
    query_sql = query.sql if hasattr(query, 'sql') else str(query)

    print(f"   Query Name: {query_name}")
    print(f"   Query SQL: {query_sql[:100]}...")

    query_payload = {
        "query": query_sql,
        "format": "columns"
    }
    payload_json = json.dumps(query_payload)

    endpoint = f'dashboards/datasource/query/{dashboard_config.datasource_id}'
    full_url = f"{session.url}/{endpoint}"

    curl_cmd = f"""curl -X POST '{full_url}' \\
  {headers_str} \\
  -H 'Content-Type: application/json' \\
  -d '{payload_json}'"""
    print(f"\n{curl_cmd}\n")

    response = session.requestPost(endpoint, data=payload_json)
    print(f"   Response Status: {response.status_code}")
    print(f"   Response: {response.text[:300]}")

# Test 4: Check what method requestPost actually uses
print("\n5. Inspecting session.requestPost implementation:")
print(f"   Session class: {type(session)}")
print(f"   requestPost method: {session.requestPost}")

# Let's manually inspect what happens
import requests

print("\n6. Manual request with explicit headers:")
endpoint = f'dashboards/datasource/query/{datasource_id}'
full_url = f"{session.url}/{endpoint}"

query_payload = {
    "query": "SELECT 1 as test",
    "format": "columns"
}

print(f"   URL: {full_url}")
print(f"   Headers: {json.dumps(dict(session.headers), indent=2)}")
print(f"   Payload: {json.dumps(query_payload, indent=2)}")

# Try with Content-Type header
headers_with_content_type = dict(session.headers)
headers_with_content_type['Content-Type'] = 'application/json'

curl_cmd = f"""curl -X POST '{full_url}' \\"""
for k, v in headers_with_content_type.items():
    curl_cmd += f"\n  -H '{k}: {v}' \\"
curl_cmd += f"\n  -d '{json.dumps(query_payload)}'"

print(f"\nCurl command with Content-Type:\n{curl_cmd}\n")

response = requests.post(full_url, headers=headers_with_content_type, json=query_payload)
print(f"   Response Status: {response.status_code}")
print(f"   Response: {response.text[:300]}")

# Test 5: Check if the issue is with how data is being sent
print("\n7. Testing different data formats:")

# Try with data parameter (string)
print("   a) Using data=json.dumps(payload):")
response = requests.post(full_url, headers=headers_with_content_type, data=json.dumps(query_payload))
print(f"      Response Status: {response.status_code}")
print(f"      Response: {response.text[:200]}")

# Try with json parameter
print("\n   b) Using json=payload:")
response = requests.post(full_url, headers=dict(session.headers), json=query_payload)
print(f"      Response Status: {response.status_code}")
print(f"      Response: {response.text[:200]}")

# Test 6: Check the actual endpoint being called
print("\n8. Verifying endpoint construction:")
print(f"   Session URL: {session.url}")
print(f"   Endpoint: dashboards/datasource/query/{datasource_id}")
print(f"   Full URL: {session.url}/dashboards/datasource/query/{datasource_id}")
print(f"   Expected: https://dev.nanohub.org/api/dashboards/datasource/query/{datasource_id}")

# Test 7: Check if there's a difference in how the client calls it
print("\n9. Testing via DashboardClient._make_request:")
try:
    from nanohubdashboard.client import DashboardClient
    client = DashboardClient(session=session)

    endpoint_path = f'datasource/query/{datasource_id}'
    print(f"   Client endpoint: {endpoint_path}")
    print(f"   Full path: dashboards/{endpoint_path}")

    # This is what the client does internally
    full_endpoint = f"dashboards/{endpoint_path}"
    print(f"   Final URL: {session.url}/{full_endpoint}")

    curl_cmd = f"""curl -X POST '{session.url}/{full_endpoint}' \\"""
    for k, v in session.headers.items():
        curl_cmd += f"\n  -H '{k}: {v}' \\"
    curl_cmd += f"\n  -H 'Content-Type: application/json' \\"
    curl_cmd += f"\n  -d '{json.dumps(query_payload)}'"

    print(f"\nCurl via client path:\n{curl_cmd}\n")

except Exception as e:
    print(f"   Error: {e}")

print("\n" + "=" * 80)
print("ANALYSIS")
print("=" * 80)
print("""
Look at the curl commands above and try running them manually to see which one works.

Key things to check:
1. Is the URL correct? (should be https://dev.nanohub.org/api/dashboards/datasource/query/12)
2. Are the headers correct? (Authorization: Bearer TOKEN)
3. Is the payload format correct? (should be JSON with "query" and "format" fields)
4. Is Content-Type: application/json being sent?

If the manual curl works but the Python code doesn't, there's an issue with how
the request is being constructed in the code.
""")
