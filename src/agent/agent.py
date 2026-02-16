import json
from google import genai
from google.genai import types
from src.agent.tools import TOOLS
from src.config.settings import settings

from src.services.graph_service import (
    get_person,
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

    return {"error": "Unknown tool"}


def run_agent(user_query: str):
    response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=user_query,
    config={
        "tools": TOOLS,
        "tool_config": {
            "function_calling_config": {
                "mode": "ANY"
            }
        }
    }
)


    candidate = response.candidates[0]
    part = candidate.content.parts[0]

    # Check if Gemini wants to call a tool
    if part.function_call:
        tool_name = part.function_call.name
        arguments = dict(part.function_call.args)

        tool_result = execute_tool(tool_name, arguments)

        # 🔥 Correct tool response format
        tool_response_part = types.Part.from_function_response(
            name=tool_name,
            response={"data": tool_result}
        )

        final_response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                {
                    "role": "user",
                    "parts": [
                        {
                            "text": f"""
                    User question:
                    {user_query}

                    Tool result:
                    {json.dumps(tool_result, indent=2)}

                    Based on the tool result above, answer clearly and directly.
                    Do not ask for more information.
                    Do not provide instructions.
                    Just answer.
                    """
                        }
                    ]
                }
            ],
        )



        return final_response.text

    return response.text