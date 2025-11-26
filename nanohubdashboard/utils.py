"""
Utility functions for the nanohubdashboard library.

Includes SQLite custom functions that match the PHP implementation.
"""

import sqlite3
from datetime import datetime
from typing import Any, Optional
import math


# Plotly color palette (matching PHP implementation)
PLOTLY_COLORS = [
    '#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A',
    '#19D3F3', '#FF6692', '#B6E880', '#FF97FF', '#FECB52'
]


def register_sqlite_functions(conn: sqlite3.Connection) -> None:
    """
    Register custom SQLite functions to match PHP implementation.
    
    Args:
        conn: SQLite database connection
    """
    # String concatenation
    conn.create_function("concat", -1, sqlite_concat)
    
    # Average of multiple values
    conn.create_function("nhavg", -1, sqlite_avg)
    
    # Quarter extraction from date
    conn.create_function("quarter", 1, sqlite_quarter)
    
    # Logarithm with custom base
    conn.create_function("nhlog", 2, sqlite_log)
    
    # Color from palette
    conn.create_function("nhcolor", 2, sqlite_color)
    
    # Immediate IF (ternary)
    conn.create_function("nhiif", 3, sqlite_iif)


def sqlite_concat(*args: str) -> str:
    """
    Concatenate multiple strings.
    
    Args:
        *args: Variable number of strings to concatenate
        
    Returns:
        Concatenated string
    """
    return ''.join(str(arg) if arg is not None else '' for arg in args)


def sqlite_iif(condition: Any, true_value: Any, false_value: Any) -> Any:
    """
    Immediate IF - returns one of two values based on condition.
    
    Args:
        condition: Condition to evaluate
        true_value: Value to return if condition is truthy
        false_value: Value to return if condition is falsy
        
    Returns:
        Selected value based on condition
    """
    return true_value if condition else false_value


def sqlite_avg(*args: float) -> float:
    """
    Calculate average of multiple values.
    
    Args:
        *args: Variable number of numeric values
        
    Returns:
        Average of all values, or 0 if no values provided
    """
    try:
        if len(args) > 0:
            return sum(args) / len(args)
    except (TypeError, ValueError):
        pass
    return 0.0


def sqlite_quarter(time_str: str) -> str:
    """
    Extract quarter from a date string.
    
    Args:
        time_str: Date/time string
        
    Returns:
        Quarter in format "YYYY-QN" or empty string on error
    """
    try:
        dt = datetime.fromisoformat(str(time_str))
        month = dt.month
        year = dt.year
        quarter = (month - 1) // 3 + 1
        return f"{year}-Q{quarter}"
    except (ValueError, AttributeError):
        return ""


def sqlite_log(value: float, base: float = 10) -> Optional[float]:
    """
    Calculate logarithm with custom base.
    
    Args:
        value: Value to calculate log for (must be > 0)
        base: Base for logarithm (default: 10)
        
    Returns:
        Logarithm result, or None if value <= 0 or error
    """
    try:
        if value > 0:
            return math.log(value, base)
    except (TypeError, ValueError):
        pass
    return None


def sqlite_color(value: int = 0, palette: str = "plotly") -> str:
    """
    Get a color from the color palette based on an index.
    
    Args:
        value: Color index (will be wrapped using modulo)
        palette: Color palette name (currently only "plotly" supported)
        
    Returns:
        Hex color code (e.g., "#636EFA")
    """
    try:
        colors = PLOTLY_COLORS
        value = int(value) % len(colors)
        return colors[value]
    except (TypeError, ValueError):
        return PLOTLY_COLORS[0]


def validate_sql_query(query: str) -> bool:
    """
    Validate that a SQL query is a SELECT statement.
    
    Args:
        query: SQL query string
        
    Returns:
        True if valid SELECT query
        
    Raises:
        ValueError: If query is not a SELECT statement
    """
    if not query.strip().upper().startswith("SELECT"):
        raise ValueError("Only SELECT queries are allowed for security reasons")
    return True


def sanitize_alias(alias: str) -> str:
    """
    Sanitize a string to be used as a URL alias.
    
    Args:
        alias: String to sanitize
        
    Returns:
        Sanitized alias (lowercase, alphanumeric and hyphens only)
    """
    import re
    # Convert to lowercase
    alias = alias.lower()
    # Replace spaces with hyphens
    alias = alias.replace(' ', '-')
    # Remove non-alphanumeric characters except hyphens
    alias = re.sub(r'[^a-z0-9-]', '', alias)
    # Remove multiple consecutive hyphens
    alias = re.sub(r'-+', '-', alias)
    # Remove leading/trailing hyphens
    alias = alias.strip('-')
    return alias
