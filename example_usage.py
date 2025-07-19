#!/usr/bin/env python3
"""
Example usage of the Technology Document Generator class.

This script demonstrates how to use the encapsulated TechnologyDocumentGenerator
class for generating technology documentation.
"""
import os
import sys
from dotenv import load_dotenv

# Add the project root to Python path to import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.tech_doc_generator import (
    TechnologyDocumentGenerator, 
    GeneratorConfig, 
    TechDocGeneratorError
)


def basic_example():
    """Basic usage example with default configuration."""
    print("=== Basic Example ===")
    
    # Load environment variables
    load_dotenv()
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set")
        return
    
    # Create generator with default configuration
    generator = TechnologyDocumentGenerator()
    
    # Generate document
    technologies = ["Python", "Docker"]
    
    try:
        print(f"Generating document for: {', '.join(technologies)}")
        document = generator.invoke(technologies)
        
        # Save the document
        with open("example_basic.md", "w", encoding="utf-8") as f:
            f.write(document)
        
        print(f"✅ Document generated successfully!")
        print(f"📄 Saved to: example_basic.md")
        print(f"📊 Length: {len(document)} characters")
        
        # Show preview
        preview = document[:200] + "..." if len(document) > 200 else document
        print(f"\n📝 Preview:\n{preview}")
        
    except TechDocGeneratorError as e:
        print(f"❌ Generation failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


def advanced_example():
    """Advanced usage example with custom configuration."""
    print("\n=== Advanced Example ===")
    
    # Load environment variables
    load_dotenv()
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set")
        return
    
    # Create custom configuration
    config = GeneratorConfig(
        max_retries={
            'prepare': 1,
            'outline': 3,
            'research': 3,
            'merge': 2,
            'write': 5
        },
        wait_times={
            'prepare': 1,
            'outline': 2,
            'research': 3,
            'merge': 1,
            'write': 2
        },
        timeout_seconds=180,  # 3 minutes
        log_level="DEBUG"
    )
    
    # Create generator with custom configuration
    generator = TechnologyDocumentGenerator(config)
    
    # Generate document for more technologies
    technologies = ["React", "Node.js", "PostgreSQL", "Redis"]
    
    try:
        print(f"Generating document for: {', '.join(technologies)}")
        document = generator.invoke(technologies)
        
        # Save the document
        with open("example_advanced.md", "w", encoding="utf-8") as f:
            f.write(document)
        
        print(f"✅ Document generated successfully!")
        print(f"📄 Saved to: example_advanced.md")
        print(f"📊 Length: {len(document)} characters")
        print(f"📊 Word count: {len(document.split())} words")
        
    except TechDocGeneratorError as e:
        print(f"❌ Generation failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


def error_handling_example():
    """Example demonstrating error handling."""
    print("\n=== Error Handling Example ===")
    
    generator = TechnologyDocumentGenerator()
    
    # Test with invalid input
    test_cases = [
        [],  # Empty list
        [""],  # Empty string
        [123],  # Non-string
        ["Tech1", "Tech1"],  # Duplicates
    ]
    
    for i, test_input in enumerate(test_cases, 1):
        try:
            print(f"Test {i}: {test_input}")
            document = generator.invoke(test_input)
            print(f"  ✅ Unexpectedly succeeded")
        except TechDocGeneratorError as e:
            print(f"  ❌ Expected error: {e}")
        except Exception as e:
            print(f"  ❌ Unexpected error: {e}")


def main():
    """Run all examples."""
    print("Technology Document Generator - Usage Examples")
    print("=" * 50)
    
    # Run examples
    basic_example()
    advanced_example()
    error_handling_example()
    
    print("\n" + "=" * 50)
    print("Examples completed!")


if __name__ == "__main__":
    main()
