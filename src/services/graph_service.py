from fastapi import HTTPException
from src.utils.redis_client import get_redis_connection
import re
from redisgraph import Graph
from redis import Redis

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
    OR toLower(p.maiden_name) CONTAINS toLower('{name}')
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

def build_children_graph(person_id: str):
    parent = get_person(person_id)
    children = get_children(person_id)

    nodes = []
    edges = []

    # Add parent node
    nodes.append({
        "id": parent["person_id"],
        "label": parent["full_name"],
        "gender": parent["gender"]
    })

    # Add child nodes + edges
    for child in children:
        nodes.append({
            "id": child["person_id"],
            "label": child["full_name"],
            "gender": child["gender"]
        })

        edges.append({
            "source": child["person_id"],
            "target": parent["person_id"],
            "type": "CHILD_OF"
        })

    return {
        "nodes": nodes,
        "edges": edges
    }

def get_semantic_subgraph(root_id: str, depth: int = 2):
    nodes = {}
    edges = []
    edge_set = set()
    visited = set()

    queue = [(root_id, 0)]

    while queue:
        person_id, level = queue.pop(0)

        if person_id in visited:
            continue

        visited.add(person_id)

        person = get_person(person_id)
        if not person:
            continue

        if person_id not in nodes:
            nodes[person_id] = {
                "id": person["person_id"],
                "label": person["full_name"],
                "gender": person.get("gender")
            }

        if level < depth:
            # ── Parents ──────────────────────────────────────
            parent_query = f"""
            MATCH (p:Person {{person_id: '{person_id}'}})-[:CHILD_OF]->(parent)
            RETURN parent
            """
            parents = run_query(parent_query)

            for parent in parents:
                parent_id = parent["person_id"]

                if parent_id not in nodes:
                    nodes[parent_id] = {
                        "id": parent["person_id"],
                        "label": parent["full_name"],
                        "gender": parent.get("gender")
                    }

                edge_key = (person_id, parent_id, "CHILD_OF")
                if edge_key not in edge_set:
                    edge_set.add(edge_key)
                    edges.append({
                        "source": person_id,
                        "target": parent_id,
                        "type": "CHILD_OF"
                    })

                if parent_id not in visited:
                    queue.append((parent_id, level + 1))

            # ── Children ─────────────────────────────────────
            child_query = f"""
            MATCH (child:Person)-[:CHILD_OF]->(p:Person {{person_id: '{person_id}'}})
            RETURN child
            """
            children = run_query(child_query)

            for child in children:
                child_id = child["person_id"]

                if child_id not in nodes:
                    nodes[child_id] = {
                        "id": child["person_id"],
                        "label": child["full_name"],
                        "gender": child.get("gender")
                    }

                edge_key = (child_id, person_id, "CHILD_OF")
                if edge_key not in edge_set:
                    edge_set.add(edge_key)
                    edges.append({
                        "source": child_id,
                        "target": person_id,
                        "type": "CHILD_OF"
                    })

                if child_id not in visited:
                    queue.append((child_id, level + 1))

        # ── Spouse (always, at any depth) ────────────────────
        spouse_query = f"""
        MATCH (p:Person {{person_id: '{person_id}'}})-[:SPOUSE]-(s)
        RETURN s
        """
        spouses = run_query(spouse_query)

        for spouse in spouses:
            spouse_id = spouse["person_id"]

            if spouse_id not in nodes:
                nodes[spouse_id] = {
                    "id": spouse["person_id"],
                    "label": spouse["full_name"],
                    "gender": spouse.get("gender")
                }

            source = min(person_id, spouse_id)
            target = max(person_id, spouse_id)
            edge_key = (source, target, "SPOUSE")
            if edge_key not in edge_set:
                edge_set.add(edge_key)
                edges.append({
                    "source": source,
                    "target": target,
                    "type": "SPOUSE"
                })

    return {
        "nodes": list(nodes.values()),
        "edges": edges
    }

def get_relationship_graph(person_a_id: str, person_b_id: str):

    redis_conn = get_redis_connection()
    graph = Graph(GRAPH_NAME, redis_conn)

    query = f"""
    MATCH (a:Person {{person_id: '{person_a_id}'}}),
          (b:Person {{person_id: '{person_b_id}'}})

    CALL algo.SPpaths({{
        sourceNode: a,
        targetNode: b,
        relTypes: ["CHILD_OF", "SPOUSE"],
        relDirection: "both",
        maxLen: 6,
        pathCount: 1
    }})
    YIELD path

    RETURN path
    """

    result = graph.query(query)

    print(f"[DEBUG] result_set: {result.result_set}")

    if not result.result_set or not result.result_set[0]:
        return None

    path = result.result_set[0][0]

    nodes = path.nodes()
    edges = path.edges()

    node_lookup = {node.id: node for node in nodes}

    ordered_nodes = []
    ordered_edges = []

    for node in nodes:
        ordered_nodes.append({
            "id": node.properties["person_id"],
            "label": node.properties.get("full_name"),
            "gender": node.properties.get("gender"),
            "born_year": node.properties.get("born_year")
        })

    for edge in edges:
        src_node = node_lookup.get(edge.src_node)
        dest_node = node_lookup.get(edge.dest_node)

        if not src_node or not dest_node:
            continue

        ordered_edges.append({
            "source": src_node.properties["person_id"],
            "target": dest_node.properties["person_id"],
            "type": edge.relation
        })

    return {
        "nodes": ordered_nodes,
        "edges": ordered_edges,
        "pathPattern": [rel["type"] for rel in ordered_edges]
    }
if __name__ == "__main__":
    # graph = get_relationship_graph("P00001", "P00011")
    print("get person")
    graph = get_person("P00011")
    print(graph)
    print("Semantic Sub graph")
    graph =get_semantic_subgraph("P00011",2)
    print(graph)
    print("children of a person")
    graph =get_children("P00011")
    print(graph)