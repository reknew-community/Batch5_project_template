from fastapi import HTTPException
from src.utils.redis_client import get_redis_connection
import re

GRAPH_NAME = "family_graph"


def run_query(query: str):
    r = get_redis_connection()
    result = r.execute_command("GRAPH.QUERY", GRAPH_NAME, query)

    if not result or len(result) < 2:
        return []

    rows = result[1]
    formatted = []

    for row in rows:
        record = row[0]  # because RETURN child gives single column
        properties = None

        for item in record:
            if item[0] == "properties":
                properties = item[1]
                break

        if properties:
            obj = {}
            for prop in properties:
                obj[prop[0]] = prop[1]
            formatted.append(obj)

    return formatted


def get_person(person_id: str):
    query = f"""
    MATCH (p:Person {{person_id: '{person_id}'}})
    RETURN p
    """
    results = run_query(query)

    if len(results) == 0:
        raise HTTPException(status_code=404, detail="Person not found")

    return results[0]


def get_children(person_id: str):
    query = f"""
    MATCH (p:Person {{person_id: '{person_id}'}})<-[:CHILD_OF]-(child)
    RETURN child
    """
    return run_query(query)


def get_parents(person_id: str):
    query = f"""
    MATCH (c:Person {{person_id: '{person_id}'}})-[:CHILD_OF]->(parent)
    RETURN parent
    """
    return run_query(query)

def search_person_by_name(name: str):
    query = f"""
    MATCH (p:Person)
    WHERE toLower(p.full_name) CONTAINS toLower('{name}')
    RETURN p
    """
    return run_query(query)

def get_siblings(person_id: str):
    query = f"""
    MATCH (p:Person {{person_id: '{person_id}'}})
    -[:CHILD_OF]->(parent)
    <-[:CHILD_OF]-(sibling)
    WHERE sibling.person_id <> '{person_id}'
    RETURN sibling
    """
    return run_query(query)

def get_relationship_path(person_a_id: str, person_b_id: str):
    query = f"""
    MATCH (a:Person {{person_id: '{person_a_id}'}}),
          (b:Person {{person_id: '{person_b_id}'}})
    MATCH path = (a)-[*1..6]-(b)
    RETURN path
    LIMIT 1
    """

    r = get_redis_connection()
    result = r.execute_command("GRAPH.QUERY", GRAPH_NAME, query)

    if not result or len(result) < 2:
        return None

    rows = result[1]
    if not rows:
        return None

    path_string = rows[0][0]

    # Extract IDs
    node_ids = list(map(int, re.findall(r'\((\d+)\)', path_string)))
    rel_ids = list(map(int, re.findall(r'\[(\d+)\]', path_string)))

    nodes = []
    relationships = []

    # Fetch node properties
    for node_id in node_ids:
        node_query = f"""
        MATCH (n)
        WHERE ID(n) = {node_id}
        RETURN n
        """
        node_result = r.execute_command("GRAPH.QUERY", GRAPH_NAME, node_query)

        if node_result and len(node_result) > 1 and node_result[1]:
            record = node_result[1][0][0]
            props = {}
            for item in record:
                if item[0] == "properties":
                    for prop in item[1]:
                        props[prop[0]] = prop[1]
            nodes.append(props)

    # Fetch relationship types
    for rel_id in rel_ids:
        rel_query = f"""
        MATCH ()-[r]->()
        WHERE ID(r) = {rel_id}
        RETURN type(r)
        """
        rel_result = r.execute_command("GRAPH.QUERY", GRAPH_NAME, rel_query)

        if rel_result and len(rel_result) > 1 and rel_result[1]:
            relationships.append(rel_result[1][0][0])

    return {
        "from_person": person_a_id,
        "to_person": person_b_id,
        "nodes": nodes,
        "relationships": relationships
    }
    
def build_descendant_tree(person_id: str,depth: int = 2):
    """
    Recursively builds descendant tree using CHILD_OF relationships.
    """

    # First get current person details
    person = get_person(person_id)

    # Stop recursion if depth is 0
    if depth == 0:
        return {
            "person": person,
            "children": []
        }

    # Now find children
    query = f"""
    MATCH (child:Person)-[:CHILD_OF]->(p:Person {{person_id: '{person_id}'}})
    RETURN child
    """

    children = run_query(query)

    # Recursively build subtree for each child
    child_trees = []
    for child in children:
        child_tree = build_descendant_tree(child["person_id"],depth-1)
        child_trees.append(child_tree)

    return {
        "person": person,
        "children": child_trees
    }

def build_ancestor_tree(person_id: str, depth: int):
    """
    Builds ancestor tree up to specified depth.
    depth = 0 → only person
    """

    # Get current person
    person = get_person(person_id)

    # Stop recursion
    if depth == 0:
        return {
            "person": person,
            "parents": []
        }

    # Find parents
    query = f"""
    MATCH (p:Person {{person_id: '{person_id}'}})-[:CHILD_OF]->(parent)
    RETURN parent
    """

    parents = run_query(query)

    # Recursively build parent trees
    parent_trees = []
    for parent in parents:
        subtree = build_ancestor_tree(parent["person_id"], depth - 1)
        parent_trees.append(subtree)

    return {
        "person": person,
        "parents": parent_trees
    }
def build_full_tree(person_id: str, depth: int, include_spouse=False, visited=None, is_root=True):

    if visited is None:
        visited = set()

    # Prevent cycles
    if person_id in visited:
        return None

    visited.add(person_id)

    person = get_person(person_id)

    if depth == 0:
        return {
            "person": person,
            "parents": [],
            "children": [],
            "spouse": []
        }

    # ---------- Parents ----------
    parent_query = f"""
    MATCH (p:Person {{person_id: '{person_id}'}})-[:CHILD_OF]->(parent)
    RETURN parent
    """
    parents = run_query(parent_query)

    parent_trees = []
    for parent in parents:
        subtree = build_full_tree(
            parent["person_id"],
            depth - 1,
            include_spouse,
            visited,
            is_root=False
        )
        if subtree:
            parent_trees.append(subtree)

    # ---------- Children ----------
    child_query = f"""
    MATCH (child:Person)-[:CHILD_OF]->(p:Person {{person_id: '{person_id}'}})
    RETURN child
    """
    children = run_query(child_query)

    child_trees = []
    for child in children:
        subtree = build_full_tree(
            child["person_id"],
            depth - 1,
            include_spouse,
            visited,
            is_root=False
        )
        if subtree:
            child_trees.append(subtree)

    # ---------- Spouse (Root Only) ----------
    spouse_trees = []
    if include_spouse and is_root:
        spouse_query = f"""
        MATCH (p:Person {{person_id: '{person_id}'}})-[:SPOUSE]-(s)
        RETURN s
        """
        spouses = run_query(spouse_query)

        for spouse in spouses:
            spouse_trees.append({
                "person": spouse,
                "parents": [],
                "children": [],
                "spouse": []
            })

    return {
        "person": person,
        "parents": parent_trees,
        "children": child_trees,
        "spouse": spouse_trees
    }


if __name__ == "__main__":
   print(get_person("P00001"))