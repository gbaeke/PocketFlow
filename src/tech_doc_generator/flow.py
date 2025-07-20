"""
Serial flow definition for the Technology Document Generator.
Simple linear workflow: Validate → Prepare → Outline → Research → Write
"""
import logging
from pocketflow import AsyncFlow
from .nodes import (
    ValidateRequestNode,
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
    ValidateRequest → PrepareData → CreateOutline → ResearchTechnologies → WriteDocument
    (Flow stops if validation fails)
    
    Returns:
        AsyncFlow: The configured serial flow for generating technology documents
    """
    # Create all nodes
    validate_node = ValidateRequestNode(max_retries=2, wait=1)
    prepare_node = PrepareDataNode(max_retries=2, wait=1)
    outline_node = CreateOutlineNode(max_retries=2, wait=1)
    research_node = ResearchTechnologiesNode(max_retries=2, wait=2)
    write_node = WriteDocumentNode(max_retries=2, wait=1)
    
    # Connect the flow structure with branching
    validate_node - "valid" >> prepare_node
    # If validation fails ("invalid"), flow stops (no connection)
    
    prepare_node >> outline_node >> research_node >> write_node
    
    # Create the main async flow starting with validation
    flow = AsyncFlow(start=validate_node)
    
    logger.debug("Created serial flow: Validate → Prepare → Outline → Research → Write")
    return flow
