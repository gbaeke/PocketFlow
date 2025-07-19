"""
OpenAI LLM wrapper utility function.
"""
import os
from openai import OpenAI


def call_llm(prompt, model="gpt-4.1", max_tokens=2000):
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
    
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=0.7
    )
    
    return response.choices[0].message.content


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
