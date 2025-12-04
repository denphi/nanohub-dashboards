
import pytest
import json
from unittest.mock import MagicMock
from nanohubdashboard.client import DashboardClient
from nanohubdashboard.graph import Graph

class TestGrouping:
    """Test cases for client-side grouping logic."""

    def test_process_graphs_with_grouping(self):
        """Test processing a graph with grouping enabled."""
        mock_session = MagicMock()
        client = DashboardClient(session=mock_session)
        
        # Mock data
        data = {
            "TOOL": ["ToolA", "ToolA", "ToolB", "ToolB"],
            "WALLTIME": [10, 20, 30, 40],
            "GROUP": ["Group1", "Group2", "Group1", "Group2"]
        }
        
        # Mock graph config
        graph = MagicMock(spec=Graph)
        graph.query = "TEST_QUERY"
        graph.group = "GROUP"
        graph.zone = "main"
        graph.html = None # Ensure it's not treated as HTML graph
        graph.plot_config = {
            "type": "bar",
            "x": "%TOOL",
            "y": "%WALLTIME",
            "name": "%TOOL"
        }
        # Ensure plots attribute is empty so it uses plot_config
        graph.plots = []
        
        # Mock query results
        query_results = {"TEST_QUERY": data}
        
        # Mock zones and DOM
        zones = {"main": MagicMock()}
        dom = MagicMock()
        dom.createElement.return_value = MagicMock()
        
        # We need to mock raw_graphs as well
        raw_graphs = [{}]
        graph.index = 0
        
        plots, html = client._process_graphs([graph], raw_graphs, query_results, zones, dom)
        
        # Verify plots
        assert len(plots) == 1
        plot_id = list(plots.keys())[0]
        plot_data = json.loads(plots[plot_id]['plot'])
        
        # Should have 2 traces (one for each group)
        assert len(plot_data) == 2
        
        # Verify trace 1 (Group1)
        # Group1 has ToolA (10) and ToolB (30)
        trace1 = plot_data[0]
        assert trace1['x'] == ["ToolA", "ToolB"]
        assert trace1['y'] == [10, 30]
        
        # Verify trace 2 (Group2)
        # Group2 has ToolA (20) and ToolB (40)
        trace2 = plot_data[1]
        assert trace2['x'] == ["ToolA", "ToolB"]
        assert trace2['y'] == [20, 40]

    def test_process_graphs_without_grouping(self):
        """Test processing a graph without grouping (regression test)."""
        mock_session = MagicMock()
        client = DashboardClient(session=mock_session)
        
        data = {
            "TOOL": ["ToolA", "ToolB"],
            "WALLTIME": [10, 30]
        }
        
        graph = MagicMock(spec=Graph)
        graph.query = "TEST_QUERY"
        graph.group = None # No grouping
        graph.zone = "main"
        graph.html = None # Ensure it's not treated as HTML graph
        graph.plot_config = {
            "type": "bar",
            "x": "%TOOL",
            "y": "%WALLTIME"
        }
        graph.plots = []
        
        query_results = {"TEST_QUERY": data}
        zones = {"main": MagicMock()}
        dom = MagicMock()
        dom.createElement.return_value = MagicMock()
        raw_graphs = [{}]
        graph.index = 0
        
        plots, html = client._process_graphs([graph], raw_graphs, query_results, zones, dom)
        
        assert len(plots) == 1
        plot_data = json.loads(plots[list(plots.keys())[0]]['plot'])
        assert len(plot_data) == 1
        assert plot_data[0]['x'] == ["ToolA", "ToolB"]

    def test_group_menu_generation(self):
        """Test generation of group menu."""
        mock_session = MagicMock()
        client = DashboardClient(session=mock_session)
        
        data = {
            "TOOL": ["ToolA", "ToolA"],
            "VALUE": [10, 20],
            "GROUP": ["G1", "G2"]
        }
        
        graph = MagicMock(spec=Graph)
        graph.query = "TEST_QUERY"
        graph.group = "GROUP"
        graph.zone = "main"
        graph.html = None
        # Enable group menu
        setattr(graph, 'group-menu', True)
        
        graph.plot_config = {
            "type": "bar",
            "x": "%TOOL",
            "y": "%VALUE"
        }
        graph.plots = []
        
        query_results = {"TEST_QUERY": data}
        zones = {"main": MagicMock()}
        dom = MagicMock()
        dom.createElement.return_value = MagicMock()
        raw_graphs = [{}]
        graph.index = 0
        
        plots, html = client._process_graphs([graph], raw_graphs, query_results, zones, dom)
        
        plot_id = list(plots.keys())[0]
        layout = json.loads(plots[plot_id]['layout'])
        plot_data = json.loads(plots[plot_id]['plot'])
        
        # Check updatemenus
        assert 'updatemenus' in layout
        assert len(layout['updatemenus']) == 1
        buttons = layout['updatemenus'][0]['buttons']
        assert len(buttons) == 2
        
        # Check visibility
        # Trace 0 (G1) should be visible
        assert plot_data[0]['visible'] is True
        # Trace 1 (G2) should be hidden
        assert plot_data[1]['visible'] is False
        
        # Check button args
        # Button 0 (G1): [True, False]
        assert buttons[0]['args'][0]['visible'] == [True, False]
        # Button 1 (G2): [False, True]
        assert buttons[1]['args'][0]['visible'] == [False, True]

    def test_grouped_indicators(self):
        """Test grouped indicators."""
        mock_session = MagicMock()
        client = DashboardClient(session=mock_session)
        
        data = {
            "VALUE": [100, 200],
            "GROUP": ["G1", "G2"]
        }
        
        graph = MagicMock(spec=Graph)
        graph.query = "TEST_QUERY"
        graph.group = "GROUP"
        graph.zone = "main"
        graph.html = None
        
        graph.plot_config = {
            "type": "indicator",
            "value": "%value", # Lowercase to test regex fix
            "mode": "number"
        }
        graph.plots = []
        
        query_results = {"TEST_QUERY": data}
        zones = {"main": MagicMock()}
        dom = MagicMock()
        dom.createElement.return_value = MagicMock()
        raw_graphs = [{}]
        graph.index = 0
        
        plots, html = client._process_graphs([graph], raw_graphs, query_results, zones, dom)
        
        plot_data = json.loads(plots[list(plots.keys())[0]]['plot'])
        assert len(plot_data) == 2
        
        # Check values
        # Indicator values should be numbers, not lists
        assert plot_data[0]['value'] == 100
        assert plot_data[1]['value'] == 200
