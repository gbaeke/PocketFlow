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
from dotenv import load_dotenv
from parallel_flow import run_parallel_flow


async def main():
    """Main function to run the technology document generator."""
    
    # Load environment variables from .env file
    load_dotenv()
    
    # Check for required environment variables
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY environment variable not set")
        print("Please set your OpenAI API key in .env file or environment variable:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        return
    
    # Example technologies - you can modify this list
    technologies = [
        "FastAPI",
        "Vue.js",
        "Redis"
    ]
    
    print("🚀 Technology Document Generator (PARALLEL MODE)")
    print("=" * 60)
    print(f"Technologies to research: {', '.join(technologies)}")
    print("🔄 Outline generation and research will run in parallel")
    print()
    
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
        
        print("� Starting parallel execution...")
        
        # Run the parallel flow
        await run_parallel_flow(shared)
        
        # Record end time
        end_time = time.time()
        execution_time = end_time - start_time
        
        print(f"\n✅ Parallel document generation completed!")
        print(f"⏱️  Total execution time: {execution_time:.1f} seconds")
        print(f"📄 Final document preview:")
        print("=" * 50)
        
        # Display first 500 characters of the document
        document = shared["final_document"]
        if document:
            preview = document[:500] + "..." if len(document) > 500 else document
            print(preview)
            
            # Save to file with timestamp
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"tech_doc_parallel_{timestamp}.md"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(document)
            
            print(f"\n💾 Full document saved to: {output_file}")
            print(f"📊 Document stats:")
            print(f"   - Length: {len(document)} characters")
            print(f"   - Lines: {document.count(chr(10)) + 1}")
            print(f"   - Technologies covered: {len(technologies)}")
            print(f"   - Execution time: {execution_time:.1f}s")
            
            # Show research results summary
            if shared.get("research_results"):
                print(f"\n🔍 Research completed for:")
                for tech in shared["research_results"].keys():
                    print(f"   - {tech}")
        else:
            print("❌ No document was generated")
            
    except Exception as e:
        print(f"❌ Error during parallel document generation: {e}")
        print("\nDebugging information:")
        print(f"- Outline generated: {'✅' if shared.get('outline') else '❌'}")
        print(f"- Research completed: {'✅' if shared.get('research_results') else '❌'}")
        print(f"- Document written: {'✅' if shared.get('final_document') else '❌'}")
        
        # Show any partial results
        if shared.get("outline"):
            print(f"- Outline title: {shared['outline'].get('title', 'No title')}")
        if shared.get("research_results"):
            print(f"- Research count: {len(shared['research_results'])} technologies")


async def interactive_main():
    """Interactive version where user can input technologies."""
    print("🚀 Technology Document Generator (Interactive Parallel Mode)")
    print("=" * 60)
    
    # Get technologies from user
    print("Enter technologies to research (comma-separated):")
    print("Example: FastAPI, Vue.js, Redis, Docker")
    user_input = input("> ").strip()
    
    if not user_input:
        print("No technologies provided. Using default list.")
        technologies = ["FastAPI", "Vue.js"]
    else:
        technologies = [tech.strip() for tech in user_input.split(",")]
    
    print(f"\nSelected technologies: {', '.join(technologies)}")
    print("🔄 Will run outline generation and research in parallel")
    
    # Update the shared store and run
    shared = {
        "technologies": technologies,
        "outline": None,
        "research_results": None,
        "final_document": None
    }
    
    try:
        start_time = time.time()
        await run_parallel_flow(shared)
        execution_time = time.time() - start_time
        
        # Save document
        if shared.get("final_document"):
            filename = f"interactive_parallel_{'_'.join(tech.lower().replace(' ', '_') for tech in technologies[:3])}.md"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(shared["final_document"])
            print(f"\n💾 Document saved to: {filename}")
            print(f"⏱️  Parallel execution time: {execution_time:.1f} seconds")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    # Check if user wants interactive mode
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        asyncio.run(interactive_main())
    else:
        asyncio.run(main())
