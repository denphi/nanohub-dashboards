"""
Unit tests for the Graph class.
"""
import pytest
import json
from nanohubdashboard import Graph, Plot


class TestGraph:
    """Test cases for the Graph class."""
    
    def test_graph_initialization_defaults(self):
        """Test Graph initialization with default values."""
        graph = Graph()
        
        assert graph.query == ""
        assert graph.plot_type == "scatter"
        assert graph.zone == "main"
        assert graph.priority == 0
        assert graph.plots == []
        assert graph.plot_config == {}
        assert graph.layout_config == {}
    
    def test_graph_initialization_with_params(self):
        """Test Graph initialization with parameters."""
        graph = Graph(
            query="test_query",
            plot_type="bar",
            zone="sidebar",
            priority=5
        )
        
        assert graph.query == "test_query"
        assert graph.plot_type == "bar"
        assert graph.zone == "sidebar"
        assert graph.priority == 5
    
    def test_graph_post_init_creates_plot(self, sample_plot_config):
        """Test that __post_init__ creates Plot from plot_config."""
        graph = Graph(plot_config=sample_plot_config)
        
        assert len(graph.plots) == 1
        assert isinstance(graph.plots[0], Plot)
        assert graph.plots[0].type == "scatter"
    
    def test_graph_to_dict(self, sample_plot_config):
        """Test converting graph to dictionary."""
        graph = Graph(
            query="test_query",
            plot_type="scatter",
            zone="main",
            priority=1,
            plot_config=sample_plot_config,
            layout_config={"title": "Test"}
        )
        
        result = graph.to_dict()
        
        assert result["query"] == "test_query"
        assert result["type"] == "scatter"
        assert result["zone"] == "main"
        assert result["priority"] == 1
        
        # Check JSON serialization
        plot_data = json.loads(result["plot"])
        assert isinstance(plot_data, list)
        assert len(plot_data) == 1
        
        layout_data = json.loads(result["layout"])
        assert layout_data["title"] == "Test"
    
    def test_graph_to_dict_multiple_plots(self, sample_plot_config, sample_bar_plot_config):
        """Test to_dict with multiple plots."""
        graph = Graph(query="test_query")
        graph.add_plot(sample_plot_config)
        graph.add_plot(sample_bar_plot_config)
        
        result = graph.to_dict()
        plot_data = json.loads(result["plot"])
        
        assert len(plot_data) == 2
        assert plot_data[0]["type"] == "scatter"
        assert plot_data[1]["type"] == "bar"
    
    def test_graph_get_plot(self, sample_plot_config):
        """Test getting a plot by index."""
        graph = Graph(plot_config=sample_plot_config)
        
        plot = graph.get_plot(0)
        
        assert isinstance(plot, Plot)
        assert plot.type == "scatter"
    
    def test_graph_get_plot_invalid_index(self):
        """Test getting plot with invalid index raises IndexError."""
        graph = Graph()
        
        with pytest.raises(IndexError):
            graph.get_plot(0)
    
    def test_graph_plot_property(self, sample_plot_config):
        """Test the plot property (convenience for first plot)."""
        graph = Graph(plot_config=sample_plot_config)
        
        plot = graph.plot
        
        assert isinstance(plot, Plot)
        assert plot.type == "scatter"
    
    def test_graph_plot_property_empty(self):
        """Test plot property returns None when no plots."""
        graph = Graph()
        
        assert graph.plot is None
    
    def test_graph_add_plot(self, sample_plot_config):
        """Test adding a plot to the graph."""
        graph = Graph()
        
        plot = graph.add_plot(sample_plot_config)
        
        assert isinstance(plot, Plot)
        assert len(graph.plots) == 1
        assert graph.plots[0] is plot
        assert plot.index == 0
    
    def test_graph_add_multiple_plots(self, sample_plot_config, sample_bar_plot_config):
        """Test adding multiple plots."""
        graph = Graph()
        
        plot1 = graph.add_plot(sample_plot_config)
        plot2 = graph.add_plot(sample_bar_plot_config)
        
        assert len(graph.plots) == 2
        assert plot1.index == 0
        assert plot2.index == 1
    
    def test_graph_remove_plot(self, sample_plot_config, sample_bar_plot_config):
        """Test removing a plot by index."""
        graph = Graph()
        graph.add_plot(sample_plot_config)
        graph.add_plot(sample_bar_plot_config)
        
        graph.remove_plot(0)
        
        assert len(graph.plots) == 1
        assert graph.plots[0].type == "bar"
        assert graph.plots[0].index == 0  # Re-indexed
    
    def test_graph_remove_plot_reindexes(self, sample_plot_config):
        """Test that removing a plot re-indexes remaining plots."""
        graph = Graph()
        for i in range(3):
            graph.add_plot(sample_plot_config)
        
        graph.remove_plot(1)  # Remove middle plot
        
        assert len(graph.plots) == 2
        assert graph.plots[0].index == 0
        assert graph.plots[1].index == 1
    
    def test_graph_set_layout(self):
        """Test setting layout properties."""
        graph = Graph()
        
        result = graph.set_layout("title", "Test Title")
        
        assert result is graph  # Returns self for chaining
        assert graph.layout_config["title"] == "Test Title"
    
    def test_graph_set_layout_chaining(self):
        """Test method chaining with set_layout."""
        graph = Graph()
        
        graph.set_layout("title", "Test").set_layout("showlegend", True)
        
        assert graph.layout_config["title"] == "Test"
        assert graph.layout_config["showlegend"] is True
    
    def test_graph_get_layout(self):
        """Test getting layout properties."""
        graph = Graph(layout_config={"title": "Test Title"})
        
        assert graph.get_layout("title") == "Test Title"
    
    def test_graph_get_layout_default(self):
        """Test getting non-existent layout property with default."""
        graph = Graph()
        
        assert graph.get_layout("nonexistent") is None
        assert graph.get_layout("nonexistent", "default") == "default"
    
    def test_graph_repr(self):
        """Test string representation."""
        graph = Graph(query="test_query", zone="main")
        graph.id = "graph_1"
        graph.index = 0
        
        repr_str = repr(graph)
        
        assert "Graph" in repr_str
        assert "graph_1" in repr_str
        assert "index=0" in repr_str
        assert "plots=0" in repr_str
        assert "main" in repr_str
    
    def test_graph_group_properties(self):
        """Test group and group_menu properties."""
        graph = Graph(group="Group 1", group_menu=True)
        
        assert graph.group == "Group 1"
        assert graph.group_menu is True
        
        result = graph.to_dict()
        assert result["group"] == "Group 1"
        assert result["group-menu"] is True
    
    def test_graph_html_property(self):
        """Test HTML property for custom HTML graphs."""
        html_content = "<div>Custom HTML</div>"
        graph = Graph(html=html_content)
        
        assert graph.html == html_content
        
        result = graph.to_dict()
        assert result["html"] == html_content
    
    def test_graph_to_dict_empty_plots(self):
        """Test to_dict with no plots but with plot_config."""
        plot_config = {"type": "scatter", "x": "%X", "y": "%Y"}
        graph = Graph(plot_config=plot_config)
        graph.plots = []  # Clear plots created by __post_init__
        
        result = graph.to_dict()
        plot_data = json.loads(result["plot"])
        
        assert len(plot_data) == 1
        assert plot_data[0]["type"] == "scatter"
