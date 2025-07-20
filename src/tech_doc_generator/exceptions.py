"""
Custom exceptions for the Technology Document Generator.

This module defines specific exceptions for different error conditions
that can occur during document generation workflow.
"""

from typing import List, Optional


class TechDocGeneratorError(Exception):
    """Base exception for Technology Document Generator."""
    pass


class InvalidTechnologyError(TechDocGeneratorError):
    """Raised when technology validation fails."""
    
    def __init__(self, message: str, invalid_technologies: Optional[List[str]] = None):
        super().__init__(message)
        self.invalid_technologies = invalid_technologies or []


class OutlineGenerationError(TechDocGeneratorError):
    """Raised when outline generation fails."""
    pass


class ResearchError(TechDocGeneratorError):
    """Raised when technology research fails."""
    
    def __init__(self, message: str, failed_technology: Optional[str] = None):
        super().__init__(message)
        self.failed_technology = failed_technology


class DocumentGenerationError(TechDocGeneratorError):
    """Raised when document generation fails."""
    pass


class YAMLParsingError(OutlineGenerationError):
    """Raised when YAML parsing fails during outline generation."""
    pass
