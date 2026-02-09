
from typing import Optional,List
from pydantic import BaseModel,Field
from datetime import datetime

class Person(BaseModel):
    person_id: str = Field(..., description="Unique identifier (e.g., P00001)")
    first_name: str
    middle_name: Optional[str] = ""
    last_name: str
    full_name: str
    maiden_name: Optional[str] = ""
    birth_year: Optional[int] = None
    died: Optional[int] = None
    is_alive: bool = True
    gender: str
    ethnicity_1: Optional[str] = ""
    ethnicity_2: Optional[str] = ""
    ethnicity_3: Optional[str] = ""
    ethnicity_4: Optional[str] = ""
    notes: Optional[str] = ""

    @property
    def age(self) -> Optional[int]:
        """Calculate current age or age at death."""
        if self.birth_year:
            if self.died:
                return self.died - self.birth_year
            else:
                return datetime.now().year - self.birth_year
        return None
    
    @property
    def ethnicities(self) -> List[str]:
        """Get list of all non-empty ethnicities."""
        return [
            eth for eth in [
                self.ethnicity_1,
                self.ethnicity_2,
                self.ethnicity_3,
                self.ethnicity_4
            ] if eth
        ]

class Relationship(BaseModel):
    """Model representing a relationship between two people."""
    
    from_person_id: str = Field(..., description="Person ID of the source")
    relationship: str = Field(..., description="Type: SPOUSE, CHILD_OF")
    to_person_id: str = Field(..., description="Person ID of the target")
