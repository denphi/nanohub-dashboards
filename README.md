# nanohub-dashboards

Python client library for interacting with the nanoHUB Dashboard API. Load, manipulate, visualize, and save dashboards programmatically.

## Installation

Install from PyPI:

```bash
pip install nanohub-dashboards
```

Then import in your code:

```python
import nanohubremote as nr
from nanohubdashboard import Dashboard
```

Note: The package is published as `nanohub-dashboards` on PyPI but imported as `nanohubdashboard` (no hyphen).

## Features

- Load existing dashboards from nanoHUB
- Manipulate plot configurations (types, properties, etc.)
- Add new plots and graphs to dashboards
- Preview dashboards locally before saving
- Save changes back to nanoHUB
- Export dashboards to standalone HTML files
- Render individual plots and graphs locally without API access
- Full support for Plotly-based visualizations
- **NEW (0.2.1):** `connect()` helper — authenticate from `NANOHUB_TOKEN` env var or a `.env` file
- **NEW (0.2.1):** Report generation — standalone HTML or Markdown reports with figures, summary statistics, and data tables
- **NEW (0.2.1):** CSV export of dashboard query results
- **NEW (0.2.1):** Data source catalog — search and describe data sources, with example queries mined from dashboards
- **NEW (0.2.1):** Lossless raw create/update (`create_dashboard_raw` / `update_dashboard_raw`) for partial updates that keep `%PLACEHOLDER` plot templates intact

## Quick Start

### Connecting

The simplest way to get a client is `connect()`, which reads your token from
the `NANOHUB_TOKEN` environment variable or a `.env` file in the working
directory (`NANOHUB_URL` selects the instance, default `https://nanohub.org`):

```python
from nanohubdashboard import connect

client = connect()                                # env / .env
client = connect(token="...", url="https://dev.nanohub.org")

client.list_dashboards({"limit": 10})
client.query_datasource(12, "SELECT * FROM tool_usage LIMIT 5")
client.visualize(19, output_file="dashboard.html", open_browser=False)
```

### Generating Reports

```python
client.generate_report(19, "report.html")                    # interactive HTML
client.generate_report(19, "report.md", format="markdown")   # text summary
client.export_dashboard_data(19, "data/")                    # CSV per query
```

### Basic Usage

```python
import nanohubremote as nr
from nanohubdashboard import Dashboard

# Create authenticated session
auth_data = {
    "grant_type": "personal_token",
    "token": "your_token_here"
}
session = nr.Session(auth_data, url="https://nanohub.org/api")

# Load a dashboard
dashboard = Dashboard(session)
dashboard.load(dashboard_id=8)

# View dashboard information
dashboard.print_graphs()

# Manipulate plots
dashboard.swap_all_bar_scatter()

# Visualize locally
dashboard.visualize(
    output_file="my_dashboard.html",
    open_browser=True
)

# Save changes back to nanoHUB
dashboard.save()
```

### Preview Before Saving

Preview how your dashboard will look on the server without saving changes:

```python
# Preview the dashboard configuration
dashboard.preview(open_browser=True)
```

### Working with Individual Graphs

```python
# Get a specific graph
graph = dashboard.get_graph(0)

# Access plots in the graph
for plot in graph.plots:
    print(f"Plot type: {plot.type}")

    # Modify plot properties
    if plot.type == 'bar':
        plot.type = 'scatter'
        plot.mode = 'markers'
```

### Adding New Plots

```python
from nanohubdashboard import Graph, Plot

# Create a new plot
plot_config = {
    'type': 'scatter',
    'mode': 'lines',
    'x': '%X_DATA',
    'y': '%Y_DATA',
    'name': 'My Plot'
}
plot = Plot(plot_config, index=0)

# Create a graph with the plot
graph = Graph(
    query='MY_QUERY',
    zone='main',
    priority=1
)
graph.plots = [plot]

# Add to dashboard
dashboard.add_graph(graph)
```

### Rendering Single Plots Locally (No API Required)

**NEW!** You can now create and render standalone plots without connecting to the API:

```python
from nanohubdashboard.plot import Plot
from nanohubdashboard.graph import Graph

# Simple plot with direct data
plot = Plot({
    'type': 'scatter',
    'mode': 'markers',
    'x': [1, 2, 3, 4, 5],
    'y': [2, 4, 6, 8, 10],
    'name': 'My Data'
}, index=0)

plot.visualize(output_file='my_plot.html')

# Or use placeholders for dynamic data
plot = Plot({
    'type': 'scatter',
    'x': '%X_DATA',
    'y': '%Y_DATA',
    'name': '%SERIES_NAME'
}, index=0)

data = {
    'x_data': [1, 2, 3],
    'y_data': [4, 5, 6],
    'series_name': 'Temperature'
}

plot.visualize(data=data, output_file='dynamic_plot.html')

# Multiple series in one graph
graph = Graph(index=0)
graph.add_plot({'type': 'scatter', 'x': [1,2,3], 'y': [1,4,9], 'name': 'Series 1'})
graph.add_plot({'type': 'scatter', 'x': [1,2,3], 'y': [1,2,3], 'name': 'Series 2'})
graph.visualize(output_file='multi_series.html')
```

See [SINGLE_PLOT_QUICKSTART.md](SINGLE_PLOT_QUICKSTART.md) for more details.

## Core Components

### Dashboard

The main class for working with dashboards:

- `load(dashboard_id)`: Load a dashboard from the API
- `save()`: Save changes back to the server
- `visualize(output_file, open_browser)`: Generate local HTML visualization
- `preview(output_file, open_browser)`: Preview server-rendered dashboard
- `get_graph(index)`: Get a specific graph by index
- `add_graph(graph)`: Add a new graph to the dashboard
- `list_graphs()`: List all graphs in the dashboard
- `print_graphs()`: Print a summary of all graphs

### Graph

Represents a single graph/visualization in the dashboard:

- `plots`: List of Plot objects in this graph
- `query`: SQL query name that provides the data
- `zone`: Layout zone where the graph appears
- `priority`: Display order priority
- `layout_config`: Plotly layout configuration
- `html`: Custom HTML content (for non-Plotly graphs)
- `visualize(data, layout, output_file, open_browser)`: **NEW** - Render graph as standalone HTML
- `add_plot(plot_config)`: Add a new plot to this graph

### Plot

Represents a single plot trace within a graph:

- `type`: Plot type (e.g., 'scatter', 'bar', 'pie')
- `mode`: Plot mode for scatter plots (e.g., 'lines', 'markers')
- `config`: Full Plotly configuration dictionary
- `visualize(data, layout, output_file, open_browser)`: **NEW** - Render plot as standalone HTML
- Direct property access (e.g., `plot.x`, `plot.y`, `plot.name`)

### DashboardClient

Low-level API client for direct API access:

- `list_dashboards(filters)`: List accessible dashboards
- `get_dashboard(dashboard_id)`: Get dashboard configuration
- `create_dashboard(dashboard_config)`: Create a new dashboard
- `create_dashboard_raw(data)`: Create from a raw dict (placeholders kept verbatim)
- `update_dashboard(dashboard_id, dashboard_config)`: Update dashboard
- `update_dashboard_raw(dashboard_id, data)`: Partial update from a raw dict
- `delete_dashboard(dashboard_id)`: Delete a dashboard
- `list_datasources(search, group_id)`: List readable data sources
- `describe_datasource(id, counts, examples)`: Schema, SQL functions and example queries
- `search_datasources(query)`: Find tables, columns and example queries across data sources
- `list_templates()` / `get_template(id)`: Layout templates
- `query_datasource(id, sql, format)`: Run a SELECT against a datasource
- `upload_datasource(...)` / `download_datasource(...)`: Move SQLite files
- `preview_dashboard(...)`: Server-side preview rendering
- `visualize(...)`: Generate local visualization
- `generate_report(id, output, format)`: HTML/Markdown report
- `export_dashboard_data(id, dir)`: CSV export of query results

## Authentication

The library uses [nanohub-remote](https://github.com/nanohub/nanohub-remote) for authentication. You need a nanoHUB personal access token.

### Getting Your API Token

1. Visit https://nanohub.org/developer/api/docs
2. Navigate to **Settings → Developer → Personal Access Tokens**
3. Generate a new personal access token
4. Copy the token for use in your code

### Using the Token

```python
auth_data = {
    "grant_type": "personal_token",
    "token": "your_token_here"
}

# Production environment
session = nr.Session(auth_data, url="https://nanohub.org/api")

# Development environment (for testing)
# Use this to safely experiment without affecting production data
session = nr.Session(auth_data, url="https://dev.nanohub.org/api")
```

**Note:** When testing or developing features, you can use the development environment (`url="https://dev.nanohub.org/api"`) to safely experiment without affecting production dashboards.

## Examples

See the [examples](examples/) directory for complete working examples:

- [demo_simple_api.py](examples/demo_simple_api.py): Basic dashboard manipulation
- [demo_base.py](examples/demo_base.py): Complete workflow including save and preview
- [demo_add_plots.py](examples/demo_add_plots.py): Adding new graphs and plots
- **[demo_single_plot_rendering.py](examples/demo_single_plot_rendering.py)**: **NEW** - Standalone plot rendering (6 examples)
- **[demo_single_plot_rendering.ipynb](examples/demo_single_plot_rendering.ipynb)**: **NEW** - Jupyter notebook version

## Requirements

- Python >= 3.6
- requests
- plotly
- pandas
- nanohub-remote

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions:
- GitHub Issues: [Report issues](https://github.com/denphi/nanohub-dashboards/issues)
- nanoHUB Support: [Contact support](https://nanohub.org/support)
