from google.genai.types import Tool, FunctionDeclaration, Schema

TOOLS = [
    Tool(
        function_declarations=[
            FunctionDeclaration(
                name="get_person_details",
                description="Get full details of a person using their person_id",
                parameters=Schema(
                    type="object",
                    properties={
                        "person_id": Schema(type="string")
                    },
                    required=["person_id"]
                )
            )
        ]
    ),
    Tool(
        function_declarations=[
            FunctionDeclaration(
                name="search_person",
                description="Search a person by name",
                parameters=Schema(
                    type="object",
                    properties={
                        "name": Schema(type="string")
                    },
                    required=["name"]
                )
            )
        ]
    ),
    Tool(
        function_declarations=[
            FunctionDeclaration(
                name="get_children",
                description="Get children of a person",
                parameters=Schema(
                    type="object",
                    properties={
                        "person_id": Schema(type="string")
                    },
                    required=["person_id"]
                )
            )
        ]
    ),
    Tool(
        function_declarations=[
            FunctionDeclaration(
                name="get_parents",
                description="Get parents of a person",
                parameters=Schema(
                    type="object",
                    properties={
                        "person_id": Schema(type="string")
                    },
                    required=["person_id"]
                )
            )
        ]
    ),
    Tool(
        function_declarations=[
            FunctionDeclaration(
                name="get_siblings",
                description="Get siblings of a person",
                parameters=Schema(
                    type="object",
                    properties={
                        "person_id": Schema(type="string")
                    },
                    required=["person_id"]
                )
            )
        ]
    ),
]
