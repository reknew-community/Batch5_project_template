from fastapi import HTTPException
from fastapi import APIRouter
from src.models.person import Person
from typing import List
from src.models.relationship import RelationshipPathResponse
from src.services.graph_service import (
    build_ancestor_tree,
    build_descendant_tree,
    get_person,
    get_children,
    get_parents,
    search_person_by_name,
    get_siblings
)
from src.models.response_models import WrapperResponse

router = APIRouter(prefix="/family", tags=["Family"])


@router.get("/person/{person_id}", response_model=Person)
def person(person_id: str):
    return get_person(person_id.upper())


@router.get("/children/{person_id}", response_model=List[Person])
def children(person_id: str):
    return get_children(person_id)


@router.get("/parents/{person_id}", response_model=List[Person])
def parents(person_id: str):
    return get_parents(person_id)



@router.get("/search", response_model=WrapperResponse)
def search(name: str):
    return search_person_by_name(name)

@router.get("/siblings/{person_id}", response_model=List[Person])
def siblings(person_id: str):
    return get_siblings(person_id)


@router.get("/descendants/{person_id}")
def get_descendants_tree(person_id: str,depth: int = 2):
    if depth < 0 or depth > 5:
        raise HTTPException(status_code=400, detail="Depth must be between 0 and 5")
    
    return build_descendant_tree(person_id)

@router.get("/ancestors/{person_id}")
def get_ancestor_tree(person_id: str, depth: int = 2):
    if depth < 0 or depth > 5:
        raise HTTPException(status_code=400, detail="Depth must be between 0 and 5")
    return build_ancestor_tree(person_id, depth)

@router.get("/tree/{person_id}")
def get_full_tree(
    person_id: str,
    depth: int = 2,
    include_spouse: bool = False
):
    if depth < 0 or depth > 5:
        raise HTTPException(status_code=400, detail="Depth must be between 0 and 5")

    return build_full_tree(person_id, depth, include_spouse)


