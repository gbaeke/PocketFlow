"""
Validation utilities for the Technology Document Generator.

This module provides validation functions for inputs, outputs, and data
structures used throughout the document generation workflow.
"""

import re
from typing import Any, Dict, List

from .exceptions import InvalidTechnologyError, OutlineGenerationError


def validate_technologies(technologies: List[str]) -> List[str]:
    """
    Validate and clean a list of technology names.
    
    Args:
        technologies: List of technology names to validate.
        
    Returns:
        Cleaned and validated list of technology names.
        
    Raises:
        InvalidTechnologyError: If validation fails.
    """
    if not technologies:
        raise InvalidTechnologyError("No technologies provided")
    
    if not isinstance(technologies, list):
        raise InvalidTechnologyError("Technologies must be provided as a list")
    
    invalid_techs = []
    cleaned_technologies = []
    
    for tech in technologies:
        if not isinstance(tech, str):
            invalid_techs.append(str(tech))
            continue
            
        cleaned_tech = tech.strip()
        if not cleaned_tech:
            invalid_techs.append(tech)
            continue
            
        # Optional: Check for reasonable technology name format
        if len(cleaned_tech) > 100:  # Reasonable length limit
            invalid_techs.append(tech)
            continue
            
        cleaned_technologies.append(cleaned_tech)
    
    if invalid_techs:
        raise InvalidTechnologyError(
            f"Invalid technologies found: {invalid_techs}",
            invalid_technologies=invalid_techs
        )
    
    # Remove duplicates while preserving order
    seen = set()
    unique_technologies = []
    for tech in cleaned_technologies:
        tech_lower = tech.lower()
        if tech_lower not in seen:
            seen.add(tech_lower)
            unique_technologies.append(tech)
    
    return unique_technologies


def validate_outline_structure(outline: Dict[str, Any]) -> None:
    """
    Validate the structure of a generated outline.
    
    Args:
        outline: The outline dictionary to validate.
        
    Raises:
        OutlineGenerationError: If outline structure is invalid.
    """
    if not isinstance(outline, dict):
        raise OutlineGenerationError("Outline must be a dictionary")
    
    required_keys = ["title", "sections"]
    for key in required_keys:
        if key not in outline:
            raise OutlineGenerationError(f"Outline must have '{key}' field")
    
    if not isinstance(outline["title"], str) or not outline["title"].strip():
        raise OutlineGenerationError("Outline title must be a non-empty string")
    
    if not isinstance(outline["sections"], list):
        raise OutlineGenerationError("Outline sections must be a list")
    
    if not outline["sections"]:
        raise OutlineGenerationError("Outline must have at least one section")
    
    # Validate section structure
    for i, section in enumerate(outline["sections"]):
        if not isinstance(section, dict):
            raise OutlineGenerationError(f"Section {i} must be a dictionary")
        
        if "name" not in section:
            raise OutlineGenerationError(f"Section {i} must have a 'name' field")
        
        if not isinstance(section["name"], str) or not section["name"].strip():
            raise OutlineGenerationError(f"Section {i} name must be a non-empty string")


def validate_research_results(research_results: Dict[str, str], expected_technologies: List[str]) -> None:
    """
    Validate research results against expected technologies.
    
    Args:
        research_results: Dictionary mapping technology names to research content.
        expected_technologies: List of technologies that should have research results.
        
    Raises:
        ValueError: If research results are incomplete or invalid.
    """
    if not isinstance(research_results, dict):
        raise ValueError("Research results must be a dictionary")
    
    missing_technologies = []
    for tech in expected_technologies:
        if tech not in research_results:
            missing_technologies.append(tech)
        elif not isinstance(research_results[tech], str) or not research_results[tech].strip():
            missing_technologies.append(tech)
    
    if missing_technologies:
        raise ValueError(f"Missing or empty research results for: {missing_technologies}")


def validate_final_document(document: str, min_length: int = 100) -> str:
    """
    Validate the final generated document.
    
    Args:
        document: The generated document content.
        min_length: Minimum acceptable document length.
        
    Returns:
        The validated document.
        
    Raises:
        ValueError: If document validation fails.
    """
    if not isinstance(document, str):
        raise ValueError("Document must be a string")
    
    document = document.strip()
    if not document:
        raise ValueError("Document cannot be empty")
    
    if len(document) < min_length:
        raise ValueError(f"Document too short: {len(document)} chars (minimum: {min_length})")
    
    # Check for basic markdown structure
    if not any(line.strip().startswith('#') for line in document.split('\n')):
        raise ValueError("Document should contain markdown headings")
    
    return document
