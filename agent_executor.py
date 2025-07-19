from a2a.server.agent_execution import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.utils import new_agent_text_message
from a2a.server.tasks import TaskUpdater
from a2a.utils.errors import ServerError
from dotenv import load_dotenv
import os
import logging
from a2a.types import (
    InternalError,
    Part,
    TextPart,
)
from utils.tech_doc_generator import TechnologyDocumentGenerator, GeneratorConfig, TechDocGeneratorError


# Set up logging
logger = logging.getLogger(__name__)


class TechnologyDocumentGeneratorExecutor(AgentExecutor):

    def __init__(self):
        logger.info("Initializing Technology Document Generator Executor...")
        self.agent = TechnologyDocumentGenerator()
        logger.info("Technology Document Generator Executor initialized successfully")

    async def execute(self, context: RequestContext, event_queue: EventQueue):
        logger.info("Starting Technology Document Generator Executor execution")

        message_text = context.get_user_input()  # helper method to extract the user input from the context
        logger.info(f"Message text: {message_text}")

        try:
            tech_list = [x.strip() for x in message_text.split(",") if x.strip()]
            if not tech_list:
                raise ValueError("No valid technologies found")
        except Exception as e:
            error_msg = "Invalid input. Please provide a comma-separated list of technologies."
            await event_queue.enqueue_event(new_agent_text_message(error_msg))
            return
        

        # invoke the agent with the user input
        result = await self.agent.invoke(tech_list)

        await event_queue.enqueue_event(new_agent_text_message(result))
        
        

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        logger.warning("Cancel operation requested")
        logger.error("Cancel not supported for Technology Document Generator Executor")
        raise Exception("Cancel not supported")
