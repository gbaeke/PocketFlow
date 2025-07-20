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

from ..flow import create_serial_tech_document_flow


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
    2. Researching technologies via web search
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
            
            # Use PocketFlow's flow execution
            await self._execute_pocketflow(shared)
            
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
    
    async def _execute_pocketflow(self, shared: Dict[str, Any]) -> None:
        """Execute the workflow using PocketFlow's serial flow execution."""
        self.logger.info("Starting PocketFlow serial execution")
        
        try:
            # Create and run the serial PocketFlow 
            flow = create_serial_tech_document_flow()
            await flow.run_async(shared)
            
            self.logger.info("PocketFlow execution completed successfully")
            
        except Exception as e:
            self.logger.error(f"PocketFlow execution failed: {e}")
            raise FlowExecutionError(f"Flow execution failed: {e}") from e
    
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