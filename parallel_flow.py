"""
Parallel flow definition for the Technology Document Generator.
Implements Split-Merge pattern for concurrent outline and research.
"""
import asyncio
import logging
from pocketflow import AsyncFlow, Flow
from nodes import (
    PrepareDataNode, 
    CreateOutlineNode, 
    ResearchTechnologiesNode, 
    MergeResultsNode,
    WriteDocumentNode
)

# Set up logger for this module
logger = logging.getLogger(__name__)


def create_parallel_tech_document_flow():
    """
    Create and return the parallel technology document generation flow.
    
    Flow Structure:
    PrepareData → [Outline || Research] → Merge → WriteDocument
    
    Returns:
        AsyncFlow: The configured parallel flow for generating technology documents
    """
    # Create all nodes
    prepare_node = PrepareDataNode(max_retries=2, wait=1)
    outline_node = CreateOutlineNode(max_retries=2, wait=1)
    research_node = ResearchTechnologiesNode(max_retries=2, wait=2)
    merge_node = MergeResultsNode(max_retries=1, wait=1)
    write_node = WriteDocumentNode(max_retries=3, wait=1)
    
    # Create sub-flows for parallel execution
    outline_flow = Flow(start=outline_node)
    research_flow = AsyncFlow(start=research_node)
    
    # Connect the main flow structure
    # Note: In PocketFlow, we need to manually coordinate parallel execution
    # This is done by having both outline and research nodes write to shared store
    # and the merge node waits for both
    
    prepare_node >> merge_node  # Prepare connects to merge (merge waits for parallel completion)
    merge_node >> write_node    # After merge, proceed to write
    
    # Create the main async flow
    main_flow = AsyncFlow(start=prepare_node)
    
    # Store references to parallel sub-flows for manual execution
    main_flow._outline_flow = outline_flow
    main_flow._research_flow = research_flow
    
    return main_flow


async def run_parallel_flow(shared):
    """
    Custom runner for parallel execution since PocketFlow doesn't have 
    built-in parallel branching. This manually coordinates the parallel execution.
    
    Args:
        shared (dict): The shared data store
    """
    logger.info("Starting parallel flow execution")
    
    # Step 1: Run prepare node
    prepare_node = PrepareDataNode()
    logger.debug("Executing PrepareDataNode")
    prepare_node.run(shared)
    
    # Step 2: Run outline and research in parallel
    outline_node = CreateOutlineNode(max_retries=2, wait=1)
    research_node = ResearchTechnologiesNode(max_retries=2, wait=2)
    
    logger.info("Starting parallel execution of outline and research")
    
    # Create tasks for parallel execution
    async def run_outline():
        logger.debug("Running outline generation in parallel")
        return outline_node.run(shared)
    
    async def run_research():
        logger.debug("Running research in parallel")
        return await research_node.run_async(shared)
    
    # Execute both in parallel
    outline_task = asyncio.create_task(run_outline())
    research_task = asyncio.create_task(run_research())
    
    # Wait for both to complete
    try:
        await asyncio.gather(outline_task, research_task)
        logger.info("Parallel outline and research completed successfully")
    except Exception as e:
        logger.error(f"Error during parallel execution: {e}")
        raise
    
    # Step 3: Run merge and write sequentially
    merge_node = MergeResultsNode()
    write_node = WriteDocumentNode(max_retries=3, wait=1)
    
    logger.debug("Executing MergeResultsNode")
    merge_node.run(shared)
    
    logger.debug("Executing WriteDocumentNode")
    write_node.run(shared)
    
    logger.info("Parallel flow execution completed successfully")
    return shared
