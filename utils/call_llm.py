"""
OpenAI LLM wrapper utility function.
"""
import os
import logging
from openai import OpenAI

# Set up logger for this module
logger = logging.getLogger(__name__)


def call_llm(prompt, model="gpt-4.1-nano", max_tokens=2000):
    """
    Call OpenAI LLM with the given prompt.
    
    Args:
        prompt (str): The prompt to send to the LLM
        model (str): The model to use (default: gpt-4o)
        max_tokens (int): Maximum tokens in response
        
    Returns:
        str: The LLM response content
    """
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    logger.debug(f"Calling LLM with model: {model}, max_tokens: {max_tokens}")
    logger.debug(f"Prompt length: {len(prompt)} characters")
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.7
        )
        
        result = response.choices[0].message.content
        logger.debug(f"LLM response length: {len(result)} characters")
        return result
        
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        raise


if __name__ == "__main__":
    # Test the function
    test_prompt = "What is Python programming language?"
    try:
        result = call_llm(test_prompt)
        print("Test successful!")
        print(f"Prompt: {test_prompt}")
        print(f"Response: {result}")
    except Exception as e:
        print(f"Test failed: {e}")
        print("Make sure OPENAI_API_KEY environment variable is set")
