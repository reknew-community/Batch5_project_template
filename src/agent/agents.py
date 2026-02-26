import json
from google import genai
from google.genai import types
from src.agent.prompts import GENEALOGY_AGENT_PROMPT
from src.agent.tools import TOOLS
from src.config.settings import settings

from src.services.graph_service import (
    get_person,
    get_relationship_graph,
    get_semantic_subgraph,
    search_person_by_name,
    get_children,
    get_parents,
    get_siblings
)

# Configure Gemini
client = genai.Client(api_key=settings.GEMINI_API_KEY)


def execute_tool(tool_name, arguments):
    if tool_name == "get_person_details":
        return get_person(arguments["person_id"])

    if tool_name == "search_person":
        return search_person_by_name(arguments["name"])

    if tool_name == "get_children":
        return get_children(arguments["person_id"])

    if tool_name == "get_parents":
        return get_parents(arguments["person_id"])

    if tool_name == "get_siblings":
        return get_siblings(arguments["person_id"])
    
    if tool_name == "get_semantic_subgraph":
        return get_semantic_subgraph(
            arguments["person_id"],
            arguments["depth"]
        )

    if tool_name == "get_relationship_graph":
        return get_relationship_graph(
            arguments["person_a_id"],
            arguments["person_b_id"]
        )
    return {"error": "Unknown tool"}


# def run_agent(user_query: str):
#     last_graph = None
#     print("USING GEMINI KEY:", settings.GEMINI_API_KEY)
#     # Proper Gemini message format
#     messages = [
#         types.Content(
#             role="user",
#             parts=[types.Part(text=GENEALOGY_AGENT_PROMPT.format(user_query=user_query))]
#         )
#     ]

#     max_iterations = 10
#     iteration = 0
    

#     while iteration < max_iterations:
#         iteration += 1
#         print("Loop iteration", iteration)

#         response = client.models.generate_content(
#             model="gemini-2.5-flash",
#             contents=messages,
#             config=types.GenerateContentConfig(
#                 tools=TOOLS,
#                 tool_config=types.ToolConfig(
#                     function_calling_config=types.FunctionCallingConfig(
#                         mode="AUTO"
#                     )
#                 )
#             )
#         )

#         candidate = response.candidates[0]
#         part = candidate.content.parts[0]

#         # If tool call
#         if part.function_call:
#             tool_name = part.function_call.name
#             arguments = dict(part.function_call.args)
#             tool_result = execute_tool(tool_name, arguments)

#             if tool_name in ["get_semantic_subgraph", "get_relationship_graph"]:
#                 last_graph = tool_result
            
            

#             messages.append(
#                 types.Content(
#                     role="model",
#                     parts=[part]
#                 )
#             )

#             messages.append(
#                 types.Content(
#                     role="tool",
#                     parts=[
#                         types.Part.from_function_response(
#                             name=tool_name,
#                             response={"data": tool_result}
#                         )
#                     ]
#                 )
#             )

#             continue
        
#         people = None
#         if last_graph is None:
#             # Try auto-detect person in question
#             people = search_person_by_name(user_query)
#         if people:
#             person_id = people[0]["person_id"]
#             last_graph = get_semantic_subgraph(person_id, depth=1)
#         # Final answer
#         return {
#             "answer": part.text,
#             "graph": last_graph
#         }

#     # If loop exceeded
#     return {
#         "answer": "Generated partial result due to iteration limit.",
#         "graph": last_graph
#     }

def run_agent(user_query: str):
    last_graph = None

    messages = [
        types.Content(
            role="user",
            parts=[
                types.Part(
                    text=GENEALOGY_AGENT_PROMPT.format(
                        user_query=user_query
                    )
                )
            ],
        )
    ]

    max_iterations = 8
    iteration = 0

    while iteration < max_iterations:
        iteration += 1
        print(f"\n--- Loop iteration {iteration} ---")

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=messages,
            config=types.GenerateContentConfig(
                tools=TOOLS,
                tool_config=types.ToolConfig(
                    function_calling_config=types.FunctionCallingConfig(
                        mode="AUTO"
                    )
                ),
            ),
        )

        candidate = response.candidates[0]
        part = candidate.content.parts[0]

        # -------------------------------------------------
        # 🔹 TOOL CALL CASE
        # -------------------------------------------------
        if part.function_call:
            tool_name = part.function_call.name
            arguments = dict(part.function_call.args)

            print("Tool Called:", tool_name)
            print("Arguments:", arguments)

            tool_result = execute_tool(tool_name, arguments)

            print("Tool Result Type:", type(tool_result))

            # Safely extract data
            if isinstance(tool_result, dict):
                tool_data = tool_result.get("data")
                tool_graph = tool_result.get("graph")
            else:
                tool_data = tool_result
                tool_graph = None

            # Save graph if available
            if tool_graph:
                last_graph = tool_graph

            # Add model tool call message
            messages.append(
                types.Content(
                    role="model",
                    parts=[part],
                )
            )

            # Add tool response
            messages.append(
                types.Content(
                    role="tool",
                    parts=[
                        types.Part.from_function_response(
                            name=tool_name,
                            response=tool_result,
                        )
                    ],
                )
            )

            continue

        # -------------------------------------------------
        # 🔹 FINAL TEXT RESPONSE CASE
        # -------------------------------------------------
        final_answer = part.text if hasattr(part, "text") else ""

        return {
            "answer": final_answer,
            "graph": last_graph,
        }

    # -------------------------------------------------
    # 🔹 FAILSAFE
    # -------------------------------------------------
    return {
        "answer": "Could not complete reasoning within iteration limit.",
        "graph": last_graph,
    }

if __name__ == "__main__":
    test_query = "How Jesee and Pallavi are related"
    result = run_agent(test_query)
    print("\n=== FINAL RESULT ===\n")
    print(result)