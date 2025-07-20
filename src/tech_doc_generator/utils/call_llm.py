"""
OpenAI LLM wrapper utility function.
"""
import logging
import os
from typing import Optional, Dict, Any, Union

from openai import OpenAI

from ..constants import DEFAULT_LLM_MODEL, DEFAULT_MAX_TOKENS, DEFAULT_TEMPERATURE

# Module exports
__all__ = ["call_llm"]

# Set up logger for this module
logger = logging.getLogger(__name__)


def call_llm(
    prompt: str, 
    model: str = DEFAULT_LLM_MODEL, 
    max_tokens: int = DEFAULT_MAX_TOKENS,
    json_mode: bool = False
) -> Union[str, Dict[str, Any]]:
    """
    Call OpenAI LLM with the given prompt.
    
    Args:
        prompt: The prompt to send to the LLM
        model: The model to use (default: gpt-4.1-nano)
        max_tokens: Maximum tokens in response
        json_mode: If True, force JSON response format and return parsed JSON
        
    Returns:
        The LLM response content as string, or parsed JSON dict if json_mode=True
        
    Raises:
        Exception: If the API call fails
        ValueError: If json_mode=True but response is not valid JSON
    """
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    logger.debug(f"Calling LLM with model: {model}, max_tokens: {max_tokens}, json_mode: {json_mode}")
    logger.debug(f"Prompt length: {len(prompt)} characters")
    
    try:
        # Prepare the request parameters
        request_params = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": DEFAULT_TEMPERATURE
        }
        
        # Add JSON mode if requested
        if json_mode:
            request_params["response_format"] = {"type": "json_object"}
        
        response = client.chat.completions.create(**request_params)
        
        result = response.choices[0].message.content
        logger.debug(f"LLM response length: {len(result)} characters")
        
        # If JSON mode is enabled, parse and return the JSON
        if json_mode:
            try:
                import json
                parsed_result = json.loads(result)
                logger.debug("Successfully parsed JSON response")
                return parsed_result
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                logger.error(f"Raw response: {result}")
                raise ValueError(f"LLM returned invalid JSON in json_mode: {e}") from e
        
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
        
        # Test JSON mode
        json_test_prompt = """
        Analyze the Python programming language and return information in JSON format.
        
        Return a JSON object with the following structure:
        {
            "name": "Python",
            "type": "programming language",
            "features": ["feature1", "feature2", "feature3"],
            "popularity": "high"
        }
        """
        
        json_result = call_llm(json_test_prompt, json_mode=True)
        print("\nJSON mode test successful!")
        print(f"JSON Response: {json_result}")
        print(f"Type: {type(json_result)}")
        
    except Exception as e:
        print(f"Test failed: {e}")
        print("Make sure OPENAI_API_KEY environment variable is set")
