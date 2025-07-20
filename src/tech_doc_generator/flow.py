"""
Serial flow definition for the Technology Document Generator.
Simple linear workflow: Prepare → Outline → Research → Write
"""
import logging
from pocketflow import AsyncFlow
from .nodes import (
    PrepareDataNode,
    CreateOutlineNode, 
    ResearchTechnologiesNode,
    WriteDocumentNode
)

# Set up logger for this module
logger = logging.getLogger(__name__)


def create_serial_tech_document_flow():
    """
    Create and return the serial technology document generation flow.
    
    Flow Structure:
    PrepareData → CreateOutline → ResearchTechnologies → WriteDocument
    
    Returns:
        AsyncFlow: The configured serial flow for generating technology documents
    """
    # Create all nodes
    prepare_node = PrepareDataNode(max_retries=2, wait=1)
    outline_node = CreateOutlineNode(max_retries=2, wait=1)
    research_node = ResearchTechnologiesNode(max_retries=2, wait=2)
    write_node = WriteDocumentNode(max_retries=3, wait=1)
    
    # Connect the flow structure serially
    prepare_node >> outline_node >> research_node >> write_node
    
    # Create the main async flow
    flow = AsyncFlow(start=prepare_node)
    
    logger.debug("Created serial flow: Prepare → Outline → Research → Write")
    return flow
