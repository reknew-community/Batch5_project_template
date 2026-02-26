# scripts/check_graph.py
from redis import Redis
from redisgraph import Graph

redis_conn = Redis(host="localhost", port=6379)
graph = Graph("family_graph", redis_conn)

try:
    result = graph.query("MATCH (n) RETURN COUNT(n)")
    print("Graph connected successfully")
    print(result.result_set)
except Exception as e:
    print("Connection failed:", e)