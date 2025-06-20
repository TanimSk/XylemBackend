from openai import OpenAI
import json
from django.conf import settings
import requests as req

OPENAI_API_KEY = settings.OPENAI_API_KEY
openai = OpenAI(api_key=OPENAI_API_KEY)


class ChatBot:
    def __init__(self):
        self.model = "gpt-4o-mini"

    TOOL_DEFINITION = [
        {
            "type": "function",
            "function": {
                "name": "search_person",
                "description": """Search for one or more persons by the following criteria: name, age, and gender (male or female). Return a report for each person found, indicating whether they are missing or not.
The output must be in valid HTML, not plain text or markdown. Use appropriate HTML tags (e.g., <div>, <h2>, <p>, etc.) to display the data clearly in natural language and accessibly.""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "age": {"type": "integer"},
                        "gender": {"type": "string"},
                    },
                    "additionalProperties": False,
                },
            },
        },
    ]

    def prompt(self, messages):
        message_history = [
            {
                "role": "system",
                "content": "You are a helpful chatbot serving on a platform named ResQ. Answer the common crisis-related questions...",
            },
            {"role": "user", "content": messages},
        ]

        completion = openai.chat.completions.create(
            model=self.model,
            messages=message_history,
            tools=self.TOOL_DEFINITION,
        )

        while True:
            choice = completion.choices[0]
            # print(choice)

            if choice.message.tool_calls:
                tool_messages = []

                for tc in choice.message.tool_calls:
                    function_name = tc.function.name
                    function_args = json.loads(tc.function.arguments)
                    print(f"[INFO] Function Call: {function_name}({function_args})")

                    function_response = self.handle_function_call(
                        function_name, function_args
                    )
                    print(f"[INFO] Function Response: {function_response}")

                    tool_messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tc.id,
                            "content": json.dumps(function_response),
                        }
                    )

                message_history.append(choice.message.model_dump())

                message_history.extend(tool_messages)

                completion = openai.chat.completions.create(
                    model=self.model,
                    messages=message_history,
                    tools=self.TOOL_DEFINITION,
                )
            else:
                break

        return completion.choices[0].message.content

    def search_person(
        self, name: str | None = None, age: int | None = None, gender: str | None = None
    ):
        if name is None and age is None and gender is None:
            return "Please provide at least one of the following parameters: name, age, gender"
        params = {
            "key": "8b8f349b-a7f5-46dc-8e48-66a2df18e1e5",
            "action": "search",
        }
        if name is not None:
            params["name"] = name
        if age is not None:
            params["age"] = age
        if gender is not None:
            params["gender"] = gender

        response = req.get(
            f"https://xylem-api.ra-physics.space/administrator/missing-reports/",
            params=params,
        )
        print(response.url)
        if response.status_code != 200:
            return "Error occurred while fetching the data"
        print(response.json())
        results = response.json().get("results")
        return results if len(results) > 0 else "No results found"

    def handle_function_call(self, function_name, arguments):
        if function_name == "search_person":
            return self.search_person(**arguments)
        else:
            return "Unknown function"


if __name__ == "__main__":
    chatbot = ChatBot()
    while True:
        prompt = input(">> ")
        if prompt.lower() == "exit":
            break
        print(chatbot.prompt(prompt))
