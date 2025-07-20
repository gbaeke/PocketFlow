"""
Node definitions for the Technology Document Generator.
"""
import asyncio
import logging
import time
from typing import Any, Dict, List

import yaml
from pocketflow import AsyncParallelBatchNode, Node

from .constants import DEFAULT_DOCUMENT_MAX_TOKENS
from .exceptions import OutlineGenerationError, YAMLParsingError
from .utils.call_llm import call_llm
from .utils.search_web import search_technology_info
from .validators import validate_outline_structure, validate_technologies

# Module exports
__all__ = [
    "PrepareDataNode",
    "CreateOutlineNode", 
    "ResearchTechnologiesNode",
    "WriteDocumentNode",
]

# Constants
DEFAULT_DOCUMENT_MAX_TOKENS = 4000

YAML_OUTLINE_TEMPLATE = """
Create a comprehensive outline for a technology document covering these technologies: {tech_list}

The document should have:
1. An introduction section
2. A dedicated section for each technology covering:
   - Overview and description
   - Latest version and recent updates
   - Key features and capabilities
   - Use cases and applications
   - Pros and cons
3. A comparison section
4. A conclusion section

Please format the response as YAML with this structure:

```yaml
title: "Technology Overview: [list of technologies]"
sections:
  - name: "Introduction"
    subsections:
      - "Purpose of this document"
      - "Technologies covered"
  - name: "[Technology 1 Name]"
    subsections:
      - "Overview"
      - "Latest Version and Updates"
      - "Key Features"
      - "Use Cases"
      - "Pros and Cons"
  # ... repeat for each technology
  - name: "Technology Comparison"
    subsections:
      - "Feature comparison"
      - "Performance considerations"
  - name: "Conclusion"
    subsections:
      - "Summary"
      - "Recommendations"
```
"""

# Set up logger for this module
logger = logging.getLogger(__name__)


class PrepareDataNode(Node):
    """Prepares the initial data.
    
    This node validates and cleans the input technologies list before
    passing it to subsequent nodes in the workflow.
    """
    
    def prep(self, shared: Dict[str, Any]) -> List[str]:
        """Read the list of technologies from shared store.
        
        Args:
            shared: Shared data store containing workflow data.
            
        Returns:
            List of technology names to process.
        """
        return shared["technologies"]
    
    def exec(self, technologies: List[str]) -> List[str]:
        """Validate and prepare technologies list.
        
        Args:
            technologies: List of technology names to validate and clean.
            
        Returns:
            Cleaned and validated list of technology names.
            
        Raises:
            ValueError: If no technologies provided or if any technology is invalid.
        """
        if not technologies:
            raise ValueError("No technologies provided")
        
        if not all(isinstance(tech, str) and tech.strip() for tech in technologies):
            raise ValueError("All technologies must be non-empty strings")
        
        # Clean and validate technologies
        cleaned_technologies = [tech.strip() for tech in technologies]
        
        logger.info(f"Preparing to process {len(cleaned_technologies)} technologies: {', '.join(cleaned_technologies)}")
        return cleaned_technologies
    
    def post(self, shared: Dict[str, Any], prep_res: List[str], exec_res: List[str]) -> str:
        """Store the prepared data and initiate processing.
        
        Args:
            shared: Shared data store for workflow data.
            prep_res: Result from prep phase (unused).
            exec_res: Cleaned technologies list from exec phase.
            
        Returns:
            Next node identifier ("default").
        """
        shared["technologies"] = exec_res
        
        logger.info("Starting outline generation and research...")
        return "default"


class CreateOutlineNode(Node):
    """Creates a structured outline for the technology document.
    
    This node generates a comprehensive YAML-structured outline that will
    guide the document generation process, including sections for each
    technology and comparison sections.
    """
    
    def prep(self, shared: Dict[str, Any]) -> List[str]:
        """Read the list of technologies from shared store.
        
        Args:
            shared: Shared data store containing workflow data.
            
        Returns:
            List of technologies to create outline for.
        """
        return shared["technologies"]
    
    def exec(self, technologies: List[str]) -> Dict[str, Any]:
        """Generate a structured outline using LLM.
        
        Args:
            technologies: List of technology names to include in outline.
            
        Returns:
            Dictionary containing the structured outline with title and sections.
            
        Raises:
            ValueError: If outline generation or YAML parsing fails.
        """
        tech_list = ", ".join(technologies)
        
        prompt = YAML_OUTLINE_TEMPLATE.format(tech_list=tech_list)
        
        response = call_llm(prompt)
        
        # Extract YAML from response
        try:
            yaml_start = response.find("```yaml")
            yaml_end = response.find("```", yaml_start + 7)
            
            if yaml_start != -1 and yaml_end != -1:
                yaml_content = response[yaml_start + 7:yaml_end].strip()
                outline = yaml.safe_load(yaml_content)
            else:
                # Fallback: try to parse the entire response as YAML
                outline = yaml.safe_load(response)
            
            # Validate outline structure
            if not isinstance(outline, dict):
                raise ValueError("Outline must be a dictionary")
            if "title" not in outline:
                raise ValueError("Outline must have a title")
            if "sections" not in outline:
                raise ValueError("Outline must have sections")
            if not isinstance(outline["sections"], list):
                raise ValueError("Sections must be a list")
            
            return outline
            
        except Exception as e:
            raise ValueError(f"Failed to parse outline YAML: {e}") from e
    
    def post(self, shared: Dict[str, Any], prep_res: List[str], exec_res: Dict[str, Any]) -> str:
        """Store the generated outline in shared store."""
        shared["outline"] = exec_res
        shared["outline_complete"] = True
        logger.info(f"Outline generated: {exec_res.get('title', 'No title')}")
        return "default"


class ResearchTechnologiesNode(AsyncParallelBatchNode):
    """Researches each technology in parallel using web search."""
    
    async def prep_async(self, shared: Dict[str, Any]) -> List[str]:
        """Read the list of technologies to research."""
        return shared["technologies"]
    
    async def exec_async(self, technology: str) -> Dict[str, str]:
        """Research a single technology using web search."""
        # Run the synchronous search function in a thread pool
        loop = asyncio.get_event_loop()
        research_results = await loop.run_in_executor(
            None, 
            search_technology_info, 
            technology
        )
        return {"technology": technology, "research": research_results}
    
    async def post_async(self, shared: Dict[str, Any], prep_res: List[str], exec_res_list: List[Dict[str, str]]) -> str:
        """Store all research results in shared store."""
        research_results = {}
        for result in exec_res_list:
            tech_name = result["technology"]
            research_data = result["research"]
            research_results[tech_name] = research_data
        
        shared["research_results"] = research_results
        shared["research_complete"] = True
        logger.info(f"Research completed for {len(research_results)} technologies")
        return "default"


class WriteDocumentNode(Node):
    """Writes the final comprehensive document using outline and research."""
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Read outline and research results from shared store."""
        outline = shared["outline"]
        research_results = shared["research_results"]
        technologies = shared["technologies"]
        
        return {
            "outline": outline,
            "research": research_results,
            "technologies": technologies
        }
    
    def exec(self, data: Dict[str, Any]) -> str:
        """Generate the comprehensive document using LLM."""
        outline = data["outline"]
        research_results = data["research"]
        technologies = data["technologies"]
        
        # Prepare research summary for the prompt
        research_summary = ""
        for tech, research in research_results.items():
            research_summary += f"\n=== {tech} Research ===\n{research}\n"
        
        prompt = f"""
Write a comprehensive technology document based on the following outline and research data.

OUTLINE:
{yaml.dump(outline, default_flow_style=False)}

RESEARCH DATA:
{research_summary}

INSTRUCTIONS:
1. Follow the outline structure exactly
2. Use the research data to provide accurate, up-to-date information
3. Write in a professional, informative tone
4. Include specific version numbers and recent updates where available
5. Make each section substantial and informative (at least 2-3 paragraphs per subsection)
6. Use markdown formatting for headings, lists, and emphasis
7. Ensure the document flows well and is cohesive

Start with the title as an H1 heading and structure the content according to the outline.
"""
        
        document = call_llm(prompt, max_tokens=DEFAULT_DOCUMENT_MAX_TOKENS)
        return document
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: str) -> str:
        """Store the final document in shared store."""
        shared["final_document"] = exec_res
        logger.info("Document generated successfully!")
        logger.info(f"Document length: {len(exec_res)} characters")
        return "default"
