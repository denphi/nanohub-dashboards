"""
Unit tests for utility functions.
"""
import pytest
import sqlite3
from nanohubdashboard.utils import (
    register_sqlite_functions,
    sqlite_concat,
    sqlite_iif,
    sqlite_avg,
    sqlite_quarter,
    sqlite_log,
    sqlite_color,
    validate_sql_query,
    sanitize_alias,
    PLOTLY_COLORS
)


class TestSQLiteFunctions:
    """Test cases for SQLite custom functions."""
    
    def test_sqlite_concat(self):
        """Test string concatenation."""
        assert sqlite_concat("Hello", " ", "World") == "Hello World"
        assert sqlite_concat("a", "b", "c") == "abc"
        assert sqlite_concat() == ""
    
    def test_sqlite_concat_with_none(self):
        """Test concatenation with None values."""
        assert sqlite_concat("Hello", None, "World") == "HelloWorld"
        assert sqlite_concat(None, None) == ""
    
    def test_sqlite_iif_true(self):
        """Test immediate IF with true condition."""
        assert sqlite_iif(True, "yes", "no") == "yes"
        assert sqlite_iif(1, "yes", "no") == "yes"
        assert sqlite_iif("truthy", "yes", "no") == "yes"
    
    def test_sqlite_iif_false(self):
        """Test immediate IF with false condition."""
        assert sqlite_iif(False, "yes", "no") == "no"
        assert sqlite_iif(0, "yes", "no") == "no"
        assert sqlite_iif(None, "yes", "no") == "no"
    
    def test_sqlite_avg(self):
        """Test average calculation."""
        assert sqlite_avg(1, 2, 3, 4, 5) == 3.0
        assert sqlite_avg(10, 20) == 15.0
        assert sqlite_avg(5) == 5.0
    
    def test_sqlite_avg_empty(self):
        """Test average with no arguments."""
        assert sqlite_avg() == 0.0
    
    def test_sqlite_avg_invalid(self):
        """Test average with invalid values."""
        assert sqlite_avg("invalid", "values") == 0.0
    
    def test_sqlite_quarter(self):
        """Test quarter extraction from date."""
        assert sqlite_quarter("2024-01-15") == "2024-Q1"
        assert sqlite_quarter("2024-04-15") == "2024-Q2"
        assert sqlite_quarter("2024-07-15") == "2024-Q3"
        assert sqlite_quarter("2024-10-15") == "2024-Q4"
    
    def test_sqlite_quarter_invalid(self):
        """Test quarter with invalid date."""
        assert sqlite_quarter("invalid") == ""
        assert sqlite_quarter("") == ""
    
    def test_sqlite_log(self):
        """Test logarithm calculation."""
        assert sqlite_log(100, 10) == 2.0
        assert sqlite_log(8, 2) == 3.0
        assert abs(sqlite_log(2.718281828, 2.718281828) - 1.0) < 0.0001
    
    def test_sqlite_log_invalid(self):
        """Test logarithm with invalid values."""
        assert sqlite_log(0, 10) is None
        assert sqlite_log(-1, 10) is None
    
    def test_sqlite_color(self):
        """Test color palette selection."""
        assert sqlite_color(0) == PLOTLY_COLORS[0]
        assert sqlite_color(1) == PLOTLY_COLORS[1]
        assert sqlite_color(9) == PLOTLY_COLORS[9]
    
    def test_sqlite_color_wrapping(self):
        """Test color index wrapping."""
        # Index 10 should wrap to 0
        assert sqlite_color(10) == PLOTLY_COLORS[0]
        assert sqlite_color(11) == PLOTLY_COLORS[1]
    
    def test_sqlite_color_invalid(self):
        """Test color with invalid index."""
        # Should return first color on error
        assert sqlite_color("invalid") == PLOTLY_COLORS[0]
    
    def test_register_sqlite_functions(self):
        """Test registering all custom functions."""
        conn = sqlite3.connect(":memory:")
        register_sqlite_functions(conn)
        
        cursor = conn.cursor()
        
        # Test concat
        cursor.execute("SELECT concat('Hello', ' ', 'World')")
        assert cursor.fetchone()[0] == "Hello World"
        
        # Test nhiif
        cursor.execute("SELECT nhiif(1, 'yes', 'no')")
        assert cursor.fetchone()[0] == "yes"
        
        # Test nhavg
        cursor.execute("SELECT nhavg(1, 2, 3, 4, 5)")
        assert cursor.fetchone()[0] == 3.0
        
        # Test quarter
        cursor.execute("SELECT quarter('2024-01-15')")
        assert cursor.fetchone()[0] == "2024-Q1"
        
        # Test nhlog
        cursor.execute("SELECT nhlog(100, 10)")
        assert cursor.fetchone()[0] == 2.0
        
        # Test nhcolor
        cursor.execute("SELECT nhcolor(0, 'plotly')")
        assert cursor.fetchone()[0] == PLOTLY_COLORS[0]
        
        conn.close()


class TestValidationFunctions:
    """Test cases for validation functions."""
    
    def test_validate_sql_query_valid(self):
        """Test validation of valid SELECT queries."""
        assert validate_sql_query("SELECT * FROM table") is True
        assert validate_sql_query("select id, name from users") is True
        assert validate_sql_query("  SELECT count(*) FROM data") is True
    
    def test_validate_sql_query_invalid(self):
        """Test validation rejects non-SELECT queries."""
        with pytest.raises(ValueError, match="Only SELECT queries"):
            validate_sql_query("INSERT INTO table VALUES (1)")
        
        with pytest.raises(ValueError):
            validate_sql_query("UPDATE table SET x=1")
        
        with pytest.raises(ValueError):
            validate_sql_query("DELETE FROM table")
        
        with pytest.raises(ValueError):
            validate_sql_query("DROP TABLE table")
    
    def test_sanitize_alias(self):
        """Test alias sanitization."""
        assert sanitize_alias("My Dashboard") == "my-dashboard"
        assert sanitize_alias("Test_123") == "test123"
        assert sanitize_alias("Hello World!") == "hello-world"
    
    def test_sanitize_alias_special_chars(self):
        """Test sanitization removes special characters."""
        assert sanitize_alias("Test@#$%Dashboard") == "testdashboard"
        assert sanitize_alias("a!b@c#d$e") == "abcde"
    
    def test_sanitize_alias_multiple_hyphens(self):
        """Test sanitization removes multiple consecutive hyphens."""
        assert sanitize_alias("test---dashboard") == "test-dashboard"
        assert sanitize_alias("a--b--c") == "a-b-c"
    
    def test_sanitize_alias_leading_trailing_hyphens(self):
        """Test sanitization removes leading/trailing hyphens."""
        assert sanitize_alias("-test-") == "test"
        assert sanitize_alias("---dashboard---") == "dashboard"
    
    def test_sanitize_alias_empty(self):
        """Test sanitization of empty string."""
        assert sanitize_alias("") == ""
        assert sanitize_alias("!!!") == ""


class TestConstants:
    """Test cases for module constants."""
    
    def test_plotly_colors_length(self):
        """Test PLOTLY_COLORS has expected length."""
        assert len(PLOTLY_COLORS) == 10
    
    def test_plotly_colors_format(self):
        """Test PLOTLY_COLORS are valid hex colors."""
        for color in PLOTLY_COLORS:
            assert color.startswith("#")
            assert len(color) == 7
            # Verify hex format
            int(color[1:], 16)  # Should not raise
