"""
API client for interacting with nanoHUB dashboard API.

Uses nanohub-remote for authentication.
"""

import requests
from typing import Dict, List, Optional, Any
from pathlib import Path
import json
import re
import os
from xml.dom import minidom

def _is_jupyter_notebook():
    """Check if running in Jupyter Notebook (not JupyterLab)."""
    try:
        from IPython import get_ipython
        ipython = get_ipython()
        if ipython is None:
            return False
        # Check if we're in a notebook environment
        if 'IPKernelApp' not in ipython.config:
            return False
        # Try to detect if it's classic notebook vs lab
        # In classic notebook, ZMQInteractiveShell is used
        # In JupyterLab, the same shell is used but we can check for lab-specific features
        shell_name = ipython.__class__.__name__
        if shell_name == 'ZMQInteractiveShell':
            # Try to import notebook-specific modules
            try:
                import notebook
                # If we can import notebook and we're in IPython, assume classic notebook
                # unless we detect JupyterLab
                return True
            except ImportError:
                return False
        return False
    except:
        return False

def _is_jupyterlab():
    """Check if running in JupyterLab."""
    try:
        from IPython import get_ipython
        ipython = get_ipython()
        if ipython is None:
            return False
        # Check if we're in a notebook environment
        if 'IPKernelApp' not in ipython.config:
            return False
        # Try to detect JupyterLab by checking for jupyterlab package
        try:
            import jupyterlab
            return True
        except ImportError:
            # Fallback: if we're in IPython but not classic notebook, assume lab
            return not _is_jupyter_notebook()
    except:
        return False

def _display_in_jupyter(file_path, height=800):
    """Display HTML file in Jupyter using iframe or new tab."""
    try:
        from IPython.display import IFrame, display
        import webbrowser

        if _is_jupyter_notebook():
            # Use iframe for classic Jupyter Notebook
            display(IFrame(src=file_path, width='100%', height=height))
        elif _is_jupyterlab():
            # Open in new tab for JupyterLab
            webbrowser.open(f'file://{os.path.abspath(file_path)}')
        else:
            # Fallback to iframe for other IPython environments
            display(IFrame(src=file_path, width='100%', height=height))
        return True
    except ImportError:
        return False

def _display_html_in_jupyter(file_path):
    """Display HTML content directly in Jupyter (for forms with hidden parameters)."""
    try:
        from IPython.display import HTML, display
        import webbrowser

        if _is_jupyter_notebook():
            # Read and display HTML directly for forms to work
            with open(file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            display(HTML(html_content))
        elif _is_jupyterlab():
            # Open in new tab for JupyterLab
            webbrowser.open(f'file://{os.path.abspath(file_path)}')
        else:
            # Fallback to HTML display for other IPython environments
            with open(file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            display(HTML(html_content))
        return True
    except ImportError:
        return False

try:
    from nanohubremote import Session
    NANOHUB_REMOTE_AVAILABLE = True
except ImportError:
    NANOHUB_REMOTE_AVAILABLE = False
    Session = None

from .config import DashboardConfig
from .query import Query
from .graph import Graph
from .exceptions import APIError, AuthenticationError, DataSourceError, QueryError
from .datasource import DataSource


class DashboardClient:
    """
    Client for interacting with the nanoHUB Dashboard API.
    
    Provides methods for:
    - Dashboard CRUD operations
    - Data source upload/download
    - Data source querying
    
    Uses nanohub-remote Session for authentication.
    """

    def __init__(self, session: Optional[Any] = None, base_url: str = "https://nanohub.org"):
        """
        Initialize the Dashboard API client.

        Args:
            session: nanohub-remote Session object for authentication.
                    If None, creates a new session.
            base_url: Base URL for the nanoHUB instance

        Raises:
            ImportError: If nanohub-remote is not installed
        """
        if not NANOHUB_REMOTE_AVAILABLE:
            raise ImportError(
                "nanohub-remote is required for API access. "
                "Install it with: pip install nanohub-remote"
            )

        self.session = session or Session()
        self.base_url = base_url.rstrip('/')
        self.api_base = f"{self.base_url}/api/dashboards"
        self._plot_transformer = None

    def _fix_json_placeholders(self, json_str: str) -> str:
        """
        Fix unquoted placeholders in JSON strings.
        
        Converts: {"key": %PLACEHOLDER} -> {"key": "%PLACEHOLDER"}
        Handles uppercase, lowercase, and list contexts.
        """
        # Match colon, comma, or open bracket, followed by optional whitespace, then the placeholder
        # We capture the delimiter in group 1 and the placeholder in group 2
        # Regex explanation:
        # ([:\[,])       - Capture group 1: match :, [, or ,
        # \s*            - Match zero or more whitespace characters
        # (%[a-zA-Z0-9_]+) - Capture group 2: match % followed by alphanumeric/underscore
        return re.sub(r'([:\[,])\s*(%[a-zA-Z0-9_]+)', r'\1 "\2"', json_str)

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Make an authenticated API request.
        
        Args:
            method: HTTP method (GET, POST, DELETE, etc.)
            endpoint: API endpoint path
            **kwargs: Additional arguments for requests
            
        Returns:
            Response JSON data
            
        Raises:
            APIError: If request fails
            AuthenticationError: If authentication fails
        """
        # Build full endpoint path
        full_endpoint = f"dashboards/{endpoint}"

        try:
            # Use nanohub-remote session methods
            # Use nanohub-remote session methods
            # Handle JSON serialization manually to ensure compatibility
            if 'json' in kwargs:
                import json
                kwargs['data'] = json.dumps(kwargs.pop('json'))
                headers = kwargs.get('headers', {})
                headers['Content-Type'] = 'application/json'
                kwargs['headers'] = headers

            if method.upper() == 'GET':
                response = self.session.requestGet(full_endpoint, **kwargs)
            elif method.upper() in ['POST', 'PUT', 'PATCH']:
                response = self.session.requestPost(full_endpoint, **kwargs)
            elif method.upper() == 'DELETE':
                response = self.session.requestDelete(full_endpoint, **kwargs)
            else:
                raise APIError(f"Unsupported HTTP method: {method}")

            # Check for authentication errors
            if response.status_code == 403:
                raise AuthenticationError(
                    "Authentication failed or insufficient permissions")

            # Check for other errors
            if response.status_code >= 400:
                error_msg = f"API request failed with status {response.status_code}"
                try:
                    error_data = response.json()
                    if 'error' in error_data:
                        error_msg = error_data['error']
                    elif 'message' in error_data:
                        error_msg = error_data['message']
                except:
                    try:
                        error_msg = f"API request failed with status {response.status_code}: {response.text[:200]}"
                    except:
                        pass
                raise APIError(
                    error_msg, status_code=response.status_code, response=response)

            # Return JSON response
            return response.json()

        except Exception as e:
            if isinstance(e, (APIError, AuthenticationError)):
                raise
            raise APIError(f"Request failed: {e}")

    # Dashboard CRUD Operations

    def list_dashboards(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        List dashboards accessible to the authenticated user.
        
        Args:
            filters: Optional filters (group_id, state, created_by, etc.)
            
        Returns:
            List of dashboard metadata dictionaries
        """
        params = filters or {}
        return self._make_request('GET', 'dashboard/list', params=params)

    def get_dashboard(self, dashboard_id: int) -> DashboardConfig:
        """
        Get full dashboard details.
        
        Args:
            dashboard_id: Dashboard ID
            
        Returns:
            DashboardConfig object
        """
        data = self._make_request('GET', f'dashboard/read/{dashboard_id}')
        # API returns {"dashboard": {...}}, extract the dashboard object
        dashboard_data = data.get('dashboard', data)
        return DashboardConfig.from_dict(dashboard_data)

    def create_dashboard(self, dashboard: DashboardConfig) -> int:
        """
        Create a new dashboard.
        
        Args:
            dashboard: DashboardConfig object
            
        Returns:
            ID of created dashboard
        """
        data = dashboard.to_dict()
        response = self._make_request('POST', 'dashboard/create', json=data)
        return response.get('id')

    def update_dashboard(self, dashboard_id: int, dashboard: DashboardConfig) -> bool:
        """
        Update an existing dashboard.

        Args:
            dashboard_id: Dashboard ID to update
            dashboard: DashboardConfig object with updated data

        Returns:
            True if successful
        """
        data = dashboard.to_dict()

        # Encode as JSON
        json_data = json.dumps(data)

        # Construct the full URL
        site_url = f"{self.session.url}/dashboards/dashboard/update/{dashboard_id}"

        # Prepare headers with authentication
        headers = dict(self.session.headers)
        headers['Content-Type'] = 'application/json'

        # Make direct POST request with explicit headers (same pattern as preview_dashboard)
        import requests
        response = requests.post(site_url, data=json_data, headers=headers)

        # Check for errors
        if response.status_code >= 400:
            error_msg = f"Update request failed with status {response.status_code}"
            try:
                error_data = response.json()
                if 'error' in error_data:
                    error_msg = error_data['error']
                elif 'message' in error_data:
                    error_msg = error_data['message']
            except:
                try:
                    error_msg = f"Update request failed with status {response.status_code}: {response.text[:200]}"
                except:
                    pass
            raise APIError(
                error_msg, status_code=response.status_code, response=response)

        return True

    def delete_dashboard(self, dashboard_id: int) -> bool:
        """
        Delete a dashboard.
        
        Args:
            dashboard_id: Dashboard ID to delete
            
        Returns:
            True if successful
        """
        self._make_request('DELETE', f'dashboard/delete/{dashboard_id}')
        return True

    # Data Source Operations

    def upload_datasource(self, datasource_id: int, token: str,
                          db_file: str, format: str = "sqlite") -> bool:
        """
        Upload a SQLite database file to a data source.
        
        Args:
            datasource_id: Data source ID
            token: Authentication token for the data source
            db_file: Path to SQLite database file
            format: Database format (currently only "sqlite" supported)
            
        Returns:
            True if successful
            
        Raises:
            DataSourceError: If upload fails
        """
        if not Path(db_file).exists():
            raise DataSourceError(f"Database file not found: {db_file}")

        with open(db_file, 'rb') as f:
            files = {'file': f}
            data = {
                'id': datasource_id,
                'token': token,
                'format': format
            }

            try:
                response = self._make_request('POST', 'datasource/update',
                                              data=data, files=files)
                return response.get('status') == 'OK'
            except APIError as e:
                raise DataSourceError(f"Upload failed: {e}")

    def download_datasource(self, datasource_id: int, token: str,
                            output_path: str) -> bool:
        """
        Download a SQLite database file from a data source.
        
        Args:
            datasource_id: Data source ID
            token: Authentication token for the data source
            output_path: Path where to save the downloaded file
            
        Returns:
            True if successful
            
        Raises:
            DataSourceError: If download fails
        """
        data = {
            'id': datasource_id,
            'token': token
        }

        try:
            url = f"{self.api_base}/datasource/download"
            response = self.session.post(url, data=data, stream=True)

            if response.status_code != 200:
                raise DataSourceError(
                    f"Download failed with status {response.status_code}")

            # Create output directory if needed
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)

            # Write file
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            return True

        except (requests.RequestException, OSError) as e:
            raise DataSourceError(f"Download failed: {e}")

    def query_datasource(self, datasource_id: int, query: str,
                         format: str = "columns") -> Dict[str, Any]:
        """
        Execute a SQL query against a data source.
        
        Args:
            datasource_id: Data source ID
            query: SQL query string (must be SELECT)
            format: Result format ('records', 'split', 'tight', or 'columns')
            
        Returns:
            Query results in the specified format
            
        Raises:
            APIError: If query fails
        """
        data = {
            'query': query,
            'format': format
        }

        return self._make_request('POST', f'datasource/query?id={datasource_id}',
                                  json=data)

    # Template Operations

    def list_templates(self) -> List[Dict[str, Any]]:
        """
        List available dashboard templates.
        
        Returns:
            List of template metadata dictionaries
        """
        return self._make_request('GET', 'template/list')

    def get_template(self, template_id: int) -> Dict[str, Any]:
        """
        Get template details.

        Args:
            template_id: Template ID

        Returns:
            Template data dictionary
        """
        return self._make_request('GET', f'template/read/{template_id}')

    def preview_dashboard(self, datasource_id: int, template_id: int,
                          queries: Optional[Dict[str, Any]] = None,
                          graphs: Optional[List[Dict[str, Any]]] = None,
                          params: Optional[Dict[str, Any]] = None) -> str:
        """
        Preview how a dashboard would be rendered by the server.

        This calls the site controller's preview endpoint directly, which uses the same
        view template as the regular dashboard view. This allows testing dashboard
        configurations before creating or updating them. It renders the dashboard
        HTML and plots without saving anything to the database.

        Args:
            datasource_id: Data source ID to use
            template_id: Template ID to use
            queries: Dictionary of query definitions (default: {})
            graphs: List of graph configurations (default: [])
            params: Dashboard parameters including filtering config (default: {})

        Returns:
            HTML string containing the rendered dashboard

        Raises:
            APIError: If preview fails
            AuthenticationError: If user lacks access to datasource or template
        """
        # Prepare the payload
        payload = {
            'datasource_id': datasource_id,
            'template_id': template_id,
            'queries': json.dumps(queries or {}),
            'graphs': json.dumps(graphs or []),
            'params': json.dumps(params or {})
        }

        # Encode as JSON
        json_data = json.dumps(payload)

        # Get the base URL and construct the site component URL
        # The session URL is typically https://example.com/api
        # We need to post to https://example.com/index.php?option=com_dashboards&controller=dashboards&task=preview
        site_url = f"{self.session.url}/dashboards/dashboard/preview"

        # Prepare headers with authentication
        headers = dict(self.session.headers)
        headers['Content-Type'] = 'application/json'

        # Make direct POST request to site component
        import requests
        response = requests.post(site_url, data=json_data, headers=headers)

        # Check for errors
        if response.status_code >= 400:
            error_msg = f"Preview request failed with status {response.status_code}"
            try:
                error_data = response.json()
                if 'error' in error_data:
                    error_msg = error_data['error']
                elif 'message' in error_data:
                    error_msg = error_data['message']
            except:
                try:
                    error_msg = f"Preview request failed with status {response.status_code}: {response.text}"
                except:
                    pass
            raise APIError(
                error_msg, status_code=response.status_code, response=response)

        # Return raw HTML
        return response.text

    def set_plot_transformer(self, transformer_func):
        """
        Set a custom plot transformer function to modify plots before rendering.

        The transformer function will be called for each plot trace and should:
        - Accept a plot configuration dictionary as input
        - Return a modified plot configuration dictionary

        Args:
            transformer_func: A callable that takes a dict and returns a dict,
                            or None to clear the transformer

        Example:
            def swap_bar_scatter(plot_config):
                if plot_config.get('type') == 'bar':
                    plot_config['type'] = 'scatter'
                    if 'mode' not in plot_config:
                        plot_config['mode'] = 'markers'
                elif plot_config.get('type') == 'scatter':
                    plot_config['type'] = 'bar'
                    plot_config.pop('mode', None)
                return plot_config

            client.set_plot_transformer(swap_bar_scatter)
        """
        self._plot_transformer = transformer_func

    def visualize(self, dashboard_id: int, output_file: Optional[str] = None,
                  open_browser: bool = True, dashboard_config: Optional[DashboardConfig] = None) -> str:
        """
        Fetch and visualize a dashboard from nanoHUB, generating an HTML file.

        This method fetches a dashboard, executes all queries, processes templates,
        and generates a complete HTML file with interactive Plotly visualizations.

        Args:
            dashboard_id: ID of the dashboard to visualize
            output_file: Path to save the HTML file (default: dashboard_{id}.html)
            open_browser: Whether to open the HTML file in a browser (default: True)

        Returns:
            Path to the generated HTML file

        Raises:
            APIError: If dashboard fetch fails
            DataSourceError: If data source queries fail
        """
        # Fetch dashboard - get raw response to access plot templates
        print(f"Fetching dashboard {dashboard_id}...")
        try:
            # Get raw API response
            response = self.session.requestGet(
                f'dashboards/dashboard/read/{dashboard_id}')
            raw_data = response.json()
            dashboard_data = raw_data.get('dashboard', raw_data)

            # Parse dashboard config
            if dashboard_config is None:
                dashboard_config = self.get_dashboard(dashboard_id)
        except Exception as e:
            raise APIError(f"Error fetching dashboard: {e}")

        print(f"✓ Dashboard: {dashboard_config.title}")
        print(f"  Description: {dashboard_config.description}")
        print(f"  Data Source ID: {dashboard_config.datasource_id}")
        print(f"  Template ID: {dashboard_config.template_id}")

        # Check if dashboard has data
        if not dashboard_config.datasource_id:
            print("\n⚠ Dashboard has no data source configured")
            # Still create HTML with no data
            html_content = self._create_empty_dashboard_html(dashboard_config)
            output_file = output_file or f"dashboard_{dashboard_id}.html"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"✓ Dashboard saved to {output_file}")
            if open_browser:
                import webbrowser
                webbrowser.open(f'file://{os.path.abspath(output_file)}')
            return output_file

        # Fetch template
        template_xml = None
        if dashboard_config.template_id:
            print(f"\nFetching template {dashboard_config.template_id}...")
            try:
                template_response = self.session.requestGet(
                    f'dashboards/template/read/{dashboard_config.template_id}')
                template_data = template_response.json().get('template', {})
                template_xml = template_data.get('description', '')
                print(
                    f"✓ Template loaded: {template_data.get('title', 'Unknown')}")
            except Exception as e:
                print(f"⚠ Warning: Could not fetch template: {e}")
                print(f"  Will use default grid layout")

        # Parse queries and graphs
        queries = dashboard_config.queries
        graphs = dashboard_config.graphs

        # Parse raw graphs data to get plot templates
        raw_graphs = json.loads(dashboard_data.get('graphs', '[]'))

        print(f"\nQueries: {len(queries)}")
        print(f"Graphs: {len(graphs)}")

        # Create data source connection
        ds = DataSource(
            datasource_id=dashboard_config.datasource_id,
            session=self.session,
            base_url=self.base_url
        )

        # Execute queries and store results
        query_results = {}
        for query in queries:
            # Handle both Query objects and dict format
            if hasattr(query, 'name'):
                query_name = query.name
                query_sql = query.sql
            else:
                query_name = str(query)
                query_sql = str(query)

            print(f"\nExecuting query '{query_name}'...")
            try:
                results = ds.query(query_sql, format="columns")
                query_results[query_name] = results
                print(
                    f"  ✓ Retrieved {len(next(iter(results.values())))} rows" if results else "  ✓ Query executed")
            except Exception as e:
                print(f"  ✗ Error: {e}")
                query_results[query_name] = {}

        # Also fetch data from raw tables referenced by _tbl. queries
        for graph in graphs:
            if graph.query.startswith('_tbl.'):
                table_name = graph.query.replace('_tbl.', '')
                table_key = f"_TABLE_{table_name.upper()}"
                if table_name and table_key not in query_results:
                    print(f"\nFetching raw table data for '{table_name}'...")
                    try:
                        # Simple SELECT * without ORDER BY, matching server behavior
                        # Server uses: SourceModel::setQuery($c, "SELECT * from " . $k)
                        table_results = ds.query(
                            f"SELECT * FROM `{table_name}`", format="columns")
                        query_results[table_key] = table_results
                        print(
                            f"  ✓ Retrieved {len(next(iter(table_results.values())))} rows" if table_results else "  ✓ Query executed")
                    except Exception as e:
                        print(f"  ✗ Error fetching table {table_name}: {e}")
                        query_results[table_key] = {}

        # Parse template XML and create HTML structure
        print(f"\nProcessing template...")
        html_template, zones, dom = self._process_template(template_xml)

        # Sort graphs by priority
        sorted_graphs = sorted(
            graphs, key=lambda g: g.priority if hasattr(g, 'priority') else 0)

        print(f"\nCreating visualization with {len(sorted_graphs)} graphs...")

        # Prepare plots data and get updated HTML template
        plots, html_template = self._process_graphs(
            sorted_graphs, raw_graphs, query_results, zones, dom)

        # Create complete HTML page with template and plots
        print(f"\n✓ Creating HTML output...")
        html_content = self._create_dashboard_html(
            dashboard_config, html_template, plots)

        # Save to file
        output_file = output_file or f"dashboard_{dashboard_id}.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"✓ Dashboard saved to {output_file}")

        # Open in browser or display in Jupyter
        if open_browser:
            # Try Jupyter display first
            if not _display_in_jupyter(output_file):
                # Fallback to regular browser for non-Jupyter environments
                print("Opening in browser...")
                import webbrowser
                webbrowser.open(f'file://{os.path.abspath(output_file)}')

        return output_file

    def _create_empty_dashboard_html(self, dashboard_config: DashboardConfig) -> str:
        """Create HTML for a dashboard with no data source."""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{dashboard_config.title}</title>
    <link rel="stylesheet" href="https://nanohub.org/app/cache/site/site.css">
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background-color: white;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            margin: 0 0 10px 0;
            color: #333;
        }}
        .warning {{
            background-color: #fff3cd;
            color: #856404;
            padding: 15px;
            border-radius: 8px;
            border: 1px solid #ffeaa7;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{dashboard_config.title}</h1>
        <p>{dashboard_config.description}</p>
    </div>
    <div class="warning">
        <strong>No Data Source:</strong> This dashboard has no data source configured.
    </div>
</body>
</html>
"""

    def _process_template(self, template_xml: Optional[str]) -> tuple:
        """Process template XML and return HTML template, zones, and DOM."""
        if template_xml:
            try:
                dom = minidom.parseString(template_xml)
                zones = {}

                # Replace <template> tags with <div> tags
                for template_elem in dom.getElementsByTagName('template'):
                    zone_id = template_elem.getAttribute('id')
                    if zone_id:
                        # Create a new div element
                        div_elem = dom.createElement('div')
                        # Copy all attributes
                        for i in range(template_elem.attributes.length):
                            attr = template_elem.attributes.item(i)
                            div_elem.setAttribute(attr.name, attr.value)
                        div_elem.setAttribute('class', f'zone zone-{zone_id}')
                        # Replace template with div
                        template_elem.parentNode.replaceChild(
                            div_elem, template_elem)
                        zones[zone_id] = div_elem

                # Don't convert to HTML yet - return the DOM for modification
                print(f"✓ Template parsed with {len(zones)} zones")
                return None, zones, dom
            except Exception as e:
                print(f"⚠ Warning: Could not parse template XML: {e}")

        # Default grid layout
        html_template = '<div id="main" style="display:grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 20px;"></div>'
        zones = {'main': None}
        return html_template, zones, None

    def _process_graphs(self, sorted_graphs: List, raw_graphs: List,
                        query_results: Dict, zones: Dict, dom) -> tuple:
        """Process graphs and return plots data and updated HTML template."""
        plots = {}
        html_template = None
        plot_counter = 0  # Separate counter for plot IDs

        for idx, graph in enumerate(sorted_graphs):
            query_name = graph.query
            zone_name = graph.zone if hasattr(graph, 'zone') else 'main'

            # Get the raw graph data
            if hasattr(graph, 'index') and isinstance(graph.index, int) and 0 <= graph.index < len(raw_graphs):
                raw_graph = raw_graphs[graph.index]
            else:
                raw_graph = {}

            # Check if this is an HTML graph
            html_content = ""
            if hasattr(graph, 'html') and graph.html:
                html_content = graph.html
            else:
                html_content = raw_graph.get('html', '').strip()

            if html_content:
                if dom and zone_name in zones and zones[zone_name] is not None:
                    try:
                        html_div = dom.createElement('div')
                        html_div.setAttribute('id', f'_html_{idx}')
                        html_div.setAttribute(
                            'class', 'dashboards-html-content')
                        zones[zone_name].appendChild(html_div)

                        plots[f'_html_{idx}'] = {
                            'html': html_content,
                            'zone': zone_name
                        }
                        print(f"  ✓ Added HTML content in zone '{zone_name}'")
                    except Exception as e:
                        print(f"  ⚠ Error adding HTML content: {e}")
                else:
                    # No DOM, store plot data for JavaScript to create
                    plots[f'_html_{idx}'] = {
                        'html': html_content,
                        'zone': zone_name
                    }
                continue

            # Strip prefix from query name
            if query_name.startswith('_tbl.'):
                table_name = query_name.replace('_tbl.', '')
                actual_query_name = f"_TABLE_{table_name.upper()}"
            elif '.' in query_name:
                actual_query_name = query_name.split('.', 1)[1].upper()
            else:
                actual_query_name = query_name.upper()

            if actual_query_name not in query_results or not query_results[actual_query_name]:
                print(
                    f"  ⚠ Skipping graph {idx+1}: no data for query '{query_name}' (looked for '{actual_query_name}')")
                continue

            data = query_results[actual_query_name]

            # Get plot template
            # Check if the graph object has plots
            if hasattr(graph, 'plots') and graph.plots:
                # Use the plot configs from graph.plots (which may have been modified)
                # The placeholders are preserved in these configs
                plot_templates = [p.config for p in graph.plots]
            # Then check if it has plot_config directly
            elif hasattr(graph, 'plot_config') and graph.plot_config:
                # If it's a dict, wrap in list
                if isinstance(graph.plot_config, dict):
                    plot_templates = [graph.plot_config]
                elif isinstance(graph.plot_config, list):
                    plot_templates = graph.plot_config
                else:
                    plot_templates = []
            else:
                # Fallback to raw graph data
                plot_template_str = raw_graph.get('plot', '[]')

                # Parse plot template and replace placeholders
                try:
                    fixed_template = re.sub(
                        r':\s*(%[A-Z_]+)', r': "\1"', plot_template_str)
                    fixed_template = re.sub(
                        r',\s*(%[A-Z_]+)', r', "\1"', fixed_template)
                    plot_templates = json.loads(fixed_template)
                except Exception as e:
                    print(
                        f"  ⚠ Warning: Could not parse plot template for graph {idx+1}: {e}")
                    continue

            if not plot_templates:
                print(f"  ⚠ Skipping graph {idx+1}: no plot template")
                continue

            # Process and replace placeholders in templates
            # Check for grouping
            group_field = None
            if hasattr(graph, 'group') and graph.group:
                # Strip _tbl. prefix if present (matching server logic)
                group_field = graph.group.replace('_tbl.', '')
                # Also strip backticks if present
                group_field = group_field.replace('`', '')

            processed_traces = []
            
            if group_field:
                # Find the group column in data (case-insensitive)
                data_lookup = {k.upper(): k for k in data.keys()}
                actual_group_field = data_lookup.get(group_field.upper())
                
                if actual_group_field and actual_group_field in data:
                    group_values = data[actual_group_field]
                    # Get unique groups while preserving order of first appearance
                    # This matches the PHP renderer behavior which doesn't sort groups
                    seen = set()
                    unique_groups = []
                    for val in group_values:
                        if val not in seen:
                            seen.add(val)
                            unique_groups.append(val)
                    
                    print(f"  ✓ Grouping by '{actual_group_field}': {len(unique_groups)} groups found")
                    
                    # Separate unique traces from regular traces
                    unique_templates = []
                    regular_templates = []

                    for template in plot_templates:
                        if isinstance(template, dict) and template.get('unique') is True:
                            # Keep the template as-is (including 'unique' field)
                            # The unique field will be used for sorting later
                            unique_templates.append(template)
                        else:
                            regular_templates.append(template)
                    
                    # Process regular traces per group
                    unique_processed = False
                    for group_val in unique_groups:
                        # Filter data for this group
                        group_data = {}
                        indices = [i for i, x in enumerate(group_values) if x == group_val]

                        for k, v in data.items():
                            # Special handling for the grouping field itself
                            if k.upper() == actual_group_field.upper():
                                # For the grouping field, use the group value as a scalar string
                                # This ensures that name fields like "name": %toolname show the group name
                                # instead of an array of repeated values
                                group_data[k] = group_val
                            elif isinstance(v, list) and len(v) == len(group_values):
                                group_data[k] = [v[i] for i in indices]
                            else:
                                # Keep scalar values or non-matching lists as is
                                group_data[k] = v

                        # Process templates with filtered data
                        group_traces = self._process_plot_templates(
                            regular_templates, group_data, graph)
                            
                        # Inject the group value into the trace for reference
                        for trace in group_traces:
                            trace['_group'] = group_val
                            
                        processed_traces.extend(group_traces)
                        
                        # Process unique traces only once (on first iteration)
                        if not unique_processed and unique_templates:
                            unique_traces = self._process_plot_templates(
                                unique_templates, data, graph)
                            # Mark as unique for menu visibility
                            for trace in unique_traces:
                                trace['_unique'] = True
                            processed_traces.extend(unique_traces)
                            unique_processed = True
                else:
                    print(f"  ⚠ Warning: Group field '{group_field}' not found in data")
                    # Fallback to no grouping
                    processed_traces = self._process_plot_templates(
                        plot_templates, data, graph)
            else:
                # No grouping
                processed_traces = self._process_plot_templates(
                    plot_templates, data, graph)

            # Sort traces if grouping is enabled: non-unique first, unique last
            # This matches the PHP renderer logic (renderer.php lines 171-177)
            if group_field:
                processed_traces.sort(key=lambda trace: trace.get('unique', False))

            # Check for group menu
            if processed_traces and (hasattr(graph, 'group-menu') or hasattr(graph, 'group_menu')):
                is_menu_enabled = getattr(graph, 'group-menu', getattr(graph, 'group_menu', False))
                
                if is_menu_enabled and group_field:
                    # Generate updatemenus
                    buttons = []
                    
                    # Get unique groups from traces
                    # We stored _group in traces during grouping
                    unique_groups = []
                    seen_groups = set()
                    for trace in processed_traces:
                        if '_group' in trace:
                            grp = trace['_group']
                            if grp not in seen_groups:
                                unique_groups.append(grp)
                                seen_groups.add(grp)
                    
                    # Sort groups if possible
                    try:
                        unique_groups.sort()
                    except:
                        pass
                        
                    # Create buttons
                    for i, group_val in enumerate(unique_groups):
                        # Create visibility array
                        visible = []
                        for trace in processed_traces:
                            if '_group' in trace and trace['_group'] == group_val:
                                visible.append(True)
                            else:
                                visible.append(False)
                                
                        buttons.append({
                            "args": [{"visible": visible}],
                            "label": f"{group_field} - {group_val}",
                            "method": "update"
                        })
                        
                    # Set initial visibility (first group visible, others hidden)
                    if unique_groups:
                        first_group = unique_groups[0]
                        for trace in processed_traces:
                            if '_group' in trace:
                                if trace['_group'] == first_group:
                                    trace['visible'] = True
                                else:
                                    trace['visible'] = False
                    
                    # Add updatemenus to layout
                    updatemenus = [{
                        "buttons": buttons,
                        "direction": "down",
                        "x": getattr(graph, 'group-x', 0.5),
                        "y": getattr(graph, 'group-y', 1.0),
                        "bgcolor": "white"
                    }]
                    
                    # We need to inject this into the layout
                    # We'll do it when creating the plot dict below
                    graph.updatemenus = updatemenus

            if processed_traces:
                # Store plot data
                plot_id = f'_plot_{plot_counter}'

                # Use graph.layout_config if available, otherwise fall back to raw_graph
                if hasattr(graph, 'layout_config') and graph.layout_config:
                    layout_config = graph.layout_config
                else:
                    layout_str = raw_graph.get('layout', '{}')
                    try:
                        layout_config = json.loads(layout_str)
                    except:
                        layout_config = {}
                
                # Inject updatemenus if present
                if hasattr(graph, 'updatemenus'):
                    layout_config['updatemenus'] = graph.updatemenus
                    
                layout_str = json.dumps(layout_config)

                # Clean up metadata fields before serializing traces
                clean_traces = []
                for trace in processed_traces:
                    clean_trace = {k: v for k, v in trace.items() if not k.startswith('_')}
                    clean_traces.append(clean_trace)

                plots[plot_id] = {
                    'plot': json.dumps(clean_traces),
                    'layout': layout_str,
                    'zone': zone_name
                }

                # Add plot div to the appropriate zone in template
                if dom and zone_name in zones and zones[zone_name] is not None:
                    try:
                        plot_div = dom.createElement('div')
                        plot_div.setAttribute('id', plot_id)
                        plot_div.setAttribute('class', 'dashboards-plot')
                        zones[zone_name].appendChild(plot_div)
                    except Exception as e:
                        print(
                            f"  ⚠ Warning: Could not add plot div to zone: {e}")

                print(
                    f"  ✓ Added {len(processed_traces)} trace(s) for '{query_name}' in zone '{zone_name}'")
                plot_counter += 1  # Increment counter after creating plot
            else:
                print(
                    f"  ⚠ Warning: Graph {idx+1} ({query_name}) produced no valid traces - check field names")

        # Convert DOM back to HTML if we have a template
        if dom:
            try:
                html_template = dom.toxml()
                html_template = re.sub(r'<\?xml[^>]+\?>', '', html_template)
                html_template = re.sub(
                    r'<div([^>]*)\/>', r'<div\1></div>', html_template)
                # Remove CDATA sections - browsers don't understand them in HTML
                # CDATA is XML-specific and causes CSS/JS to be ignored in HTML documents
                html_template = re.sub(r'<!\[CDATA\[', '', html_template)
                html_template = re.sub(r'\]\]>', '', html_template)
            except Exception as e:
                print(f"  ⚠ Warning: Could not convert DOM to HTML: {e}")

        return plots, html_template

    def _process_plot_templates(self, plot_templates: List, data: Dict, graph: Optional[Graph] = None) -> List:
        """Process plot templates and replace placeholders with actual data."""
        processed_traces = []

        for idx, trace_template in enumerate(plot_templates):
            # Make a copy to avoid modifying the original
            trace_config = json.loads(json.dumps(trace_template))

            # Apply custom plot transformer if set
            if hasattr(self, '_plot_transformer') and callable(self._plot_transformer):
                # Pass config, graph, and index to transformer
                trace_config = self._plot_transformer(trace_config, graph, idx)

            # Replace placeholders with actual data
            trace_str = json.dumps(trace_config)

            # Find all placeholders like %FIELD_NAME (case-insensitive)
            placeholders = re.findall(r'%([a-zA-Z0-9_]+)', trace_str)

            # Create a case-insensitive lookup for data fields
            data_lookup = {k.upper(): k for k in data.keys()}

            for placeholder in placeholders:
                field_name_upper = placeholder.upper()

                # Try to find the field in data (case-insensitive)
                if field_name_upper in data_lookup:
                    actual_field_name = data_lookup[field_name_upper]
                    field_data = data[actual_field_name]

                    # Determine the value to use based on the data type
                    if isinstance(field_data, (str, int, float, bool, type(None))):
                        # Scalar value - use as-is (common for group fields in grouped traces)
                        value = field_data
                    elif isinstance(field_data, list) and len(field_data) > 0:
                        # For single values (like indicators), use the first item
                        if trace_config.get('type') == 'indicator':
                            value = field_data[0]
                        else:
                            value = field_data
                    else:
                        value = field_data

                    # Replace placeholder with actual value
                    trace_str = trace_str.replace(
                        f'"%{placeholder}"', json.dumps(value))

            # Check if there are still unreplaced placeholders
            if '%' in trace_str:
                remaining_placeholders = re.findall(r'"%([a-zA-Z0-9_]+)"', trace_str)
                if remaining_placeholders:
                    print(
                        f"  ⚠ Warning: Skipping trace {idx} in graph - missing fields: {remaining_placeholders}")
                    print(f"     Available fields: {list(data.keys())}")
                    continue

            # Parse back to dict
            try:
                trace_config = json.loads(trace_str)
                processed_traces.append(trace_config)
            except:
                print(
                    f"  ⚠ Warning: Could not parse trace after placeholder replacement")
                continue

        return processed_traces

    def _create_dashboard_html(self, dashboard_config: DashboardConfig,
                               html_template: str, plots: Dict) -> str:
        """Create complete HTML page with template and plots."""
        # Get base URL from session
        base_url = self.session.url.replace('/api', '') if hasattr(self.session, 'url') else 'https://nanohub.org'

        # Build HTML in parts to avoid f-string issues with template containing {}
        html_header = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{dashboard_config.title}</title>
    <link rel="stylesheet" type="text/css" media="screen" href="{base_url}/app/cache/site/site.css" />
    <link rel="stylesheet" href="{base_url}/app/components/com_dashboards/site/assets/css/dashboards.css" type="text/css" />
    <link rel="stylesheet" href="{base_url}/app/components/com_dashboards/site/assets/css/pivottable.css" type="text/css" />
    <script src="{base_url}/core/assets/js/jquery.js" type="text/javascript"></script>
    <script src="{base_url}/core/assets/js/jquery.ui.js" type="text/javascript"></script>
    <script src="{base_url}/core/assets/js/jquery.fancybox.js" type="text/javascript"></script>
    <script src="{base_url}/app/components/com_dashboards/site/assets/js/pivottable.min.js" type="text/javascript"></script>
    <script src="{base_url}/app/components/com_dashboards/site/assets/js/plotly.min.js" type="text/javascript"></script>
</head>
<body>

"""

        # Insert template (may contain {} so can't use f-string)
        html_body = html_template if html_template else ""

        html_footer = f"""
    <script>
        // Render all plots and HTML content
        const plots = {json.dumps(plots)};

        for (const [plotId, plotData] of Object.entries(plots)) {{
            let element = document.getElementById(plotId);

            // If element doesn't exist, create it and append to the appropriate zone
            if (!element) {{
                console.log(`Creating element: ${{plotId}} in zone ${{plotData.zone || 'main'}}`);
                const zoneName = plotData.zone || 'main';
                const zoneElement = document.getElementById(zoneName);

                if (zoneElement) {{
                    element = document.createElement('div');
                    element.id = plotId;
                    element.className = plotData.html ? 'dashboards-html-content' : 'dashboards-plot';
                    zoneElement.appendChild(element);
                }} else {{
                    console.error(`Zone not found: ${{zoneName}} for plot ${{plotId}}`);
                    continue;
                }}
            }}

            // Check if this is HTML content
            if (plotData.html) {{
                try {{
                    element.innerHTML = plotData.html;
                    console.log(`Rendered HTML content: ${{plotId}}`);
                }} catch (e) {{
                    console.error(`Error rendering HTML ${{plotId}}:`, e);
                    element.innerHTML = '<p style="color: red;">Error rendering HTML: ' + e.message + '</p>';
                }}
            }}
            // Otherwise it's a Plotly chart
            else if (plotData.plot && plotData.layout) {{
                try {{
                    const data = JSON.parse(plotData.plot);
                    const layout = JSON.parse(plotData.layout);

                    // Set responsive layout
                    layout.autosize = true;
                    layout.margin = layout.margin || {{}};

                    Plotly.newPlot(plotId, data, layout, {{responsive: true}});

                    console.log(`Rendered plot: ${{plotId}}`);
                }} catch (e) {{
                    console.error(`Error rendering plot ${{plotId}}:`, e);
                    element.innerHTML = '<p style="color: red;">Error rendering plot: ' + e.message + '</p>';
                }}
            }} else {{
                console.warn(`Invalid data for: ${{plotId}}`);
            }}
        }}
    </script>
</body>
</html>
"""

        # Combine all parts
        return html_header + html_body + html_footer
