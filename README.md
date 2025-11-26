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
- Full support for Plotly-based visualizations

## Quick Start

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

### Plot

Represents a single plot trace within a graph:

- `type`: Plot type (e.g., 'scatter', 'bar', 'pie')
- `mode`: Plot mode for scatter plots (e.g., 'lines', 'markers')
- `config`: Full Plotly configuration dictionary
- Direct property access (e.g., `plot.x`, `plot.y`, `plot.name`)

### DashboardClient

Low-level API client for direct API access:

- `get_dashboard(dashboard_id)`: Get dashboard configuration
- `create_dashboard(dashboard_config)`: Create a new dashboard
- `update_dashboard(dashboard_id, dashboard_config)`: Update dashboard
- `delete_dashboard(dashboard_id)`: Delete a dashboard
- `preview_dashboard(...)`: Preview dashboard rendering
- `visualize(...)`: Generate local visualization

## Authentication

The library uses [nanohub-remote](https://github.com/nanohub/nanohub-remote) for authentication. You need a nanoHUB personal access token:

1. Log in to nanoHUB
2. Go to your account settings
3. Generate a personal access token
4. Use the token in your code:

```python
auth_data = {
    "grant_type": "personal_token",
    "token": "your_token_here"
}
session = nr.Session(auth_data, url="https://nanohub.org/api")
```

## Examples

See the [examples](examples/) directory for complete working examples:

- [demo_simple_api.py](examples/demo_simple_api.py): Basic dashboard manipulation
- [demo_base.py](examples/demo_base.py): Complete workflow including save and preview
- [demo_add_plots.py](examples/demo_add_plots.py): Adding new graphs and plots

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
