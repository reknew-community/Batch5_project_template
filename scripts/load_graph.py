import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))
import redis
import pandas as pd

from src.config.settings import settings


GRAPH_NAME = settings.GRAPH_NAME

def connect():
    return redis.Redis(host="localhost", port=6379, decode_responses=True)

def run_query(r, query):
    return r.execute_command("GRAPH.QUERY", GRAPH_NAME, query)

def clear_graph(r):
    try:
        r.execute_command("GRAPH.DELETE", GRAPH_NAME)
        print("Existing graph deleted.")
    except:
        print("No existing graph found.")

def load_people(r):
    df = pd.read_csv(settings.PEOPLE_FILE)

    for _, row in df.iterrows():
        query = f"""
        CREATE (:Person {{
            person_id: '{row.person_id}',
            first_name: '{row.first_name}',
            middle_name: '{row.middle_name}',
            last_name: '{row.last_name}',
            full_name:'{row.full_name}',
            maiden_name:'{row.maiden_name}',
            born_year: {row.born_year},
            died:'{row.died}',
            age: {row.age},
            gender: '{row.gender}',
            ethnicity_1:'{row.ethnicity_1}',
            ethnicity_2:'{row.ethnicity_2}',
            ethnicity_3:'{row.ethnicity_3}',
            ethnicity_4:'{row.ethnicity_4}',
            notes:'{row.notes}'
        }})
        """
        run_query(r, query)

    print(f"{len(df)} people loaded.")

def load_relationships(r):
    df = pd.read_csv(settings.RELATIONSHIPS_FILE)

    for _, row in df.iterrows():
        query = f"""
        MATCH (a:Person {{person_id: '{row.from_person_id}'}})
        MATCH (b:Person {{person_id: '{row.to_person_id}'}})
        CREATE (a)-[:{row.relationship}]->(b)
        """
        run_query(r, query)

    print(f"{len(df)} relationships loaded.")

if __name__ == "__main__":
    r = connect()
    clear_graph(r)
    load_people(r)
    load_relationships(r)
    print("Graph loading complete.")
