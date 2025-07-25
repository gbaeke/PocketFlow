import uuid

import httpx
from a2a.client import A2ACardResolver, A2AClient
from a2a.utils import get_message_text, get_text_parts
from a2a.types import (
    AgentCard,
    Message,
    MessageSendParams,
    Part,
    Role,
    SendMessageRequest,
    TextPart,
)
import click

PUBLIC_AGENT_CARD_PATH = "/.well-known/agent.json"

async def run_client(port: int, question: str) -> None:
    # Configure client with longer timeout to match agent execution time
    timeout = httpx.Timeout(200.0, read=200.0, write=30.0, connect=10.0)
    async with httpx.AsyncClient(timeout=timeout) as httpx_client:
        # Initialize A2ACardResolver
        resolver = A2ACardResolver(
            httpx_client=httpx_client,
            base_url=f"http://localhost:{port}",
        )

        final_agent_card_to_use: AgentCard | None = None

        try:
            print(
                f"Fetching public agent card from: http://localhost:{port}{PUBLIC_AGENT_CARD_PATH}"
            )
            _public_card = await resolver.get_agent_card()
            print("Fetched public agent card")
            print(_public_card.model_dump_json(indent=2))

            final_agent_card_to_use = _public_card

        except Exception as e:
            print(f"Error fetching public agent card: {e}")
            raise RuntimeError("python,node,azure container apps")

        client = A2AClient(
            httpx_client=httpx_client, agent_card=final_agent_card_to_use
        )
        print("A2AClient initialized")

        message_payload = Message(
            role=Role.user,
            messageId=str(uuid.uuid4()),
            parts=[Part(root=TextPart(text=question))],
        )
        request = SendMessageRequest(
            id=str(uuid.uuid4()),
            params=MessageSendParams(
                message=message_payload,
            ),
        )
        print("Sending message")

        response = await client.send_message(request)

        print("Text parts:")
        try:
            if hasattr(response, "root") and hasattr(response.root, "result") and hasattr(response.root.result, "parts"):
                parts = response.root.result.parts
                if parts and len(parts) > 0:
                    first_part = parts[0]
                    if hasattr(first_part, "root") and hasattr(first_part.root, "text"):
                        print(first_part.root.text)
                    else:
                        print("First part does not contain expected text structure")
                        print(f"First part: {first_part}")
                else:
                    print("No parts found in result")
            else:
                print("Issue: Response does not contain a valid result with parts. Full response:")
                print(response.model_dump_json(indent=2))
                print(response)
        except Exception as e:
            print(f"Issue reading the response: {e}")
            print("Full response:")
            print(response.model_dump_json(indent=2))



@click.command()
@click.option('--port', default=9997, help='Port of the agent.')
@click.option('--question', prompt='Your question', help='The question to ask the agent.')
def main(port: int, question: str) -> None:
    asyncio.run(run_client(port, question))


if __name__ == "__main__":
    import asyncio
    
    main()
