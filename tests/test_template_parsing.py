
import pytest
import json
from unittest.mock import MagicMock
from nanohubdashboard.client import DashboardClient

class TestTemplateParsing:
    """Test cases for JSON template parsing and placeholder fixing."""

    def test_fix_json_placeholders_uppercase(self):
        """Test fixing uppercase placeholders."""
        # Mock session to avoid initialization error
        mock_session = MagicMock()
        client = DashboardClient(session=mock_session)
        
        # Standard case
        input_str = '{"x": %TOOL, "y": %WALLTIME}'
        expected = '{"x": "%TOOL", "y": "%WALLTIME"}'
        assert client._fix_json_placeholders(input_str) == expected
        
        # Verify it parses as JSON
        assert json.loads(expected) == {"x": "%TOOL", "y": "%WALLTIME"}

    def test_fix_json_placeholders_lowercase(self):
        """Test fixing lowercase placeholders."""
        mock_session = MagicMock()
        client = DashboardClient(session=mock_session)
        
        input_str = '{"value": %groupcount}'
        expected = '{"value": "%groupcount"}'
        assert client._fix_json_placeholders(input_str) == expected
        
        assert json.loads(expected) == {"value": "%groupcount"}

    def test_fix_json_placeholders_mixed(self):
        """Test fixing mixed case placeholders."""
        mock_session = MagicMock()
        client = DashboardClient(session=mock_session)
        
        input_str = '{"a": %UPPER, "b": %lower}'
        expected = '{"a": "%UPPER", "b": "%lower"}'
        assert client._fix_json_placeholders(input_str) == expected

    def test_fix_json_placeholders_in_list(self):
        """Test fixing placeholders inside lists."""
        mock_session = MagicMock()
        client = DashboardClient(session=mock_session)
        
        # List with comma
        input_str = '{"list": [%ITEM1, %item2]}'
        expected = '{"list": [ "%ITEM1", "%item2" ]}'
        # Note: whitespace might vary depending on regex replacement, but JSON should be valid
        fixed = client._fix_json_placeholders(input_str)
        assert json.loads(fixed) == {"list": ["%ITEM1", "%item2"]}

    def test_fix_json_placeholders_start_of_list(self):
        """Test fixing placeholder at start of list."""
        mock_session = MagicMock()
        client = DashboardClient(session=mock_session)
        
        input_str = '{"list": [%ITEM1]}'
        expected = '{"list": [ "%ITEM1" ]}'
        fixed = client._fix_json_placeholders(input_str)
        assert json.loads(fixed) == {"list": ["%ITEM1"]}

    def test_fix_json_placeholders_nested_list(self):
        """Test fixing placeholders in nested lists."""
        mock_session = MagicMock()
        client = DashboardClient(session=mock_session)
        
        input_str = '{"colors": [[0, %COLOR1], [1, %COLOR2]]}'
        fixed = client._fix_json_placeholders(input_str)
        assert json.loads(fixed) == {"colors": [[0, "%COLOR1"], [1, "%COLOR2"]]}

    def test_fix_json_placeholders_no_spaces(self):
        """Test fixing placeholders with no spaces around delimiters."""
        mock_session = MagicMock()
        client = DashboardClient(session=mock_session)
        
        input_str = '{"x":%date,"y":%count}'
        fixed = client._fix_json_placeholders(input_str)
        assert json.loads(fixed) == {"x": "%date", "y": "%count"}
