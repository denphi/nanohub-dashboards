from dataclasses import dataclass
from typing import Dict

@dataclass
class Query:
    """
    Represents a SQL query for a dashboard.
    
    Attributes:
        name: Unique identifier for the query
        sql: SQL query string (must be a SELECT statement)
        description: Optional description of what the query does
    """
    name: str
    sql: str
    description: str = ""
    
    def validate(self) -> bool:
        """Validate that the query is a SELECT statement."""
        if not self.sql.strip().upper().startswith("SELECT"):
            raise ValueError("Only SELECT queries are allowed")
        return True
    
    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary format."""
        return {
            "name": self.name,
            "sql": self.sql,
            "description": self.description
        }
