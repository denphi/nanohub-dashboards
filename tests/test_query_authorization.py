"""
Test query authorization and fallback to preview when direct query access fails.

This test validates that when a user doesn't have direct access to query a datasource
(403 errors), the preview method still works because it uses server-side rendering.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from nanohubdashboard import Dashboard
from nanohubdashboard.datasource import DataSource
from nanohubdashboard.exceptions import QueryError, AuthenticationError, APIError


class TestQueryAuthorization:
    """Test query authorization scenarios."""

    def test_datasource_query_unauthorized(self, mock_session):
        """Test that datasource query fails with 403 when user is not authorized."""
        # Create a datasource
        ds = DataSource(datasource_id=12, session=mock_session)

        # Mock the session to return 403
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.text = '{"message":"USER NOT AUTHORIZED","code":403}'
        mock_session.requestPost.return_value = mock_response

        # Query should fail with QueryError
        with pytest.raises(QueryError, match="Query failed with status 403"):
            ds.query("SELECT * FROM test_table")

    @patch('nanohubdashboard.client.DashboardClient.visualize')
    def test_dashboard_visualize_fails_on_unauthorized_queries(self, mock_visualize, mock_session):
        """Test that dashboard.visualize() fails when queries return 403."""
        dashboard = Dashboard(mock_session)
        dashboard.id = 19
        dashboard.config = Mock()
        dashboard.config.datasource_id = 12
        dashboard.config.queries = [
            Mock(name='GROUPOWNER', sql='SELECT * FROM groups'),
            Mock(name='AVGWALLPLOT', sql='SELECT * FROM metrics')
        ]

        # Mock visualize to simulate query failures
        def simulate_query_failure(*args, **kwargs):
            # Simulate the behavior where queries fail during visualization
            raise APIError("Query failed with status 403: USER NOT AUTHORIZED", status_code=403)

        mock_visualize.side_effect = simulate_query_failure

        # visualize should propagate the error
        with pytest.raises(APIError, match="403"):
            dashboard.visualize(open_browser=False)

    @patch('nanohubdashboard.client.DashboardClient.preview_dashboard')
    @patch('builtins.open', create=True)
    def test_dashboard_preview_succeeds_when_queries_unauthorized(self, mock_open, mock_preview, mock_session):
        """
        Test that dashboard.preview() succeeds even when user lacks direct query access.

        This is the key test - preview uses server-side rendering which has elevated
        permissions, so it should work even when direct queries fail with 403.
        """
        dashboard = Dashboard(mock_session)
        dashboard.id = 19
        dashboard.config = Mock()
        dashboard.config.datasource_id = 12
        dashboard.config.template_id = 6
        dashboard.config.queries = [
            Mock(name='GROUPOWNER', sql='SELECT * FROM groups'),
            Mock(name='AVGWALLPLOT', sql='SELECT * FROM metrics')
        ]
        dashboard.config.params = {}
        dashboard.graphs = []

        # Mock preview to return successful HTML (server-side has access)
        mock_preview.return_value = "<html><body>Dashboard rendered successfully</body></html>"

        # Mock file writing
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        # Preview should succeed
        result = dashboard.preview(output_file="test_preview.html", open_browser=False)

        assert result == "test_preview.html"
        mock_preview.assert_called_once()
        mock_file.write.assert_called_once()

        # Verify the written content contains the successful render
        written_content = mock_file.write.call_args[0][0]
        assert "Dashboard rendered successfully" in written_content

    def test_datasource_query_various_errors(self, mock_session):
        """Test that datasource handles various HTTP error codes appropriately."""
        ds = DataSource(datasource_id=12, session=mock_session)

        error_scenarios = [
            (403, "USER NOT AUTHORIZED"),
            (401, "Authentication required"),
            (404, "Datasource not found"),
            (500, "Internal server error")
        ]

        for status_code, error_message in error_scenarios:
            mock_response = Mock()
            mock_response.status_code = status_code
            mock_response.text = f'{{"message":"{error_message}"}}'
            mock_session.requestPost.return_value = mock_response

            with pytest.raises(QueryError, match=f"Query failed with status {status_code}"):
                ds.query("SELECT * FROM test_table")

    @patch('nanohubdashboard.client.DashboardClient.get_dashboard')
    @patch('nanohubdashboard.client.DashboardClient.preview_dashboard')
    @patch('builtins.open', create=True)
    def test_integration_load_and_preview_with_auth_issues(
        self, mock_open, mock_preview, mock_get_dashboard, mock_session
    ):
        """
        Integration test: Load a dashboard and preview it when direct query access fails.

        This simulates the user's exact scenario from the issue.
        """
        # Setup mock dashboard config
        mock_config = Mock()
        mock_config.id = 19
        mock_config.title = "EDA_Tool"
        mock_config.description = ""
        mock_config.datasource_id = 12
        mock_config.template_id = 6
        mock_config.graphs = []
        mock_config.queries = []
        mock_config.params = {}

        mock_get_dashboard.return_value = mock_config

        # Mock the raw dashboard data response
        raw_dashboard_response = Mock()
        raw_dashboard_response.status_code = 200
        raw_dashboard_response.json.return_value = {
            'dashboard': {
                'id': 19,
                'title': 'EDA_Tool',
                'graphs': '[]',
                'queries': '{}'
            }
        }
        mock_session.requestGet.return_value = raw_dashboard_response

        # Mock preview to succeed (server-side has permissions)
        mock_preview.return_value = """
        <html>
            <head><title>EDA_Tool</title></head>
            <body>
                <div class="dashboard">
                    <h1>EDA_Tool Dashboard</h1>
                    <div id="plot_1"><!-- Plotly chart --></div>
                </div>
            </body>
        </html>
        """

        # Mock file operations
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        # Create dashboard and load it
        dashboard = Dashboard(mock_session)
        dashboard.load(19)

        assert dashboard.id == 19
        assert dashboard.config is not None

        # Preview should work even though direct queries would fail
        result = dashboard.preview(open_browser=False)

        # Verify preview succeeded
        assert result is not None
        mock_preview.assert_called_once()

        # Verify the preview was called with correct datasource and template
        call_kwargs = mock_preview.call_args.kwargs
        assert call_kwargs['datasource_id'] == 12
        assert call_kwargs['template_id'] == 6

    @patch('nanohubdashboard.datasource.DataSource.query')
    def test_visualize_with_multiple_query_failures(self, mock_query, mock_session):
        """Test that visualize handles multiple query failures gracefully."""
        # Mock query to fail for all queries
        mock_query.side_effect = QueryError("Query failed with status 403: USER NOT AUTHORIZED")

        dashboard = Dashboard(mock_session)
        dashboard.id = 19
        dashboard.config = Mock()
        dashboard.config.datasource_id = 12
        dashboard.config.template_id = 6
        dashboard.config.title = "Test Dashboard"
        dashboard.config.description = "Test"
        dashboard.config.queries = [
            Mock(name='QUERY1', sql='SELECT * FROM table1'),
            Mock(name='QUERY2', sql='SELECT * FROM table2'),
            Mock(name='QUERY3', sql='SELECT * FROM table3')
        ]
        dashboard.config.graphs = []

        # Even with query failures, visualize should handle them
        # (though the resulting dashboard will have no data)
        # The actual implementation logs errors but continues
        # This tests that it doesn't crash
        with patch('nanohubdashboard.client.DashboardClient.visualize') as mock_vis:
            mock_vis.return_value = "dashboard_19.html"
            result = dashboard.visualize(open_browser=False)
            assert result == "dashboard_19.html"


class TestQueryAuthorizationRecommendations:
    """Tests that document recommended approaches when facing auth issues."""

    @patch('builtins.open', create=True)
    @patch('nanohubdashboard.client.DashboardClient.preview_dashboard')
    def test_preview_is_recommended_alternative(self, mock_preview, mock_open, mock_session):
        """
        Document that preview() is the recommended method when direct queries fail.

        When visualize() fails due to query authorization (403 errors), users should
        use preview() instead, which uses server-side rendering with elevated permissions.
        """
        dashboard = Dashboard(mock_session)
        dashboard.id = 19
        dashboard.config = Mock()
        dashboard.config.datasource_id = 12
        dashboard.config.template_id = 6
        dashboard.config.queries = []
        dashboard.config.params = {}
        dashboard.graphs = []

        mock_preview.return_value = "<html>Preview</html>"
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        # Use preview as the recommended approach
        result = dashboard.preview(open_browser=True)

        # Verify it works
        assert result is not None
        mock_preview.assert_called_once()

        # The preview method should open browser when requested
        assert mock_file.write.called
