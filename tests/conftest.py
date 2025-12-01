"""
Pytest configuration and shared fixtures for nanohub-dashboards tests.
"""
import pytest
from unittest.mock import Mock, MagicMock
import json


@pytest.fixture
def mock_session():
    """Create a mock nanohub-remote Session object."""
    session = Mock()
    session.url = "https://nanohub.org/api"
    session.headers = {"Authorization": "Bearer mock_token"}
    return session


@pytest.fixture
def sample_plot_config():
    """Sample plot configuration for testing."""
    return {
        "type": "scatter",
        "mode": "markers",
        "x": "%X_DATA",
        "y": "%Y_DATA",
        "name": "Test Plot",
        "marker": {
            "size": 10,
            "color": "blue"
        }
    }


@pytest.fixture
def sample_bar_plot_config():
    """Sample bar plot configuration for testing."""
    return {
        "type": "bar",
        "x": "%X_DATA",
        "y": "%Y_DATA",
        "name": "Test Bar Plot"
    }


@pytest.fixture
def sample_graph_config():
    """Sample graph configuration for testing."""
    return {
        "query": "test_query",
        "type": "scatter",
        "zone": "main",
        "priority": 1,
        "plot": json.dumps([{
            "type": "scatter",
            "mode": "lines",
            "x": "%X_DATA",
            "y": "%Y_DATA",
            "name": "Sample Graph"
        }]),
        "layout": json.dumps({
            "title": "Test Graph",
            "xaxis": {"title": "X Axis"},
            "yaxis": {"title": "Y Axis"}
        }),
        "html": "",
        "group": "",
        "group-menu": False
    }


@pytest.fixture
def sample_dashboard_config():
    """Sample dashboard configuration for testing."""
    return {
        "id": 1,
        "title": "Test Dashboard",
        "description": "A test dashboard",
        "state": 1,
        "created_by": 1000,
        "group_id": 1,
        "datasource_id": 1,
        "graphs": [
            {
                "id": 1,
                "query": "test_query_1",
                "type": "scatter",
                "zone": "main",
                "priority": 1,
                "plot": json.dumps([{
                    "type": "scatter",
                    "mode": "markers",
                    "x": "%X_DATA",
                    "y": "%Y_DATA",
                    "name": "Plot 1"
                }]),
                "layout": json.dumps({"title": "Graph 1"}),
                "html": "",
                "group": "",
                "group-menu": False
            },
            {
                "id": 2,
                "query": "test_query_2",
                "type": "bar",
                "zone": "sidebar",
                "priority": 2,
                "plot": json.dumps([{
                    "type": "bar",
                    "x": "%X_DATA",
                    "y": "%Y_DATA",
                    "name": "Plot 2"
                }]),
                "layout": json.dumps({"title": "Graph 2"}),
                "html": "",
                "group": "",
                "group-menu": False
            }
        ],
        "queries": [
            {
                "id": 1,
                "name": "test_query_1",
                "query": "SELECT * FROM table1"
            },
            {
                "id": 2,
                "name": "test_query_2",
                "query": "SELECT * FROM table2"
            }
        ]
    }


@pytest.fixture
def mock_api_response():
    """Create a mock API response object."""
    response = Mock()
    response.status_code = 200
    response.json.return_value = {"success": True}
    response.text = '{"success": true}'
    return response


@pytest.fixture
def mock_dashboard_api_response(sample_dashboard_config):
    """Create a mock API response for dashboard GET request."""
    response = Mock()
    response.status_code = 200
    response.json.return_value = sample_dashboard_config
    return response


@pytest.fixture
def mock_requests(monkeypatch, mock_api_response):
    """Mock the requests library."""
    mock_get = Mock(return_value=mock_api_response)
    mock_post = Mock(return_value=mock_api_response)
    mock_put = Mock(return_value=mock_api_response)
    mock_delete = Mock(return_value=mock_api_response)
    
    monkeypatch.setattr("requests.get", mock_get)
    monkeypatch.setattr("requests.post", mock_post)
    monkeypatch.setattr("requests.put", mock_put)
    monkeypatch.setattr("requests.delete", mock_delete)
    
    return {
        "get": mock_get,
        "post": mock_post,
        "put": mock_put,
        "delete": mock_delete
    }


@pytest.fixture
def sample_query_result():
    """Sample query result data."""
    return {
        "columns": ["id", "name", "value"],
        "data": [
            [1, "Item 1", 100],
            [2, "Item 2", 200],
            [3, "Item 3", 300]
        ]
    }
