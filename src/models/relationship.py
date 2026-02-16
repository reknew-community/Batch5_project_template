from pydantic import BaseModel
from typing import List, Dict


class RelationshipPathResponse(BaseModel):
    from_person: str
    to_person: str
    nodes: List[Dict]
    relationships: List[str]
