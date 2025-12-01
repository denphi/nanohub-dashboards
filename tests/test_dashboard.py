"""
Unit tests for the Dashboard class.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from nanohubdashboard import Dashboard, Graph, Plot


class TestDashboard:
    """Test cases for the Dashboard class."""
    
    def test_dashboard_initialization(self, mock_session):
        """Test Dashboard initialization."""
        dashboard = Dashboard(mock_session)
        
        assert dashboard.session is mock_session
        assert dashboard.client is not None
        assert dashboard.id is None
        assert dashboard.config is None
        assert dashboard.graphs == []
    
    def test_dashboard_get_graph(self, mock_session, sample_plot_config):
        """Test getting a graph by index."""
        dashboard = Dashboard(mock_session)
        graph = Graph(plot_config=sample_plot_config)
        dashboard.graphs = [graph]
        
        result = dashboard.get_graph(0)
        
        assert result is graph
    
    def test_dashboard_get_graph_invalid_index(self, mock_session):
        """Test getting graph with invalid index raises IndexError."""
        dashboard = Dashboard(mock_session)
        
        with pytest.raises(IndexError):
            dashboard.get_graph(0)
    
    def test_dashboard_list_graphs(self, mock_session, sample_plot_config):
        """Test listing all graphs."""
        dashboard = Dashboard(mock_session)
        
        graph1 = Graph(plot_config=sample_plot_config, zone="main")
        graph1.id = "graph_1"
        graph2 = Graph(plot_config=sample_plot_config, zone="sidebar")
        graph2.id = "graph_2"
        
        dashboard.graphs = [graph1, graph2]
        
        summaries = dashboard.list_graphs()
        
        assert len(summaries) == 2
        assert "graph_1" in summaries[0]
        assert "graph_2" in summaries[1]
        assert "main" in summaries[0]
        assert "sidebar" in summaries[1]
    
    def test_dashboard_print_graphs_no_config(self, mock_session, capsys):
        """Test print_graphs with no dashboard loaded."""
        dashboard = Dashboard(mock_session)
        
        dashboard.print_graphs()
        
        captured = capsys.readouterr()
        assert "No dashboard loaded" in captured.out
    
    def test_dashboard_print_graphs_with_config(self, mock_session, sample_plot_config, capsys):
        """Test print_graphs with loaded dashboard."""
        dashboard = Dashboard(mock_session)
        dashboard.id = 1
        dashboard.config = Mock()
        dashboard.config.title = "Test Dashboard"
        
        graph = Graph(plot_config=sample_plot_config)
        graph.id = "graph_1"
        dashboard.graphs = [graph]
        
        dashboard.print_graphs()
        
        captured = capsys.readouterr()
        assert "Test Dashboard" in captured.out
        assert "graph_1" in captured.out
    
    def test_dashboard_add_graph(self, mock_session, sample_plot_config):
        """Test adding a graph to the dashboard."""
        dashboard = Dashboard(mock_session)
        graph = Graph(plot_config=sample_plot_config)
        
        result = dashboard.add_graph(graph)
        
        assert result is dashboard  # Returns self for chaining
        assert len(dashboard.graphs) == 1
        assert dashboard.graphs[0] is graph
        assert graph.index == -1  # New graphs get index -1
    
    def test_dashboard_swap_all_bar_scatter(self, mock_session, sample_plot_config, sample_bar_plot_config):
        """Test swapping bar and scatter plots."""
        dashboard = Dashboard(mock_session)
        
        graph1 = Graph(plot_config=sample_plot_config)  # scatter
        graph2 = Graph(plot_config=sample_bar_plot_config)  # bar
        dashboard.graphs = [graph1, graph2]
        
        result = dashboard.swap_all_bar_scatter()
        
        assert result is dashboard  # Returns self for chaining
        assert graph1.plots[0].type == "bar"
        assert graph2.plots[0].type == "scatter"
    
    def test_dashboard_swap_all_bar_scatter_multiple_plots(self, mock_session, sample_plot_config, sample_bar_plot_config):
        """Test swapping with multiple plots per graph."""
        dashboard = Dashboard(mock_session)
        
        graph = Graph()
        graph.add_plot(sample_plot_config)  # scatter
        graph.add_plot(sample_bar_plot_config)  # bar
        dashboard.graphs = [graph]
        
        dashboard.swap_all_bar_scatter()
        
        assert graph.plots[0].type == "bar"
        assert graph.plots[1].type == "scatter"
    
    def test_dashboard_visualize_no_dashboard(self, mock_session):
        """Test visualize raises error when no dashboard loaded."""
        dashboard = Dashboard(mock_session)
        
        with pytest.raises(ValueError, match="No dashboard loaded"):
            dashboard.visualize()
    
    @patch('nanohubdashboard.client.DashboardClient.visualize')
    def test_dashboard_visualize_success(self, mock_visualize, mock_session):
        """Test successful visualization."""
        dashboard = Dashboard(mock_session)
        dashboard.id = 1
        dashboard.config = Mock()
        
        mock_visualize.return_value = "dashboard_1.html"
        
        result = dashboard.visualize(output_file="test.html", open_browser=False)
        
        assert result == "dashboard_1.html"
        mock_visualize.assert_called_once()
    
    @patch('nanohubdashboard.client.DashboardClient.visualize')
    def test_dashboard_visualize_default_filename(self, mock_visualize, mock_session):
        """Test visualization with default filename."""
        dashboard = Dashboard(mock_session)
        dashboard.id = 5
        dashboard.config = Mock()
        
        mock_visualize.return_value = "dashboard_5.html"
        
        result = dashboard.visualize(open_browser=False)
        
        # Check that default filename was used
        call_args = mock_visualize.call_args
        assert call_args.kwargs['output_file'] == "dashboard_5.html"
    
    def test_dashboard_save_no_dashboard(self, mock_session):
        """Test save raises error when no dashboard loaded."""
        dashboard = Dashboard(mock_session)
        
        with pytest.raises(ValueError, match="No dashboard loaded"):
            dashboard.save()
    
    @patch('nanohubdashboard.client.DashboardClient.update_dashboard')
    def test_dashboard_save_success(self, mock_update, mock_session, capsys):
        """Test successful save."""
        dashboard = Dashboard(mock_session)
        dashboard.id = 1
        dashboard.config = Mock()
        
        dashboard.save()
        
        mock_update.assert_called_once_with(1, dashboard.config)
        captured = capsys.readouterr()
        assert "Dashboard updated" in captured.out
    
    def test_dashboard_preview_no_config(self, mock_session):
        """Test preview raises error when no dashboard loaded."""
        dashboard = Dashboard(mock_session)
        
        with pytest.raises(ValueError, match="No dashboard loaded"):
            dashboard.preview()
    
    @patch('nanohubdashboard.client.DashboardClient.preview_dashboard')
    @patch('builtins.open', create=True)
    def test_dashboard_preview_success(self, mock_open, mock_preview, mock_session):
        """Test successful preview."""
        dashboard = Dashboard(mock_session)
        dashboard.id = 1
        dashboard.config = Mock()
        dashboard.config.datasource_id = 1
        dashboard.config.template_id = 1
        dashboard.config.queries = []
        dashboard.config.params = {}
        dashboard.graphs = []
        
        mock_preview.return_value = "<html>Preview</html>"
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        
        result = dashboard.preview(output_file="preview.html", open_browser=False)
        
        assert result == "preview.html"
        mock_preview.assert_called_once()
        mock_file.write.assert_called_once_with("<html>Preview</html>")
    
    def test_dashboard_repr_no_config(self, mock_session):
        """Test string representation without config."""
        dashboard = Dashboard(mock_session)
        dashboard.id = 1
        
        repr_str = repr(dashboard)
        
        assert "Dashboard" in repr_str
        assert "id=1" in repr_str
        assert "None" in repr_str
        assert "graphs=0" in repr_str
    
    def test_dashboard_repr_with_config(self, mock_session):
        """Test string representation with config."""
        dashboard = Dashboard(mock_session)
        dashboard.id = 1
        dashboard.config = Mock()
        dashboard.config.title = "Test Dashboard"
        dashboard.graphs = [Mock(), Mock()]
        
        repr_str = repr(dashboard)
        
        assert "Dashboard" in repr_str
        assert "id=1" in repr_str
        assert "Test Dashboard" in repr_str
        assert "graphs=2" in repr_str
    
    def test_dashboard_apply_plot_modifications(self, mock_session, sample_plot_config):
        """Test _apply_plot_modifications method."""
        dashboard = Dashboard(mock_session)
        
        # Create a graph with a modified plot
        graph = Graph(plot_config=sample_plot_config)
        plot = graph.plots[0]
        plot.set("opacity", 0.5)
        
        # Apply modifications
        result = dashboard._apply_plot_modifications(
            sample_plot_config,
            graph=graph,
            plot_index=0
        )
        
        assert result["opacity"] == 0.5
        assert result["type"] == "scatter"
    
    def test_dashboard_apply_plot_modifications_preserves_placeholders(self, mock_session, sample_plot_config):
        """Test that _apply_plot_modifications preserves data placeholders."""
        dashboard = Dashboard(mock_session)
        
        # Create a graph with a modified plot
        graph = Graph(plot_config=sample_plot_config)
        plot = graph.plots[0]
        plot.set("x", "modified_x")  # This should be overridden by placeholder
        
        # Original config with placeholder
        original_config = sample_plot_config.copy()
        original_config["x"] = "%X_DATA"
        
        # Apply modifications
        result = dashboard._apply_plot_modifications(
            original_config,
            graph=graph,
            plot_index=0
        )
        
        # Placeholder should be preserved
        assert result["x"] == "%X_DATA"
