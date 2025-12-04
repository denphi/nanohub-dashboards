from typing import List, Any, Optional
import json
import re
from .client import DashboardClient, _display_html_in_jupyter
from .graph import Graph
from .plot import Plot
from .config import DashboardConfig

class Dashboard:
    """
    Represents a dashboard loaded from the API with all its data.
    
    Provides methods to manipulate plots and visualize the dashboard.
    """

    def __init__(self, session: Any):
        """
        Initialize a Dashboard object.

        Args:
            session: nanohub-remote Session instance
        """
        self.session = session
        self.client = DashboardClient(session=session)
        self.id: Optional[int] = None
        self.config: Optional[DashboardConfig] = None
        self.graphs: List[Graph] = []

    def _safe_json_parse(self, json_str: str, graph_idx: int, field_name: str) -> Any:
        """
        Safely parse JSON with better error handling.
        
        Args:
            json_str: JSON string to parse
            graph_idx: Graph index for error reporting
            field_name: Field name for error reporting
            
        Returns:
            Parsed JSON object, or None if parsing fails
        """
        if not json_str or json_str.strip() in ['', '[]', '{}']:
            return [] if json_str.strip() == '[]' else {}
            
        try:
            # Fix placeholder variables that aren't quoted
            # This regex matches %VARIABLE patterns that appear after : or , but NOT inside quoted strings
            # We need to be careful not to match % inside strings like "%b, %Y" (date formats)
            
            # Strategy: Only quote %VARIABLE if it's not already inside quotes
            # Match pattern: colon/comma followed by whitespace and %WORD (not in quotes)
            # This is a simplified approach - we look for unquoted placeholders
            fixed_str = json_str
            
            # Match ': %variable' or ', %variable' patterns where %variable is not quoted
            # Replace with ': "%variable"' or ', "%variable"'
            def quote_placeholder(match):
                prefix = match.group(1)  # : or ,
                spaces = match.group(2)  # whitespace
                placeholder = match.group(3)  # %variable
                return f'{prefix}{spaces}"{placeholder}"'
            
            # This pattern matches: (: or ,)(whitespace)(%WORD) but only if not already in quotes
            # We check the next character after %WORD - if it's a comma or closing bracket, it's likely unquoted
            fixed_str = re.sub(r'([:,])(\s*)(%[A-Z_a-z0-9]+)(?=\s*[,\]\}])', quote_placeholder, fixed_str)
            
            # Try to parse
            return json.loads(fixed_str)
        except json.JSONDecodeError as e:
            # Provide detailed error information for debugging
            lines = json_str.split('\n')
            error_line = lines[e.lineno - 1] if e.lineno <= len(lines) else "N/A"
            
            # Check if this looks like truncated JSON
            if not json_str.rstrip().endswith(('}', ']', '"')):
                print(f"Warning: Graph {graph_idx} {field_name} appears truncated or incomplete")
            else:
                print(f"Warning: Graph {graph_idx} {field_name} has invalid JSON at line {e.lineno}, col {e.colno}")
                print(f"  Error: {e.msg}")
                if len(error_line) < 100:
                    print(f"  Line: {error_line.strip()}")
            
            return None
        except Exception as e:
            print(f"Warning: Graph {graph_idx} {field_name} parsing failed: {e}")
            return None

    def load(self, dashboard_id: int):
        """
        Load a dashboard from the API.

        Args:
            dashboard_id: ID of the dashboard to load
        """
        print(f"Loading dashboard {dashboard_id}...")
        self.id = dashboard_id
        self.config = self.client.get_dashboard(dashboard_id)
        
        # Fetch raw dashboard data to get plot templates
        try:
            response = self.client.session.requestGet(f'dashboards/dashboard/read/{dashboard_id}')
            raw_data = response.json()
            dashboard_data = raw_data.get('dashboard', raw_data)
            raw_graphs = json.loads(dashboard_data.get('graphs', '[]'))
        except Exception as e:
            print(f"Warning: Could not load plot details: {e}")
            raw_graphs = []

        # Process graphs and create Graph objects
        self.graphs = []
        parse_errors = 0
        
        for idx, (graph_config, raw_graph) in enumerate(zip(self.config.graphs, raw_graphs)):
            # Use the graph config from the API response, but populate it with plot templates from raw data
            
            # Parse plot template and layout
            plot_template_str = raw_graph.get('plot', '[]')
            layout_str = raw_graph.get('layout', '{}')
            html_content = raw_graph.get('html', '')

            # Try to parse plot configs
            plot_configs = self._safe_json_parse(plot_template_str, idx, 'plot')
            layout = self._safe_json_parse(layout_str, idx, 'layout')
            
            # Handle parsing failures
            if plot_configs is None:
                plot_configs = []
                parse_errors += 1
                
            if layout is None:
                layout = {}
                parse_errors += 1
            
            # Skip graphs that have no valid data
            if not plot_configs and not html_content:
                continue
            
            # If we have HTML content but no plot config, that's okay
            if html_content and not plot_configs:
                print(f"Note: Graph {idx} has HTML content but no valid plot config. Loading as HTML-only graph.")
            
            try:
                # Update the graph object with parsed configs
                graph_config.plot_config = plot_configs[0] if plot_configs else {}
                graph_config.layout_config = layout
                graph_config.html = html_content
                
                # Set runtime attributes
                graph_config.id = f"_plot_{idx}"
                graph_config.index = idx
                
                # Create Plot objects
                graph_config.plots = [Plot(cfg, i) for i, cfg in enumerate(plot_configs)]
                
                self.graphs.append(graph_config)
                
            except Exception as e:
                print(f"Warning: Could not create graph object for {idx}: {e}")
                parse_errors += 1

        # Summary
        if parse_errors > 0:
            print(f"⚠ Encountered {parse_errors} parsing error(s)")
        print(f"✓ Loaded {len(self.graphs)} graphs successfully")
        return self

    def get_graph(self, index: int) -> Graph:
        """
        Get a graph by index.

        Args:
            index: Graph index (0-based)

        Returns:
            Graph object

        Raises:
            IndexError: If index is out of range
        """
        return self.graphs[index]

    def list_graphs(self) -> List[str]:
        """
        List all graphs in the dashboard.

        Returns:
            List of graph summaries
        """
        summaries = []
        for i, g in enumerate(self.graphs):
            plot_types = [p.type for p in g.plots]
            summaries.append(
                f"Graph {i}: {g.id} - {len(g.plots)} plot(s) [{', '.join(plot_types)}] in zone '{g.zone}'"
            )
        return summaries

    def print_graphs(self):
        """Print a summary of all graphs."""
        if not self.config:
            print("No dashboard loaded.")
            return
            
        print(f"Dashboard: {self.config.title} (ID: {self.id})")
        print(f"Total graphs: {len(self.graphs)}\n")
        for summary in self.list_graphs():
            print(summary)

    def add_graph(self, graph: Graph):
        """
        Add a new graph to the dashboard.

        Args:
            graph: Graph object to add
        """
        graph.index = -1
        self.graphs.append(graph)
        return self

    def swap_all_bar_scatter(self):
        """Swap all bar plots with scatter and vice versa."""
        for graph in self.graphs:
            for plot in graph.plots:
                if plot.type == 'bar':
                    plot.type = 'scatter'
                elif plot.type == 'scatter':
                    plot.type = 'bar'
        return self

    def visualize(self, output_file: Optional[str] = None, open_browser: bool = True) -> str:
        """
        Visualize the dashboard with current plot modifications.

        Args:
            output_file: Path to save the HTML file (default: dashboard_{id}.html)
            open_browser: Whether to open the HTML file in a browser

        Returns:
            Path to the generated HTML file
        """
        if not self.id:
            raise ValueError("No dashboard loaded. Call load() first.")

        # Sync graphs to config
        if self.config:
            self.config.graphs = self.graphs

        # Visualize using the client
        # The client will use the modified plot configs from graph.plots
        result = self.client.visualize(
            dashboard_id=self.id,
            output_file=output_file or f"dashboard_{self.id}.html",
            open_browser=open_browser,
            dashboard_config=self.config
        )

        return result

    def save(self):
        """
        Save the current dashboard configuration back to the server.
        """
        if not self.id or not self.config:
            raise ValueError("No dashboard loaded.")

        # Update config with current graph states
        # Note: This updates the configuration, but might need more work to fully serialize
        # complex plot changes back to the template format with placeholders.
        # For now, we'll just update the basic graph properties.

        print(f"Updating dashboard {self.id}...")
        self.client.update_dashboard(self.id, self.config)
        print("✓ Dashboard updated")

    def preview(self, output_file: Optional[str] = None, open_browser: bool = False) -> str:
        """
        Preview how the dashboard would be rendered by the server.

        This is useful for testing dashboard configurations before saving them.
        If output_file is not specified and open_browser is True, uses a temporary file.

        Args:
            output_file: Path to save the HTML file (default: None for temp file if open_browser=True,
                        or dashboard_{id}_preview.html if open_browser=False)
            open_browser: Whether to open the HTML file in a browser (default: False)

        Returns:
            Path to the generated HTML file (or temp file path if using temporary file)

        Raises:
            ValueError: If no dashboard is loaded
        """
        if not self.config:
            raise ValueError("No dashboard loaded. Call load() first.")

        # Prepare queries - convert Query objects to dict format
        queries_dict = {}
        for query in self.config.queries:
            if hasattr(query, 'name') and hasattr(query, 'sql'):
                queries_dict[query.name] = query.sql
            elif hasattr(query, 'sql'):
                queries_dict[str(query)] = query.sql
            else:
                queries_dict[str(query)] = str(query)

        # Prepare graphs - convert Graph objects to dict format
        graphs_list = []
        for graph in self.graphs:
            graph_dict = {
                'query': graph.query,
                'zone': graph.zone if hasattr(graph, 'zone') else 'main',
                'priority': graph.priority if hasattr(graph, 'priority') else 0,
                'group': getattr(graph, 'group', ''),
                'group-menu': getattr(graph, 'group_menu', False),
                'plot-hidden': 'on' if getattr(graph, 'hidden', False) else 'off'
            }

            # Add plot configuration
            if hasattr(graph, 'plots') and graph.plots:
                graph_dict['plot'] = json.dumps([p.config for p in graph.plots])
            elif hasattr(graph, 'plot_config') and graph.plot_config:
                graph_dict['plot'] = json.dumps([graph.plot_config])
            else:
                graph_dict['plot'] = '[]'

            # Add layout configuration
            if hasattr(graph, 'layout_config') and graph.layout_config:
                graph_dict['layout'] = json.dumps(graph.layout_config)
            else:
                graph_dict['layout'] = '{}'

            # Add HTML content if present
            if hasattr(graph, 'html') and graph.html:
                graph_dict['html'] = graph.html
            else:
                graph_dict['html'] = ''

            graphs_list.append(graph_dict)

        # Get params from config
        params_dict = {}
        if hasattr(self.config, 'params') and self.config.params:
            params_dict = self.config.params if isinstance(self.config.params, dict) else json.loads(self.config.params)

        # Call the preview endpoint
        html_content = self.client.preview_dashboard(
            datasource_id=self.config.datasource_id,
            template_id=self.config.template_id,
            queries=queries_dict,
            graphs=graphs_list,
            params=params_dict
        )

        # Always save to a regular file (not temporary)
        if not output_file:
            output_file = f"dashboard_{self.id}_preview.html"

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"✓ Preview saved to {output_file}")

        # Open in browser or display in Jupyter if requested
        if open_browser:
            # Try Jupyter HTML display first (for forms with hidden parameters)
            if not _display_html_in_jupyter(output_file):
                # Fallback to regular browser for non-Jupyter environments
                import webbrowser
                import os
                webbrowser.open(f'file://{os.path.abspath(output_file)}')
                print("Opening in browser...")

        return output_file

    def __repr__(self):
        title = self.config.title if self.config else "None"
        return f"Dashboard(id={self.id}, title='{title}', graphs={len(self.graphs)})"
