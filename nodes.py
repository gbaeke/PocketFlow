"""
Node definitions for the Technology Document Generator.
"""
import yaml
import asyncio
import time
import logging
from pocketflow import Node, AsyncParallelBatchNode
from utils.call_llm import call_llm
from utils.search_web import search_technology_info

# Set up logger for this module
logger = logging.getLogger(__name__)


class PrepareDataNode(Node):
    """Prepares the initial data and distributes to parallel branches."""
    
    def prep(self, shared):
        """Read the list of technologies from shared store."""
        return shared["technologies"]
    
    def exec(self, technologies):
        """Validate and prepare technologies list."""
        if not technologies:
            raise ValueError("No technologies provided")
        
        logger.info(f"Preparing to process {len(technologies)} technologies: {', '.join(technologies)}")
        return technologies
    
    def post(self, shared, prep_res, exec_res):
        """Store the prepared data and initiate parallel processing."""
        shared["technologies"] = exec_res
        
        logger.info("Starting parallel outline generation and research...")
        return "default"


class MergeResultsNode(Node):
    """Waits for both outline and research to complete before proceeding."""
    
    def prep(self, shared):
        """Wait until both outline and research results are available."""
        logger.info("Waiting for outline and research to complete...")
        
        # Wait for both operations to complete
        max_wait = 120  # 2 minutes timeout
        wait_time = 0
        check_interval = 0.5  # Check every 0.5 seconds
        
        while wait_time < max_wait:
            outline_ready = shared.get("outline") is not None
            research_ready = shared.get("research_results") is not None
            
            if outline_ready and research_ready:
                logger.info("Both outline and research completed!")
                return {
                    "outline": shared["outline"],
                    "research": shared["research_results"],
                    "technologies": shared["technologies"]
                }
            
            # Show progress
            if wait_time % 5 == 0:  # Every 5 seconds
                status = []
                if outline_ready:
                    status.append("Outline ready")
                else:
                    status.append("Waiting for Outline")

                if research_ready:
                    status.append("Research ready")
                else:
                    status.append("Waiting for Research")
                    
                logger.info(f"Status: {' | '.join(status)}")
            
            time.sleep(check_interval)
            wait_time += check_interval
        
        # Timeout - check what's missing
        missing = []
        if not shared.get("outline"):
            missing.append("outline")
        if not shared.get("research_results"):
            missing.append("research results")
            
        logger.error(f"Timeout waiting for: {', '.join(missing)}")
        raise TimeoutError(f"Timeout waiting for: {', '.join(missing)}")
    
    def exec(self, data):
        """Validate that both results are properly formatted."""
        outline = data["outline"]
        research = data["research"]
        technologies = data["technologies"]
        
        # Validate outline
        if not isinstance(outline, dict) or "title" not in outline:
            raise ValueError("Invalid outline structure")
        
        # Validate research results
        if not isinstance(research, dict) or len(research) == 0:
            raise ValueError("Invalid research results")
        
        # Check that we have research for each technology
        for tech in technologies:
            if tech not in research:
                logger.warning(f"No research found for {tech}")
        
        logger.info("Merge validation complete:")
        logger.info(f"  - Outline: {outline.get('title', 'No title')}")
        logger.info(f"  - Research: {len(research)} technologies researched")
        
        return data
    
    def post(self, shared, prep_res, exec_res):
        """Mark merge as complete and proceed to document writing."""
        logger.info("Proceeding to document generation...")
        return "default"


class CreateOutlineNode(Node):
    """Creates a structured outline for the technology document."""
    
    def prep(self, shared):
        """Read the list of technologies from shared store."""
        return shared["technologies"]
    
    def exec(self, technologies):
        """Generate a structured outline using LLM."""
        tech_list = ", ".join(technologies)
        
        prompt = f"""
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
            assert isinstance(outline, dict), "Outline must be a dictionary"
            assert "title" in outline, "Outline must have a title"
            assert "sections" in outline, "Outline must have sections"
            assert isinstance(outline["sections"], list), "Sections must be a list"
            
            return outline
            
        except Exception as e:
            raise ValueError(f"Failed to parse outline YAML: {e}")
    
    def post(self, shared, prep_res, exec_res):
        """Store the generated outline in shared store."""
        shared["outline"] = exec_res
        shared["outline_complete"] = True
        logger.info(f"Outline generated: {exec_res.get('title', 'No title')}")
        return "default"


class ResearchTechnologiesNode(AsyncParallelBatchNode):
    """Researches each technology in parallel using web search."""
    
    async def prep_async(self, shared):
        """Read the list of technologies to research."""
        return shared["technologies"]
    
    async def exec_async(self, technology):
        """Research a single technology using web search."""
        # Run the synchronous search function in a thread pool
        loop = asyncio.get_event_loop()
        research_results = await loop.run_in_executor(
            None, 
            search_technology_info, 
            technology
        )
        return {"technology": technology, "research": research_results}
    
    async def post_async(self, shared, prep_res, exec_res_list):
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
    
    def prep(self, shared):
        """Read outline and research results from shared store."""
        outline = shared["outline"]
        research_results = shared["research_results"]
        technologies = shared["technologies"]
        
        return {
            "outline": outline,
            "research": research_results,
            "technologies": technologies
        }
    
    def exec(self, data):
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
        
        document = call_llm(prompt, max_tokens=4000)
        return document
    
    def post(self, shared, prep_res, exec_res):
        """Store the final document in shared store."""
        shared["final_document"] = exec_res
        logger.info("Document generated successfully!")
        logger.info(f"Document length: {len(exec_res)} characters")
        return "default"
