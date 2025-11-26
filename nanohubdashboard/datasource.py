"""
DataSource for querying remote data sources via nanoHUB API.

Uses nanohub-remote for authentication and API access.
"""

import json
from typing import Dict, List, Optional, Any, Union

try:
    from nanohubremote import Session
    NANOHUB_REMOTE_AVAILABLE = True
except ImportError:
    NANOHUB_REMOTE_AVAILABLE = False
    Session = None

from .utils import validate_sql_query
from .exceptions import QueryError


class DataSource:
    """
    Remote data source that queries via nanoHUB API.
    
    Uses nanohub-remote for authentication and API access.
    Does not download or manage local database files, only executes queries remotely.
    
    Example:
        import nanohubremote as nr
        
        # Create session with credentials
        auth_data = {"username": "user", "password": "pass"}
        session = nr.Session(auth_data)
        
        # Create data source
        ds = DataSource(datasource_id=2, session=session)
        
        # Query the data source
        query = "SELECT * FROM course"
        results = ds.query(query, format="columns")
        
        # Convert to pandas DataFrame
        import pandas as pd
        df = pd.DataFrame.from_dict(results)
    
    Attributes:
        datasource_id: ID of the data source on nanoHUB
        session: nanohub-remote Session object
        base_url: Base URL for the nanoHUB instance
    """
    
    def __init__(self, datasource_id: int, session: Optional[Any] = None,
                 base_url: str = "https://nanohub.org"):
        """
        Initialize a remote data source.
        
        Args:
            datasource_id: ID of the data source on nanoHUB
            session: nanohub-remote Session object. If None, creates a new session.
            base_url: Base URL for the nanoHUB instance
            
        Raises:
            ImportError: If nanohub-remote is not installed
        """
        if not NANOHUB_REMOTE_AVAILABLE:
            raise ImportError(
                "nanohub-remote is required. "
                "Install it with: pip install nanohub-remote"
            )
        
        self.datasource_id = datasource_id
        self.session = session or Session()
        self.base_url = base_url.rstrip('/')
        self._metadata: Optional[Dict[str, Any]] = None
    
    def query(self, sql: str, format: str = "columns") -> Union[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Execute a SELECT query against the remote data source.
        
        Args:
            sql: SQL query string (must be SELECT)
            format: Result format:
                - 'columns': {"col1": [val1, val2, ...], "col2": [...]} (default)
                - 'records': [{"col1": val1, "col2": val2}, ...]
                - 'split': {"columns": [...], "index": [...], "data": [[...]]}
                - 'tight': {"columns": [...], "index": [...], "data": [[...]], ...}
            
        Returns:
            Query results in the specified format
            
        Raises:
            QueryError: If query execution fails
            ValueError: If query is not a SELECT statement
            
        Example:
            # Query with columns format (default)
            results = ds.query("SELECT * FROM course", format="columns")
            # Returns: {"col1": [1, 2, 3], "col2": ["a", "b", "c"]}
            
            # Query with records format
            results = ds.query("SELECT * FROM course", format="records")
            # Returns: [{"col1": 1, "col2": "a"}, {"col1": 2, "col2": "b"}]
        """
        validate_sql_query(sql)
        
        endpoint = f'dashboards/datasource/query/{self.datasource_id}'
        
        try:
            response = self.session.requestPost(
                endpoint,
                data=json.dumps({
                    "query": sql,
                    "format": format
                })
            )
            
            if response.status_code != 200:
                raise QueryError(
                    f"Query failed with status {response.status_code}: {response.text}"
                )
            
            result = response.json()
            
            # Return just the results for easier use
            return result.get("results", {} if format != "records" else [])
            
        except Exception as e:
            if isinstance(e, QueryError):
                raise
            raise QueryError(f"Query execution failed: {e}")
    
    def to_dataframe(self, sql: str):
        """
        Execute a query and return results as a pandas DataFrame.
        
        Args:
            sql: SQL query string
            
        Returns:
            pandas DataFrame with query results
            
        Raises:
            ImportError: If pandas is not installed
            
        Example:
            import pandas as pd
            df = ds.to_dataframe("SELECT * FROM course")
            print(df.head())
        """
        try:
            import pandas as pd
        except ImportError:
            raise ImportError(
                "pandas is required for to_dataframe(). "
                "Install it with: pip install pandas"
            )
        
        results = self.query(sql, format="columns")
        return pd.DataFrame.from_dict(results)
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get metadata about the remote data source.
        
        Note: This is a placeholder. A full implementation would require
        a metadata endpoint in the API.
        
        Returns:
            Dictionary with data source metadata
        """
        if self._metadata is None:
            self._metadata = {
                "id": self.datasource_id,
                "type": "remote",
                "base_url": self.base_url
            }
        return self._metadata
    
    def __repr__(self) -> str:
        return f"DataSource(id={self.datasource_id}, url={self.base_url})"
