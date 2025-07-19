"""
Technology Document Generator - Main Application

This application generates comprehensive technology documentation by:
1. Creating an outline for the given technologies
2. Researching each technology on the web (in parallel)
3. Writing a comprehensive document based on outline and research

The implementation uses an encapsulated workflow class with parallel execution.

Usage:
    python main.py                    # Run with default technologies
    python main.py --interactive      # Interactive mode for custom technologies

Requirements:
    - Set OPENAI_API_KEY environment variable or in .env file
    - Install dependencies: openai, requests, beautifulsoup4, pyyaml, python-dotenv
"""
import os
import time
import logging
import sys
import datetime
from dotenv import load_dotenv
from utils.tech_doc_generator import TechnologyDocumentGenerator, GeneratorConfig, TechDocGeneratorError

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


def main():
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
    logger.info("Using encapsulated workflow with parallel execution")
    
    try:
        # Record start time
        start_time = time.time()
        
        logger.info("Starting document generation...")
        
        # Create generator with default configuration
        generator = TechnologyDocumentGenerator()
        
        # Generate the document
        document = generator.invoke(technologies)
        
        # Record end time
        end_time = time.time()
        execution_time = end_time - start_time
        
        logger.info("Document generation completed successfully!")
        logger.info(f"Total execution time: {execution_time:.1f} seconds")
        
        # Save to file with timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"tech_doc_{timestamp}.md"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(document)
        
        logger.info(f"Full document saved to: {output_file}")
        
    except TechDocGeneratorError as e:
        logger.error(f"Document generation failed: {e}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1
    
    return 0


def interactive_main():
    """Interactive version where user can input technologies."""
    logger.info("Technology Document Generator - Interactive Mode")

    # Load environment variables from .env file
    load_dotenv()
    logger.info("Environment variables loaded from .env file")
    
    # Check for required environment variables
    if not os.getenv("OPENAI_API_KEY"):
        logger.error("OPENAI_API_KEY environment variable not set")
        return 1
    
    logger.info("OpenAI API key found and configured")
    
    # Get technologies from user
    print("\nEnter technologies to research (comma-separated):")
    print("Example: FastAPI, Vue.js, Redis, Docker")
    user_input = input("> ").strip()
    
    if not user_input:
        logger.warning("No technologies provided. Using default list.")
        technologies = ["FastAPI", "Vue.js"]
    else:
        technologies = [tech.strip() for tech in user_input.split(",")]
    
    logger.info(f"Selected technologies: {', '.join(technologies)}")
    
    try:
        start_time = time.time()
        logger.info("Starting interactive document generation...")
        
        # Create generator with custom configuration for interactive mode
        config = GeneratorConfig(
            max_retries={
                'prepare': 1,
                'outline': 3,  # More retries for interactive mode
                'research': 3,
                'merge': 1,
                'write': 4
            }
        )
        generator = TechnologyDocumentGenerator(config)
        
        # Generate the document
        document = generator.invoke(technologies)
        
        execution_time = time.time() - start_time
        
        # Save document
        tech_names = [tech.lower().replace(' ', '_') for tech in technologies[:3]]
        filename = f"interactive_{'_'.join(tech_names)}.md"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(document)
        
        logger.info(f"Document saved to: {filename}")
        logger.info(f"Execution time: {execution_time:.1f} seconds")
        
        # Log document statistics
        doc_length = len(document)
        word_count = len(document.split())
        logger.info(f"Generated document: {doc_length} characters, {word_count} words")
        
    except TechDocGeneratorError as e:
        logger.error(f"Interactive document generation failed: {e}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error in interactive mode: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    # Check if user wants interactive mode
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        exit_code = interactive_main()
    else:
        exit_code = main()
    
    sys.exit(exit_code)
