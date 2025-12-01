"""
Unit tests for the DashboardConfig class.
"""
import pytest
import json
from nanohubdashboard import DashboardConfig, Graph, Query


class TestDashboardConfig:
    """Test cases for the DashboardConfig class."""
    
    def test_config_initialization_defaults(self):
        """Test DashboardConfig initialization with defaults."""
        config = DashboardConfig(title="Test Dashboard")
        
        assert config.title == "Test Dashboard"
        assert config.description == ""
        assert config.datasource_id is None
        assert config.template_id is None
        assert config.queries == []
        assert config.graphs == []
        assert config.params == {}
        assert config.state == 0
        assert config.group_id == 0
        assert config.id is None
        assert config.alias == ""
    
    def test_config_initialization_with_params(self):
        """Test DashboardConfig initialization with parameters."""
        queries = [Query(name="q1", sql="SELECT * FROM table1")]
        graphs = [Graph(query="q1", zone="main")]
        params = {"filter": "active"}
        
        config = DashboardConfig(
            title="Test Dashboard",
            description="Test Description",
            datasource_id=1,
            template_id=2,
            queries=queries,
            graphs=graphs,
            params=params,
            state=1,
            group_id=5,
            id=10,
            alias="test-alias"
        )
        
        assert config.title == "Test Dashboard"
        assert config.description == "Test Description"
        assert config.datasource_id == 1
        assert config.template_id == 2
        assert len(config.queries) == 1
        assert len(config.graphs) == 1
        assert config.params == {"filter": "active"}
        assert config.state == 1
        assert config.group_id == 5
        assert config.id == 10
        assert config.alias == "test-alias"
    
    def test_config_to_dict(self):
        """Test converting config to dictionary."""
        queries = [Query(name="q1", sql="SELECT * FROM table1")]
        graphs = [Graph(query="q1", zone="main")]
        
        config = DashboardConfig(
            title="Test Dashboard",
            description="Test Description",
            datasource_id=1,
            template_id=2,
            queries=queries,
            graphs=graphs,
            params={"filter": "active"},
            state=1,
            group_id=5,
            id=10
        )
        
        result = config.to_dict()
        
        assert result["id"] == 10
        assert result["title"] == "Test Dashboard"
        assert result["description"] == "Test Description"
        assert result["datasource_id"] == 1
        assert result["template_id"] == 2
        assert result["state"] == 1
        assert result["group_id"] == 5
        
        # Check JSON serialization
        queries_dict = json.loads(result["queries"])
        assert "q1" in queries_dict
        assert queries_dict["q1"] == "SELECT * FROM table1"
        
        graphs_list = json.loads(result["graphs"])
        assert isinstance(graphs_list, list)
        assert len(graphs_list) == 1
        
        params_dict = json.loads(result["params"])
        assert params_dict["filter"] == "active"
    
    def test_config_from_dict_basic(self):
        """Test creating config from dictionary."""
        data = {
            "id": 10,
            "title": "Test Dashboard",
            "description": "Test Description",
            "datasource_id": 1,
            "template_id": 2,
            "state": 1,
            "group_id": 5,
            "alias": "test-alias"
        }
        
        config = DashboardConfig.from_dict(data)
        
        assert config.id == 10
        assert config.title == "Test Dashboard"
        assert config.description == "Test Description"
        assert config.datasource_id == 1
        assert config.template_id == 2
        assert config.state == 1
        assert config.group_id == 5
        assert config.alias == "test-alias"
    
    def test_config_from_dict_with_queries_string(self):
        """Test creating config from dict with queries as JSON string."""
        data = {
            "title": "Test Dashboard",
            "queries": json.dumps({"q1": "SELECT * FROM table1", "q2": "SELECT * FROM table2"})
        }
        
        config = DashboardConfig.from_dict(data)
        
        assert len(config.queries) == 2
        query_names = [q.name for q in config.queries]
        assert "q1" in query_names
        assert "q2" in query_names
    
    def test_config_from_dict_with_queries_dict(self):
        """Test creating config from dict with queries as dictionary."""
        data = {
            "title": "Test Dashboard",
            "queries": {"q1": "SELECT * FROM table1"}
        }
        
        config = DashboardConfig.from_dict(data)
        
        assert len(config.queries) == 1
        assert config.queries[0].name == "q1"
        assert config.queries[0].sql == "SELECT * FROM table1"
    
    def test_config_from_dict_with_graphs_string(self):
        """Test creating config from dict with graphs as JSON string."""
        graphs_data = [
            {
                "query": "q1",
                "type": "scatter",
                "zone": "main",
                "priority": 1,
                "plot": json.dumps([{"type": "scatter", "x": "%X", "y": "%Y"}]),
                "layout": json.dumps({"title": "Graph 1"})
            }
        ]
        
        data = {
            "title": "Test Dashboard",
            "graphs": json.dumps(graphs_data)
        }
        
        config = DashboardConfig.from_dict(data)
        
        assert len(config.graphs) == 1
        assert config.graphs[0].query == "q1"
        assert config.graphs[0].plot_type == "scatter"
        assert config.graphs[0].zone == "main"
    
    def test_config_from_dict_with_graphs_list(self):
        """Test creating config from dict with graphs as list."""
        graphs_data = [
            {
                "query": "q1",
                "type": "bar",
                "zone": "sidebar",
                "priority": 2
            }
        ]
        
        data = {
            "title": "Test Dashboard",
            "graphs": graphs_data
        }
        
        config = DashboardConfig.from_dict(data)
        
        assert len(config.graphs) == 1
        assert config.graphs[0].query == "q1"
        assert config.graphs[0].plot_type == "bar"
        assert config.graphs[0].zone == "sidebar"
    
    def test_config_from_dict_with_params_string(self):
        """Test creating config from dict with params as JSON string."""
        data = {
            "title": "Test Dashboard",
            "params": json.dumps({"filter": "active", "limit": 100})
        }
        
        config = DashboardConfig.from_dict(data)
        
        assert config.params["filter"] == "active"
        assert config.params["limit"] == 100
    
    def test_config_from_dict_with_params_dict(self):
        """Test creating config from dict with params as dictionary."""
        data = {
            "title": "Test Dashboard",
            "params": {"filter": "active"}
        }
        
        config = DashboardConfig.from_dict(data)
        
        assert config.params["filter"] == "active"
    
    def test_config_from_dict_invalid_json_queries(self, capsys):
        """Test handling invalid JSON in queries."""
        data = {
            "title": "Test Dashboard",
            "queries": "invalid json {"
        }
        
        config = DashboardConfig.from_dict(data)
        
        assert config.queries == []
        captured = capsys.readouterr()
        assert "Warning" in captured.out
    
    def test_config_from_dict_invalid_json_graphs(self, capsys):
        """Test handling invalid JSON in graphs."""
        data = {
            "title": "Test Dashboard",
            "graphs": "invalid json ["
        }
        
        config = DashboardConfig.from_dict(data)
        
        assert config.graphs == []
        captured = capsys.readouterr()
        assert "Warning" in captured.out
    
    def test_config_from_dict_invalid_json_params(self, capsys):
        """Test handling invalid JSON in params."""
        data = {
            "title": "Test Dashboard",
            "params": "invalid json {"
        }
        
        config = DashboardConfig.from_dict(data)
        
        assert config.params == {}
        captured = capsys.readouterr()
        assert "Warning" in captured.out
    
    def test_config_from_dict_graph_with_group_menu(self):
        """Test parsing graph with group-menu field."""
        graphs_data = [
            {
                "query": "q1",
                "type": "scatter",
                "group": "Group 1",
                "group-menu": True
            }
        ]
        
        data = {
            "title": "Test Dashboard",
            "graphs": graphs_data
        }
        
        config = DashboardConfig.from_dict(data)
        
        assert config.graphs[0].group == "Group 1"
        assert config.graphs[0].group_menu is True
    
    def test_config_roundtrip(self):
        """Test converting to dict and back preserves data."""
        queries = [Query(name="q1", sql="SELECT * FROM table1")]
        graphs = [Graph(query="q1", zone="main", plot_type="scatter")]
        
        original = DashboardConfig(
            title="Test Dashboard",
            description="Test Description",
            datasource_id=1,
            template_id=2,
            queries=queries,
            graphs=graphs,
            params={"filter": "active"},
            state=1,
            group_id=5,
            id=10
        )
        
        # Convert to dict and back
        data = original.to_dict()
        restored = DashboardConfig.from_dict(data)
        
        assert restored.id == original.id
        assert restored.title == original.title
        assert restored.description == original.description
        assert restored.datasource_id == original.datasource_id
        assert restored.template_id == original.template_id
        assert len(restored.queries) == len(original.queries)
        assert len(restored.graphs) == len(original.graphs)
        assert restored.params == original.params
        assert restored.state == original.state
        assert restored.group_id == original.group_id
