# src/models/response_models.py

from pydantic import BaseModel
from typing import List, Optional, Any


class GraphNode(BaseModel):
    id: str
    label: str
    gender: Optional[str] = None


class GraphEdge(BaseModel):
    source: str
    target: str
    type: str


class GraphResponse(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]


class WrapperResponse(BaseModel):
    data: Optional[Any] = None
    graph: Optional[GraphResponse] = None