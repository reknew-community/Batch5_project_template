from pydantic import BaseModel
from typing import Optional


class Person(BaseModel):
    person_id: str
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    full_name: str
    maiden_name: Optional[str] = None
    born_year: Optional[int] = None
    died: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    ethnicity_1: Optional[str] = None
    ethnicity_2: Optional[str] = None
    ethnicity_3: Optional[str] = None
    ethnicity_4: Optional[str] = None
    notes: Optional[str] = None
