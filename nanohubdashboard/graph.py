from typing import List, Dict, Any, Optional
import copy
import json
import os
import webbrowser
from dataclasses import dataclass, field
from .plot import Plot

@dataclass
class Graph:
    """
    Represents a graph in a dashboard.
    
    This class handles both the configuration (data model) and manipulation (logic).
    """
    # Configuration attributes (from models.py)
    query: str = ""
    plot_type: str = "scatter"
    zone: str = "main"
    priority: int = 0
    plot_config: Dict[str, Any] = field(default_factory=dict)
    layout_config: Dict[str, Any] = field(default_factory=dict)
    group: str = ""
    group_menu: bool = False
    html: str = ""
    
    # Runtime attributes (from loader.py)
    id: str = ""
    index: int = 0
    plots: List[Plot] = field(default_factory=list)
    
    def __post_init__(self):
        """Initialize plots from plot_config if available."""
        if self.plot_config and not self.plots:
            # If we have a single plot config, create a Plot object
            self.plots = [Plot(self.plot_config, 0)]
            
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format compatible with PHP component."""
        # Serialize all plots
        plots_data = []
        if self.plots:
            plots_data = [p.config for p in self.plots]
        elif self.plot_config:
            plots_data = [self.plot_config]
        
        return {
            "query": self.query,
            "type": self.plot_type,
            "zone": self.zone,
            "priority": self.priority,
            "plot": json.dumps(plots_data),
            "layout": json.dumps(self.layout_config),
            "html": self.html,
            "group": self.group,
            "group-menu": self.group_menu
        }

    def get_plot(self, index: int) -> Plot:
        """
        Get a specific plot by index.

        Args:
            index: Plot index (0-based)

        Returns:
            Plot object

        Raises:
            IndexError: If index is out of range
        """
        return self.plots[index]

    @property
    def plot(self) -> Optional[Plot]:
        """Get the first plot (convenience property for single-plot graphs)."""
        return self.plots[0] if self.plots else None

    def add_plot(self, plot_config: Dict[str, Any]) -> Plot:
        """
        Add a new plot to this graph.

        Args:
            plot_config: Plot configuration dictionary

        Returns:
            The newly created Plot object
        """
        plot = Plot(plot_config, len(self.plots))
        self.plots.append(plot)
        return plot

    def remove_plot(self, index: int):
        """
        Remove a plot by index.

        Args:
            index: Plot index to remove
        """
        del self.plots[index]
        # Reindex remaining plots
        for i, plot in enumerate(self.plots):
            plot.index = i
            
    def set_layout(self, key: str, value: Any):
        """Set a layout property."""
        self.layout_config[key] = value
        return self
        
    def get_layout(self, key: str, default: Any = None) -> Any:
        """Get a layout property."""
        return self.layout_config.get(key, default)

    def visualize(self, data: Optional[Dict[str, list]] = None,
                  layout: Optional[Dict[str, Any]] = None,
                  output_file: Optional[str] = None,
                  open_browser: bool = True) -> str:
        """
        Render this graph (all its plots) as a standalone HTML file.

        Args:
            data: Optional dictionary containing data to replace placeholders in plot configs.
                  Keys should match placeholder names (case-insensitive, without % prefix).
                  Example: {'x': [1, 2, 3], 'y': [4, 5, 6], 'name': ['Series 1']}
            layout: Optional layout configuration. If not provided, uses graph's layout_config.
            output_file: Path to save HTML file. Defaults to 'graph_{index}.html'
            open_browser: Whether to open the HTML file in a browser

        Returns:
            Path to the generated HTML file
        """
        # Determine output file
        if output_file is None:
            output_file = f'graph_{self.index}.html'

        # Prepare layout
        if layout is None:
            layout = copy.deepcopy(self.layout_config) if self.layout_config else {}
        else:
            layout = copy.deepcopy(layout)

        # Set defaults if not specified
        if 'autosize' not in layout:
            layout['autosize'] = True
        if 'margin' not in layout:
            layout['margin'] = {'l': 50, 'r': 50, 't': 50, 'b': 50}

        # Process all plots
        plots_data = []
        for plot in self.plots:
            plot_config = copy.deepcopy(plot.config)

            # Replace placeholders with data if provided
            if data:
                plot_config = self._replace_placeholders(plot_config, data)

            plots_data.append(plot_config)

        # Generate HTML
        title = f"Graph {self.index}" if not self.id else f"Graph {self.id}"
        html_content = self._generate_html(plots_data, layout, title)

        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        # Display in browser or Jupyter
        abs_path = os.path.abspath(output_file)
        if open_browser:
            # Try Jupyter display first
            if not self._display_in_jupyter(output_file):
                # Fallback to browser
                webbrowser.open(f'file://{abs_path}')

        return abs_path

    def _replace_placeholders(self, config: Any, data: Dict[str, list]) -> Any:
        """
        Recursively replace placeholders in plot config with actual data.

        Args:
            config: Plot configuration (can be dict, list, or primitive)
            data: Dictionary mapping field names to data arrays

        Returns:
            Config with placeholders replaced
        """
        if isinstance(config, dict):
            return {k: self._replace_placeholders(v, data) for k, v in config.items()}
        elif isinstance(config, list):
            return [self._replace_placeholders(item, data) for item in config]
        elif isinstance(config, str) and config.startswith('%'):
            # Extract field name (remove %)
            field_name = config[1:].lower()
            # Create case-insensitive lookup
            data_lower = {k.lower(): v for k, v in data.items()}
            if field_name in data_lower:
                return data_lower[field_name]
            else:
                return config  # Keep placeholder if no data found
        else:
            return config

    def _display_in_jupyter(self, file_path: str) -> bool:
        """Try to display HTML file in Jupyter environment."""
        try:
            from IPython.display import IFrame, display
            import IPython

            # Check if in Jupyter
            ipython = IPython.get_ipython()
            if ipython is None:
                return False

            # Display using IFrame
            display(IFrame(src=file_path, width='100%', height=600))
            return True
        except (ImportError, AttributeError):
            return False

    def _generate_html(self, plots_data: list, layout: Dict[str, Any], title: str) -> str:
        """
        Generate standalone HTML with Plotly visualization.

        Args:
            plots_data: List of plot configurations
            layout: Layout configuration
            title: HTML page title

        Returns:
            Complete HTML string
        """
        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    <script src="https://cdn.plot.ly/plotly-2.26.0.min.js"></script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
        }}
        #plot {{
            width: 100%;
            height: 600px;
        }}
    </style>
</head>
<body>
    <div id="plot"></div>
    <script>
        const data = {json.dumps(plots_data)};
        const layout = {json.dumps(layout)};

        Plotly.newPlot('plot', data, layout, {{responsive: true}});
    </script>
</body>
</html>
"""

    def __repr__(self):
        return f"Graph(id={self.id}, index={self.index}, plots={len(self.plots)}, zone={self.zone})"
