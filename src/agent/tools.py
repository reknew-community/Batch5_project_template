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
                name="get_relationship_graph",
                description="Get relathionship path of two person",
                parameters=Schema(
                    type="object",
                    properties={
                        "person_a_id": Schema(type="string"),
                        "person_b_id": Schema(type="string")
                    },
                    required=["person_a_id","person_b_id"]
                )
            )
        ]
    ),
    Tool(
        function_declarations = [
            FunctionDeclaration(
                name="get_semantic_subgraph",
                description="Get semantic sub tree graph for a person given person_id and depth",
                parameters=Schema(
                    type="object",
                    properties={
                        "person_id": Schema(type="string"),
                        "depth": Schema(type="integer")
                    },
                    required=["person_id", "depth"]
                )
            )
        ]
    ),
    
]
