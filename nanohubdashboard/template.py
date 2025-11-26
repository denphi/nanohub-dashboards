from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any

@dataclass
class Template:
    """
    Represents a dashboard template defining layout zones.
    
    Attributes:
        id: Template ID
        title: Template name
        description: XML template definition
        zones: List of zone IDs available in the template
    """
    id: Optional[int] = None
    title: str = ""
    description: str = ""  # XML template
    zones: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description
        }
