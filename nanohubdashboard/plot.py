from typing import Dict, Any, Optional
import copy
import json
import os
import webbrowser
from pathlib import Path

class Plot:
    """Represents a single plot/trace in a dashboard."""

    def __init__(self, plot_config: Dict[str, Any], index: int):
        """
        Initialize a Plot object.

        Args:
            plot_config: Dictionary containing plot configuration (Plotly format)
            index: Index of this plot within its graph
        """
        self._config = copy.deepcopy(plot_config)
        self.index = index

    @property
    def type(self) -> str:
        """Get the plot type (bar, scatter, indicator, etc.)."""
        return self._config.get('type', 'scatter')

    @type.setter
    def type(self, value: str):
        """Set the plot type."""
        old_type = self._config.get('type')
        self._config['type'] = value

        # Handle type-specific properties
        if old_type == 'scatter' and value == 'bar':
            # Remove scatter-specific properties
            self._config.pop('mode', None)
        elif old_type == 'bar' and value == 'scatter':
            # Add default mode if not present
            if 'mode' not in self._config:
                self._config['mode'] = 'markers'

    @property
    def mode(self) -> Optional[str]:
        """Get the plot mode (for scatter plots: markers, lines, markers+lines, etc.)."""
        return self._config.get('mode')

    @mode.setter
    def mode(self, value: Optional[str]):
        """Set the plot mode."""
        if value is None:
            self._config.pop('mode', None)
        else:
            self._config['mode'] = value

    @property
    def config(self) -> Dict[str, Any]:
        """Get the full plot configuration dictionary."""
        return self._config

    def set(self, key: str, value: Any):
        """
        Set any property in the plot configuration.

        Args:
            key: Property name
            value: Property value

        Returns:
            Self for method chaining
        """
        self._config[key] = value
        return self

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get any property from the plot configuration.

        Args:
            key: Property name
            default: Default value if property doesn't exist

        Returns:
            Property value or default
        """
        return self._config.get(key, default)

    def visualize(self, data: Optional[Dict[str, list]] = None,
                  layout: Optional[Dict[str, Any]] = None,
                  output_file: Optional[str] = None,
                  open_browser: bool = True) -> str:
        """
        Render this plot as a standalone HTML file.

        Args:
            data: Optional dictionary containing data to replace placeholders in plot config.
                  Keys should match placeholder names (case-insensitive, without % prefix).
                  Example: {'x': [1, 2, 3], 'y': [4, 5, 6]}
            layout: Optional layout configuration to override defaults.
            output_file: Path to save HTML file. Defaults to 'plot_{index}.html'
            open_browser: Whether to open the HTML file in a browser

        Returns:
            Path to the generated HTML file
        """
        # Determine output file
        if output_file is None:
            output_file = f'plot_{self.index}.html'

        # Create a copy of the plot config
        plot_config = copy.deepcopy(self._config)

        # Replace placeholders with data if provided
        if data:
            plot_config = self._replace_placeholders(plot_config, data)

        # Create default layout if not provided
        if layout is None:
            layout = {
                'autosize': True,
                'margin': {'l': 50, 'r': 50, 't': 50, 'b': 50}
            }
        else:
            layout = copy.deepcopy(layout)

        # Generate HTML
        html_content = self._generate_html([plot_config], layout, f"Plot {self.index}")

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
        return f"Plot(index={self.index}, type={self.type}, mode={self.mode})"
