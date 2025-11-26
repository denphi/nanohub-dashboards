"""
Custom exceptions for the nanohubdashboard library.
"""


class DashboardError(Exception):
    """Base exception for all dashboard-related errors."""
    pass


class AuthenticationError(DashboardError):
    """Raised when authentication fails."""
    pass


class DataSourceError(DashboardError):
    """Raised when data source operations fail."""
    pass


class APIError(DashboardError):
    """Raised when API requests fail."""
    
    def __init__(self, message, status_code=None, response=None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class ValidationError(DashboardError):
    """Raised when data validation fails."""
    pass


class QueryError(DashboardError):
    """Raised when SQL query execution fails."""
    pass
