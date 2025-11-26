from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import json
from .query import Query
from .graph import Graph

@dataclass
class DashboardConfig:
    """
    Complete dashboard configuration.
    
    Attributes:
        title: Dashboard title
        description: Dashboard description
        datasource_id: ID of the data source to use
        template_id: ID of the template to use
        queries: List of Query objects
        graphs: List of Graph objects
        params: Additional parameters (filtering, etc.)
        state: Publication state (0=unpublished, 1=published)
        group_id: Group ID for access control (0=public)
    """
    title: str
    description: str = ""
    datasource_id: Optional[int] = None
    template_id: Optional[int] = None
    queries: List[Query] = field(default_factory=list)
    graphs: List[Graph] = field(default_factory=list)
    params: Dict[str, Any] = field(default_factory=dict)
    state: int = 0
    group_id: int = 0
    id: Optional[int] = None
    alias: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for API."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "datasource_id": self.datasource_id,
            "template_id": self.template_id,
            "queries": json.dumps({q.name: q.sql for q in self.queries}),
            "graphs": json.dumps([g.to_dict() for g in self.graphs]),
            "params": json.dumps(self.params),
            "state": self.state,
            "group_id": self.group_id,
            "alias": self.alias
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DashboardConfig':
        """Create from dictionary (e.g., from API response)."""
        # Handle queries - can be string or dict
        queries_data = data.get('queries', '{}')
        if isinstance(queries_data, str):
            try:
                queries_dict = json.loads(queries_data) if queries_data else {}
            except json.JSONDecodeError as e:
                print(f"Warning: Failed to parse queries JSON: {e}")
                print(f"Queries data: {repr(queries_data[:200])}")
                queries_dict = {}
        else:
            queries_dict = queries_data
        
        queries = [Query(name=k, sql=v) for k, v in queries_dict.items()]
        
        # Handle graphs - can be string or list
        graphs_data = data.get('graphs', '[]')
        if isinstance(graphs_data, str):
            try:
                graphs_list = json.loads(graphs_data) if graphs_data else []
            except json.JSONDecodeError as e:
                print(f"Warning: Failed to parse graphs JSON: {e}")
                print(f"Graphs data: {repr(graphs_data[:200])}")
                graphs_list = []
        else:
            graphs_list = graphs_data
        
        # Convert graph dicts to Graph objects, handling API field names
        graphs = []
        for g in graphs_list:
            try:
                # API uses 'type', 'plot', 'layout' - convert to our field names
                graph_dict = {
                    'query': g.get('query', ''),
                    'plot_type': g.get('type', g.get('plot_type', 'scatter')),
                    'zone': g.get('zone', 'main'),
                    'priority': g.get('priority', 0),
                    'group': g.get('group', ''),
                    'group_menu': g.get('group-menu', g.get('group_menu', False))
                }
                
                # Handle plot config
                plot_data = g.get('plot', g.get('plot_config', '[]'))
                if isinstance(plot_data, str):
                    try:
                        plot_list = json.loads(plot_data) if plot_data else []
                        graph_dict['plot_config'] = plot_list[0] if plot_list else {}
                    except json.JSONDecodeError:
                        graph_dict['plot_config'] = {}
                else:
                    graph_dict['plot_config'] = plot_data
                
                # Handle layout config
                layout_data = g.get('layout', g.get('layout_config', '{}'))
                if isinstance(layout_data, str):
                    try:
                        graph_dict['layout_config'] = json.loads(layout_data) if layout_data else {}
                    except json.JSONDecodeError:
                        graph_dict['layout_config'] = {}
                else:
                    graph_dict['layout_config'] = layout_data
                
                graphs.append(Graph(**graph_dict))
            except Exception as e:
                print(f"Warning: Failed to parse graph: {e}")
                print(f"Graph data: {repr(g)}")
                continue
        
        # Handle params
        params_data = data.get('params', '{}')
        if isinstance(params_data, str):
            try:
                params = json.loads(params_data) if params_data else {}
            except json.JSONDecodeError as e:
                print(f"Warning: Failed to parse params JSON: {e}")
                params = {}
        else:
            params = params_data
        
        return cls(
            id=data.get('id'),
            title=data.get('title', ''),
            description=data.get('description', ''),
            datasource_id=data.get('datasource_id'),
            template_id=data.get('template_id'),
            queries=queries,
            graphs=graphs,
            params=params,
            state=data.get('state', 0),
            group_id=data.get('group_id', 0),
            alias=data.get('alias', '')
        )
