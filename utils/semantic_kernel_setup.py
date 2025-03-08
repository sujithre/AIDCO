"""
utils/semantic_kernel_setup.py - Sets up and configures Semantic Kernel with Azure OpenAI

This module provides functionality to create and configure a Semantic Kernel instance
with Azure OpenAI chat completion capabilities.
"""

import os
from dotenv import load_dotenv
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

def create_kernel() -> Kernel:
    """
    Creates and returns a Semantic Kernel instance configured to use Azure OpenAI chat completion.
    
    Returns:
        Configured Semantic Kernel instance
        
    Raises:
        ValueError: If required environment variables are missing or invalid
    """
    # Load environment variables from .env file
    load_dotenv(override=True)
    
    # Get environment variables and strip any quotation marks
    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT", "")
    if endpoint:
        endpoint = endpoint.strip().strip('"\'')
    
    api_key = os.environ.get("AZURE_OPENAI_KEY", "")
    if api_key:
        api_key = api_key.strip().strip('"\'')
    
    deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "")
    if deployment:
        deployment = deployment.strip().strip('"\'')
    
    # Check if values are placeholders
    if "<YOUR-RESOURCE-NAME>" in endpoint:
        raise ValueError("AZURE_OPENAI_ENDPOINT contains a placeholder. Please update your .env file.")
    
    if "<Your-Azure-Deployment-Name>" in deployment:
        raise ValueError("AZURE_OPENAI_DEPLOYMENT contains a placeholder. Please update your .env file.")

    if not endpoint or not api_key or not deployment:
        raise ValueError(
            "Missing Azure OpenAI environment variables. "
            "Please set AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_KEY, "
            "and AZURE_OPENAI_DEPLOYMENT in your .env file or environment."
        )
    
    # Remove any trailing slashes from the endpoint
    endpoint = endpoint.rstrip('/')
    
    # Debug output
    print(f"Using Azure OpenAI endpoint: {endpoint}")
    print(f"Using Azure OpenAI deployment: {deployment}")
    
    kernel = Kernel()
    try:
        service = AzureChatCompletion(
            deployment_name=deployment,
            endpoint=endpoint,
            api_key=api_key
        )
        kernel.add_service(service)
        return kernel
    except Exception as e:
        print(f"Error initializing Azure OpenAI service: {str(e)}")
        raise