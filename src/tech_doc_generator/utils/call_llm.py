"""
OpenAI LLM wrapper utility function.
"""
import logging
import os
from typing import Optional

from openai import OpenAI

from ..constants import DEFAULT_LLM_MODEL, DEFAULT_MAX_TOKENS, DEFAULT_TEMPERATURE

# Module exports
__all__ = ["call_llm"]

# Set up logger for this module
logger = logging.getLogger(__name__)


def call_llm(
    prompt: str, 
    model: str = DEFAULT_LLM_MODEL, 
    max_tokens: int = DEFAULT_MAX_TOKENS
) -> str:
    """
    Call OpenAI LLM with the given prompt.
    
    Args:
        prompt: The prompt to send to the LLM
        model: The model to use (default: gpt-4.1-nano)
        max_tokens: Maximum tokens in response
        
    Returns:
        The LLM response content
        
    Raises:
        Exception: If the API call fails
    """
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    logger.debug(f"Calling LLM with model: {model}, max_tokens: {max_tokens}")
    logger.debug(f"Prompt length: {len(prompt)} characters")
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=DEFAULT_TEMPERATURE
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
