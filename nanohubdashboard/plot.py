from typing import Dict, Any, Optional
import copy
import json

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

    def __repr__(self):
        return f"Plot(index={self.index}, type={self.type}, mode={self.mode})"
