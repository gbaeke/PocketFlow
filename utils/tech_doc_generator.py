"""
Technology Document Generator - Encapsulated Workflow Class

This module provides a clean, encapsulated interface for generating comprehensive
technology documentation using the PocketFlow framework.
"""
import asyncio
import logging
import time
from typing import List, Dict, Optional, Any
from dataclasses import dataclass

from nodes import (
    PrepareDataNode,
    CreateOutlineNode,
    ResearchTechnologiesNode,
    MergeResultsNode,
    WriteDocumentNode
)


@dataclass
class GeneratorConfig:
    """Configuration for the Technology Document Generator."""
    max_retries: Dict[str, int] = None
    wait_times: Dict[str, int] = None
    timeout_seconds: int = 120
    enable_logging: bool = True
    log_level: str = "INFO"
    
    def __post_init__(self):
        if self.max_retries is None:
            self.max_retries = {
                'prepare': 1,
                'outline': 2,
                'research': 2,
                'merge': 1,
                'write': 3
            }
        if self.wait_times is None:
            self.wait_times = {
                'prepare': 1,
                'outline': 1,
                'research': 2,
                'merge': 1,
                'write': 1
            }


class TechDocGeneratorError(Exception):
    """Base exception for Technology Document Generator."""
    pass


class InputValidationError(TechDocGeneratorError):
    """Raised when input validation fails."""
    pass


class FlowExecutionError(TechDocGeneratorError):
    """Raised when flow execution fails."""
    pass


class OutputValidationError(TechDocGeneratorError):
    """Raised when output validation fails."""
    pass


class TechnologyDocumentGenerator:
    """
    Technology Document Generator - Encapsulated Workflow
    
    Generates comprehensive technology documentation by:
    1. Creating structured outlines
    2. Researching technologies in parallel via web search
    3. Writing comprehensive documents based on outline and research
    
    Usage:
        generator = TechnologyDocumentGenerator()
        document = generator.invoke(["FastAPI", "Vue.js", "Redis"])
    """
    
    def __init__(self, config: Optional[GeneratorConfig] = None):
        """
        Initialize the Technology Document Generator.
        
        Args:
            config: Optional configuration object. If None, uses defaults.
        """
        self.config = config or GeneratorConfig()
        self.logger = self._create_logger()
        self._nodes = {}  # Lazy-loaded node cache
        
        self.logger.info("Technology Document Generator initialized")
        self.logger.debug(f"Configuration: {self.config}")
    
    async def invoke(self, technologies: List[str]) -> str:
        """
        Generate a comprehensive technology document.
        
        Args:
            technologies: List of technology names to document
            
        Returns:
            Generated markdown document as string
            
        Raises:
            InputValidationError: If input validation fails
            FlowExecutionError: If workflow execution fails
            OutputValidationError: If output validation fails
        """
        start_time = time.time()
        
        try:
            # Validate inputs
            self._validate_inputs(technologies)
            
            # Initialize shared store
            shared = self._create_shared_store(technologies)
            
            # Execute the workflow
            await self._execute_workflow(shared)
            
            # Validate and return output
            document = self._validate_outputs(shared)
            
            execution_time = time.time() - start_time
            self.logger.info(f"Document generation completed successfully in {execution_time:.1f}s")
            self.logger.info(f"Generated document: {len(document)} characters")
            
            return document
            
        except (InputValidationError, FlowExecutionError, OutputValidationError):
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error in document generation: {e}")
            raise FlowExecutionError(f"Workflow execution failed: {e}") from e
    
    def _validate_inputs(self, technologies: List[str]) -> None:
        """Validate input technologies list."""
        if not technologies:
            raise InputValidationError("Technology list cannot be empty")
        
        if not isinstance(technologies, list):
            raise InputValidationError("Technologies must be provided as a list")
        
        for i, tech in enumerate(technologies):
            if not isinstance(tech, str):
                raise InputValidationError(f"Technology at index {i} must be a string, got {type(tech)}")
            
            if not tech.strip():
                raise InputValidationError(f"Technology at index {i} cannot be empty or whitespace only")
        
        # Clean up the technologies list
        cleaned_techs = [tech.strip() for tech in technologies]
        if len(set(cleaned_techs)) != len(cleaned_techs):
            raise InputValidationError("Duplicate technologies found in the list")
        
        self.logger.info(f"Input validation passed for {len(technologies)} technologies")
    
    def _validate_outputs(self, shared: Dict[str, Any]) -> str:
        """Validate and extract the final document."""
        document = shared.get("final_document")
        
        if not document:
            self.logger.error("No document was generated")
            self.logger.debug(f"Shared store contents: {list(shared.keys())}")
            raise OutputValidationError("Failed to generate document - no final_document in shared store")
        
        if not isinstance(document, str):
            raise OutputValidationError(f"Document must be a string, got {type(document)}")
        
        if len(document.strip()) < 100:  # Reasonable minimum length
            raise OutputValidationError(f"Generated document is too short ({len(document)} characters)")
        
        self.logger.info("Output validation passed")
        return document
    
    def _create_shared_store(self, technologies: List[str]) -> Dict[str, Any]:
        """Create and initialize the shared data store."""
        shared = {
            "technologies": [tech.strip() for tech in technologies],
            "outline": None,
            "research_results": None,
            "final_document": None,
            "outline_complete": False,
            "research_complete": False,
            "_start_time": time.time(),
            "_phase_times": {}
        }
        
        self.logger.debug("Shared store initialized")
        return shared
    
    async def _execute_workflow(self, shared: Dict[str, Any]) -> None:
        """Execute the complete workflow with parallel processing."""
        self.logger.info("Starting workflow execution")
        
        try:
            # Phase 1: Prepare data
            self.logger.info("Phase 1: Preparing data")
            phase_start = time.time()
            self._execute_prepare_node(shared)
            shared["_phase_times"]["prepare"] = time.time() - phase_start
            
            # Phase 2: Parallel execution (outline + research)
            self.logger.info("Phase 2: Parallel outline generation and research")
            phase_start = time.time()
            await self._execute_parallel_phase(shared)
            shared["_phase_times"]["parallel"] = time.time() - phase_start
            
            # Phase 3: Merge results
            self.logger.info("Phase 3: Merging results")
            phase_start = time.time()
            self._execute_merge_node(shared)
            shared["_phase_times"]["merge"] = time.time() - phase_start
            
            # Phase 4: Write document
            self.logger.info("Phase 4: Writing final document")
            phase_start = time.time()
            self._execute_write_node(shared)
            shared["_phase_times"]["write"] = time.time() - phase_start
            
            self.logger.info("Workflow execution completed successfully")
            self._log_performance_metrics(shared)
            
        except Exception as e:
            self.logger.error(f"Workflow execution failed: {e}")
            self._log_debug_info(shared)
            raise FlowExecutionError(f"Workflow execution failed at phase: {e}") from e
    
    def _execute_prepare_node(self, shared: Dict[str, Any]) -> None:
        """Execute the data preparation node."""
        node = self._get_node('prepare', PrepareDataNode)
        
        try:
            result = node.run(shared)
            self.logger.debug(f"Prepare node completed with action: {result}")
        except Exception as e:
            self.logger.error(f"Prepare node failed: {e}")
            raise FlowExecutionError(f"Data preparation failed: {e}") from e
    
    async def _execute_parallel_phase(self, shared: Dict[str, Any]) -> None:
        """Execute outline generation and research in parallel."""
        outline_node = self._get_node('outline', CreateOutlineNode)
        research_node = self._get_node('research', ResearchTechnologiesNode)
        
        async def run_outline():
            try:
                self.logger.debug("Starting outline generation")
                result = outline_node.run(shared)
                self.logger.debug(f"Outline generation completed with action: {result}")
                return result
            except Exception as e:
                self.logger.error(f"Outline generation failed: {e}")
                raise FlowExecutionError(f"Outline generation failed: {e}") from e
        
        async def run_research():
            try:
                self.logger.debug("Starting parallel research")
                result = await research_node.run_async(shared)
                self.logger.debug(f"Research completed with action: {result}")
                return result
            except Exception as e:
                self.logger.error(f"Research failed: {e}")
                raise FlowExecutionError(f"Research failed: {e}") from e
        
        # Execute both tasks in parallel
        try:
            outline_task = asyncio.create_task(run_outline())
            research_task = asyncio.create_task(run_research())
            
            await asyncio.gather(outline_task, research_task)
            self.logger.info("Parallel phase completed successfully")
            
        except Exception as e:
            self.logger.error(f"Parallel execution failed: {e}")
            raise
    
    def _execute_merge_node(self, shared: Dict[str, Any]) -> None:
        """Execute the results merging node."""
        node = self._get_node('merge', MergeResultsNode)
        
        try:
            result = node.run(shared)
            self.logger.debug(f"Merge node completed with action: {result}")
        except Exception as e:
            self.logger.error(f"Merge node failed: {e}")
            raise FlowExecutionError(f"Results merging failed: {e}") from e
    
    def _execute_write_node(self, shared: Dict[str, Any]) -> None:
        """Execute the document writing node."""
        node = self._get_node('write', WriteDocumentNode)
        
        try:
            result = node.run(shared)
            self.logger.debug(f"Write node completed with action: {result}")
        except Exception as e:
            self.logger.error(f"Write node failed: {e}")
            raise FlowExecutionError(f"Document writing failed: {e}") from e
    
    def _get_node(self, node_type: str, node_class) -> Any:
        """Get or create a node with proper configuration."""
        if node_type not in self._nodes:
            max_retries = self.config.max_retries.get(node_type, 1)
            wait_time = self.config.wait_times.get(node_type, 1)
            
            self._nodes[node_type] = node_class(
                max_retries=max_retries,
                wait=wait_time
            )
            
            self.logger.debug(f"Created {node_type} node with retries={max_retries}, wait={wait_time}")
        
        return self._nodes[node_type]
    
    def _create_logger(self) -> logging.Logger:
        """Create and configure a logger for this instance."""
        logger = logging.getLogger(f"{__name__}.TechnologyDocumentGenerator")
        
        if self.config.enable_logging and not logger.handlers:
            # Create handler only if logging is enabled and no handlers exist
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(getattr(logging, self.config.log_level.upper()))
        
        return logger
    
    def _log_performance_metrics(self, shared: Dict[str, Any]) -> None:
        """Log performance metrics for the workflow execution."""
        total_time = time.time() - shared["_start_time"]
        phase_times = shared.get("_phase_times", {})
        
        self.logger.info("=== Performance Metrics ===")
        self.logger.info(f"Total execution time: {total_time:.2f}s")
        
        for phase, duration in phase_times.items():
            percentage = (duration / total_time) * 100
            self.logger.info(f"  {phase.capitalize()}: {duration:.2f}s ({percentage:.1f}%)")
        
        # Document statistics
        document = shared.get("final_document", "")
        if document:
            lines = document.count('\n') + 1
            words = len(document.split())
            self.logger.info(f"Document stats: {len(document)} chars, {words} words, {lines} lines")
    
    def _log_debug_info(self, shared: Dict[str, Any]) -> None:
        """Log debug information for troubleshooting."""
        self.logger.debug("=== Debug Information ===")
        self.logger.debug(f"Technologies: {shared.get('technologies', 'None')}")
        self.logger.debug(f"Outline ready: {'✅' if shared.get('outline') else '❌'}")
        self.logger.debug(f"Research ready: {'✅' if shared.get('research_results') else '❌'}")
        self.logger.debug(f"Document ready: {'✅' if shared.get('final_document') else '❌'}")
        
        if shared.get('research_results'):
            research_count = len(shared['research_results'])
            self.logger.debug(f"Research completed for {research_count} technologies")
