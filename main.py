"""
Technology Document Generator - Main Application

This application generates comprehensive technology documentation by:
1. Creating an outline for the given technologies
2. Researching each technology on the web (in parallel)
3. Writing a comprehensive document based on outline and research

The implementation uses a parallel execution pattern where outline generation
and research happen simultaneously for improved performance.

Usage:
    python main.py

Requirements:
    - Set OPENAI_API_KEY environment variable or in .env file
    - Install dependencies: openai, requests, beautifulsoup4, pyyaml, python-dotenv
"""
import os
import asyncio
import time
import logging
import sys
from dotenv import load_dotenv
from parallel_flow import run_parallel_flow

# Configure logging
def setup_logging():
    """Set up logging configuration for the application."""
    # Create formatter with module name for clear identification
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Configure root logger to handle all modules
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)
    
    # Get logger for this module
    logger = logging.getLogger(__name__)
    
    return logger

# Initialize logger
logger = setup_logging()


async def main():
    """Main function to run the technology document generator."""
    
    # Load environment variables from .env file
    load_dotenv()
    logger.info("Environment variables loaded from .env file")
    
    # Check for required environment variables
    if not os.getenv("OPENAI_API_KEY"):
        logger.error("OPENAI_API_KEY environment variable not set")
        return
    
    logger.info("OpenAI API key found and configured")
    
    # Example technologies - you can modify this list
    technologies = [
        "FastAPI",
        "Vue.js",
        "Redis"
    ]
    
    logger.info("Technology Document Generator")
    logger.info(f"Technologies to research: {', '.join(technologies)}")
    logger.info("Outline generation and research will run in parallel")
    
    # Initialize shared store
    shared = {
        "technologies": technologies,
        "outline": None,
        "research_results": None,
        "final_document": None
    }
    
    try:
        # Record start time
        start_time = time.time()
        
        logger.info("Starting parallel execution...")
        
        # Run the parallel flow
        await run_parallel_flow(shared)
        
        # Record end time
        end_time = time.time()
        execution_time = end_time - start_time
        
        logger.info("Parallel document generation completed successfully!")
        logger.info(f"Total execution time: {execution_time:.1f} seconds")
        
        # Display first 500 characters of the document
        document = shared["final_document"]
        if document:
            # Save to file with timestamp
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"tech_doc_parallel_{timestamp}.md"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(document)
            
            logger.info(f"Full document saved to: {output_file}")
            
        else:
            logger.error("No document was generated")
            
    except Exception as e:
        logger.error(f"Error during parallel document generation: {e}")
        logger.info("Debugging information:")
        logger.info(f"- Outline generated: {'✅' if shared.get('outline') else '❌'}")
        logger.info(f"- Research completed: {'✅' if shared.get('research_results') else '❌'}")
        logger.info(f"- Document written: {'✅' if shared.get('final_document') else '❌'}")


async def interactive_main():
    """Interactive version where user can input technologies."""
    logger.info("Technology Document Generator starting in Interactive Parallel Mode")

    # Load environment variables from .env file
    load_dotenv()
    logger.info("Environment variables loaded from .env file")
    
    # Check for required environment variables
    if not os.getenv("OPENAI_API_KEY"):
        logger.error("OPENAI_API_KEY environment variable not set")
        return
    
    logger.info("OpenAI API key found and configured")
    
    # Get technologies from user
    logger.info("Enter technologies to research (comma-separated):")
    logger.info("Example: FastAPI, Vue.js, Redis, Docker")
    user_input = input("> ").strip()
    
    if not user_input:
        logger.warning("No technologies provided. Using default list.")
        technologies = ["FastAPI", "Vue.js"]
    else:
        technologies = [tech.strip() for tech in user_input.split(",")]
    
    logger.info(f"Selected technologies: {', '.join(technologies)}")
    logger.info("Will run outline generation and research in parallel")
    
    # Update the shared store and run
    shared = {
        "technologies": technologies,
        "outline": None,
        "research_results": None,
        "final_document": None
    }
    
    try:
        start_time = time.time()
        logger.info("Starting interactive parallel flow execution...")
        
        await run_parallel_flow(shared)
        execution_time = time.time() - start_time
        
        # Save document
        if shared.get("final_document"):
            tech_names = [tech.lower().replace(' ', '_') for tech in technologies[:3]]
            filename = f"interactive_parallel_{'_'.join(tech_names)}.md"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(shared["final_document"])
            
            logger.info(f"Document saved to: {filename}")
            logger.info(f"Parallel execution time: {execution_time:.1f} seconds")
            
            # Log document statistics
            doc_length = len(shared["final_document"])
            logger.info(f"Generated document length: {doc_length} characters")
        else:
            logger.error("No document was generated in interactive mode")
            
    except Exception as e:
        logger.error(f"Error in interactive mode: {e}")
        logger.error("Interactive execution failed")


if __name__ == "__main__":
    # Check if user wants interactive mode
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        asyncio.run(interactive_main())
    else:
        asyncio.run(main())
