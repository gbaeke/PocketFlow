"""
Utility functions for the Technology Document Generator.

This package provides utility functions for:
- LLM interactions (call_llm)
- Web searching (search_web, search_technology_info)
- Document generation (TechnologyDocumentGenerator)
"""

from .call_llm import call_llm
from .search_web import search_web, search_technology_info
from .tech_doc_generator import (
    TechnologyDocumentGenerator,
    GeneratorConfig,
    TechDocGeneratorError,
    InputValidationError,
    FlowExecutionError,
    OutputValidationError,
)

__all__ = [
    # LLM utilities
    "call_llm",
    # Search utilities
    "search_web",
    "search_technology_info",
    # Document generator
    "TechnologyDocumentGenerator",
    "GeneratorConfig",
    # Exceptions
    "TechDocGeneratorError",
    "InputValidationError", 
    "FlowExecutionError",
    "OutputValidationError",
]

__version__ = "1.0.0"
