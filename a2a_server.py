import logging
import os
import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from agent_executor import TechnologyDocumentGeneratorExecutor
from dotenv import load_dotenv

load_dotenv()

def main():
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s:     %(message)s'
    )

    A2A_SERVER_BASE_URL = os.getenv("A2A_SERVER_BASE_URL", "http://localhost")
    A2A_SERVER_PORT = int(os.getenv("A2A_SERVER_PORT", 9997))

    # Suppress Azure SDK logs - only show warnings and errors
    logging.getLogger('azure').setLevel(logging.WARNING)
    logging.getLogger('azure.ai').setLevel(logging.WARNING)
    logging.getLogger('azure.identity').setLevel(logging.WARNING)
    logging.getLogger('azure.core').setLevel(logging.WARNING)

    # Suppress other verbose libraries
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)

    # Keep your application logs visible
    logging.getLogger('agent_executor').setLevel(logging.INFO)

    skill = AgentSkill(
        id="DocumentGenerator",
        name="Document Generator",
        description="Generates comprehensive technology documentation",
        tags=["document", "generation", "technology"],
        examples=["FastAPI,Docker,Kubernetes"],
    )

    agent_card = AgentCard(
        name="Document Generator Agent",
        description="An agent that generates documentation for various technologies",
        url=f"{A2A_SERVER_BASE_URL}:{A2A_SERVER_PORT}/",
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        skills=[skill],
        version="1.0.0",
        capabilities=AgentCapabilities(),
    )

    request_handler = DefaultRequestHandler(
        agent_executor=TechnologyDocumentGeneratorExecutor(),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        http_handler=request_handler,
        agent_card=agent_card,
    )

    uvicorn.run(server.build(), host="0.0.0.0", port=A2A_SERVER_PORT)


if __name__ == "__main__":
    main()
