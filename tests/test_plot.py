"""
Unit tests for the Plot class.
"""
import pytest
from nanohubdashboard import Plot


class TestPlot:
    """Test cases for the Plot class."""
    
    def test_plot_initialization(self, sample_plot_config):
        """Test Plot initialization with configuration."""
        plot = Plot(sample_plot_config, index=0)
        
        assert plot.index == 0
        assert plot.type == "scatter"
        assert plot.mode == "markers"
        assert plot.get("name") == "Test Plot"
    
    def test_plot_type_getter(self, sample_plot_config):
        """Test getting plot type."""
        plot = Plot(sample_plot_config, index=0)
        assert plot.type == "scatter"
    
    def test_plot_type_setter(self, sample_plot_config):
        """Test setting plot type."""
        plot = Plot(sample_plot_config, index=0)
        plot.type = "bar"
        
        assert plot.type == "bar"
        # Mode should be removed when changing to bar
        assert "mode" not in plot.config
    
    def test_plot_type_scatter_to_bar(self, sample_plot_config):
        """Test changing plot type from scatter to bar."""
        plot = Plot(sample_plot_config, index=0)
        assert plot.mode == "markers"
        
        plot.type = "bar"
        
        assert plot.type == "bar"
        assert plot.mode is None
    
    def test_plot_type_bar_to_scatter(self, sample_bar_plot_config):
        """Test changing plot type from bar to scatter."""
        plot = Plot(sample_bar_plot_config, index=0)
        assert plot.type == "bar"
        
        plot.type = "scatter"
        
        assert plot.type == "scatter"
        assert plot.mode == "markers"  # Default mode added
    
    def test_plot_mode_getter(self, sample_plot_config):
        """Test getting plot mode."""
        plot = Plot(sample_plot_config, index=0)
        assert plot.mode == "markers"
    
    def test_plot_mode_setter(self, sample_plot_config):
        """Test setting plot mode."""
        plot = Plot(sample_plot_config, index=0)
        plot.mode = "lines"
        
        assert plot.mode == "lines"
    
    def test_plot_mode_setter_none(self, sample_plot_config):
        """Test setting plot mode to None."""
        plot = Plot(sample_plot_config, index=0)
        plot.mode = None
        
        assert plot.mode is None
        assert "mode" not in plot.config
    
    def test_plot_config_property(self, sample_plot_config):
        """Test getting full plot configuration."""
        plot = Plot(sample_plot_config, index=0)
        config = plot.config
        
        assert isinstance(config, dict)
        assert config["type"] == "scatter"
        assert config["mode"] == "markers"
    
    def test_plot_set_method(self, sample_plot_config):
        """Test setting arbitrary properties."""
        plot = Plot(sample_plot_config, index=0)
        plot.set("opacity", 0.5)
        
        assert plot.get("opacity") == 0.5
        assert plot.config["opacity"] == 0.5
    
    def test_plot_set_method_chaining(self, sample_plot_config):
        """Test method chaining with set."""
        plot = Plot(sample_plot_config, index=0)
        result = plot.set("opacity", 0.5).set("line", {"width": 2})
        
        assert result is plot  # Returns self
        assert plot.get("opacity") == 0.5
        assert plot.get("line") == {"width": 2}
    
    def test_plot_get_method(self, sample_plot_config):
        """Test getting properties."""
        plot = Plot(sample_plot_config, index=0)
        
        assert plot.get("name") == "Test Plot"
        assert plot.get("type") == "scatter"
    
    def test_plot_get_method_default(self, sample_plot_config):
        """Test getting non-existent property with default."""
        plot = Plot(sample_plot_config, index=0)
        
        assert plot.get("nonexistent") is None
        assert plot.get("nonexistent", "default") == "default"
    
    def test_plot_config_deep_copy(self, sample_plot_config):
        """Test that plot config is deep copied."""
        plot = Plot(sample_plot_config, index=0)
        
        # Modify original config
        sample_plot_config["type"] = "bar"
        
        # Plot config should be unchanged
        assert plot.type == "scatter"
    
    def test_plot_repr(self, sample_plot_config):
        """Test string representation."""
        plot = Plot(sample_plot_config, index=0)
        repr_str = repr(plot)
        
        assert "Plot" in repr_str
        assert "index=0" in repr_str
        assert "scatter" in repr_str
        assert "markers" in repr_str
    
    def test_plot_marker_config(self, sample_plot_config):
        """Test accessing nested marker configuration."""
        plot = Plot(sample_plot_config, index=0)
        
        marker = plot.get("marker")
        assert marker is not None
        assert marker["size"] == 10
        assert marker["color"] == "blue"
    
    def test_plot_update_nested_config(self, sample_plot_config):
        """Test updating nested configuration."""
        plot = Plot(sample_plot_config, index=0)
        
        plot.set("marker", {"size": 15, "color": "red"})
        
        marker = plot.get("marker")
        assert marker["size"] == 15
        assert marker["color"] == "red"
