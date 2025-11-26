from typing import List, Dict, Any, Optional
import copy
import json
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

    def __repr__(self):
        return f"Graph(id={self.id}, index={self.index}, plots={len(self.plots)}, zone={self.zone})"
