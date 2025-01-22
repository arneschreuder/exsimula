import os
from typing import Dict, Optional, Tuple
from openai import OpenAI
from exsimula.graph import Edge, Node
from dotenv import load_dotenv

load_dotenv()


client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),  # This is the default and can be omitted
)

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "Say this is a test",
        }
    ],
    model="gpt-4o",
)


class OpenAILLM(Node):
    client: OpenAI

    def __init__(self, id: Optional[str] = None):
        super().__init__(id)
        self.client

    def __call__(self, state: Dict) -> Tuple[Dict, Optional[Edge]]:
        chat_completion = self.client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": "Say this is a test",
                }
            ],
            model="gpt-3.5-turbo",
        )
        return chat_completion.choices[0].message, None
