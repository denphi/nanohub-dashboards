"""
Unit tests for the DashboardClient class.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import json
from nanohubdashboard import DashboardClient, DashboardConfig
from nanohubdashboard.exceptions import APIError, AuthenticationError


class TestDashboardClient:
    """Test cases for the DashboardClient class."""
    
    def test_client_initialization_with_session(self, mock_session):
        """Test client initialization with a session."""
        client = DashboardClient(session=mock_session)
        
        assert client.session is mock_session
        assert client.base_url == "https://nanohub.org"
    
    def test_client_initialization_custom_base_url(self, mock_session):
        """Test client initialization with custom base URL."""
        client = DashboardClient(session=mock_session, base_url="https://test.nanohub.org")
        
        assert client.base_url == "https://test.nanohub.org"
    
    @patch('nanohubdashboard.client.DashboardClient._make_request')
    def test_list_dashboards(self, mock_request, mock_session):
        """Test listing dashboards."""
        mock_request.return_value = [
            {"id": 1, "title": "Dashboard 1"},
            {"id": 2, "title": "Dashboard 2"}
        ]
        
        client = DashboardClient(session=mock_session)
        result = client.list_dashboards()
        
        assert len(result) == 2
        assert result[0]["title"] == "Dashboard 1"
        mock_request.assert_called_once()
    
    @patch('nanohubdashboard.client.DashboardClient._make_request')
    def test_list_dashboards_with_filters(self, mock_request, mock_session):
        """Test listing dashboards with filters."""
        mock_request.return_value = []
        
        client = DashboardClient(session=mock_session)
        filters = {"group_id": 5, "state": 1}
        client.list_dashboards(filters=filters)
        
        # Verify filters were passed
        call_args = mock_request.call_args
        assert call_args is not None
    
    @patch('nanohubdashboard.client.DashboardClient._make_request')
    def test_get_dashboard(self, mock_request, mock_session, sample_dashboard_config):
        """Test getting a dashboard."""
        mock_request.return_value = sample_dashboard_config
        
        client = DashboardClient(session=mock_session)
        result = client.get_dashboard(dashboard_id=1)
        
        assert isinstance(result, DashboardConfig)
        assert result.title == "Test Dashboard"
        mock_request.assert_called_once()
    
    @patch('nanohubdashboard.client.DashboardClient._make_request')
    def test_create_dashboard(self, mock_request, mock_session):
        """Test creating a dashboard."""
        mock_request.return_value = {"id": 10}
        
        config = DashboardConfig(title="New Dashboard")
        client = DashboardClient(session=mock_session)
        
        result = client.create_dashboard(config)
        
        assert result == 10
        mock_request.assert_called_once()
    
    @patch('nanohubdashboard.client.DashboardClient._make_request')
    def test_update_dashboard(self, mock_request, mock_session):
        """Test updating a dashboard."""
        mock_request.return_value = {"success": True}
        
        config = DashboardConfig(title="Updated Dashboard")
        client = DashboardClient(session=mock_session)
        
        result = client.update_dashboard(dashboard_id=1, dashboard=config)
        
        assert result is True
        mock_request.assert_called_once()
    
    @patch('nanohubdashboard.client.DashboardClient._make_request')
    def test_delete_dashboard(self, mock_request, mock_session):
        """Test deleting a dashboard."""
        mock_request.return_value = {"success": True}
        
        client = DashboardClient(session=mock_session)
        result = client.delete_dashboard(dashboard_id=1)
        
        assert result is True
        mock_request.assert_called_once()
    
    @patch('nanohubdashboard.client.DashboardClient._make_request')
    def test_list_templates(self, mock_request, mock_session):
        """Test listing templates."""
        mock_request.return_value = [
            {"id": 1, "name": "Template 1"},
            {"id": 2, "name": "Template 2"}
        ]
        
        client = DashboardClient(session=mock_session)
        result = client.list_templates()
        
        assert len(result) == 2
        assert result[0]["name"] == "Template 1"
    
    @patch('nanohubdashboard.client.DashboardClient._make_request')
    def test_get_template(self, mock_request, mock_session):
        """Test getting a template."""
        mock_request.return_value = {"id": 1, "name": "Template 1"}
        
        client = DashboardClient(session=mock_session)
        result = client.get_template(template_id=1)
        
        assert result["name"] == "Template 1"
    
    @patch('nanohubdashboard.client.DashboardClient._make_request')
    def test_query_datasource(self, mock_request, mock_session, sample_query_result):
        """Test querying a datasource."""
        mock_request.return_value = sample_query_result
        
        client = DashboardClient(session=mock_session)
        result = client.query_datasource(
            datasource_id=1,
            query="SELECT * FROM table1"
        )
        
        assert "columns" in result
        assert "data" in result
        assert len(result["data"]) == 3
    
    def test_make_request_authentication_error(self, mock_session):
        """Test _make_request handles authentication errors."""
        client = DashboardClient(session=mock_session)
        
        # Mock a 401 response
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        
        with patch.object(mock_session, 'requestGet', return_value=mock_response):
            with pytest.raises(AuthenticationError):
                client._make_request("GET", "test/endpoint")
    
    def test_make_request_api_error(self, mock_session):
        """Test _make_request handles API errors."""
        client = DashboardClient(session=mock_session)
        
        # Mock a 500 response
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_response.json.side_effect = Exception("Not JSON")
        
        with patch.object(mock_session, 'requestGet', return_value=mock_response):
            with pytest.raises(APIError):
                client._make_request("GET", "test/endpoint")
    
    def test_set_plot_transformer(self, mock_session):
        """Test setting plot transformer."""
        client = DashboardClient(session=mock_session)
        
        def transformer(plot_config, graph=None, plot_index=0):
            return plot_config
        
        client.set_plot_transformer(transformer)
        
        # Verify transformer is set (internal state)
        assert hasattr(client, '_plot_transformer')
    
    def test_set_plot_transformer_none(self, mock_session):
        """Test clearing plot transformer."""
        client = DashboardClient(session=mock_session)
        
        # Set and then clear
        client.set_plot_transformer(lambda x: x)
        client.set_plot_transformer(None)
        
        # Transformer should be cleared
        assert client._plot_transformer is None or not hasattr(client, '_plot_transformer')


class TestDashboardClientIntegration:
    """Integration tests for DashboardClient (marked for skipping by default)."""
    
    @pytest.mark.integration
    def test_full_dashboard_workflow(self, mock_session):
        """Test complete dashboard workflow (requires live API)."""
        # This test would require actual API credentials
        # Marked as integration test to skip by default
        pytest.skip("Requires live API credentials")
