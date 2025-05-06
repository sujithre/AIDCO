"""
agents/address_agents.py - Define Semantic Kernel agents for address verification

This module creates two specialized agents for the address verification workflow:
1. RETRIEVER: Performs telsearch API lookups to verify addresses
2. REPORT_AGENT: Collects and reports verification results in structured format
"""

from typing import Tuple

from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.functions.kernel_arguments import KernelArguments
from semantic_kernel.connectors.ai.prompt_execution_settings import PromptExecutionSettings
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel import Kernel

# Define agent names as constants
RETRIEVER = "Retriever_Agent" 
REPORT_AGENT = "Report_Agent"

def create_address_agents(kernel: Kernel) -> Tuple[ChatCompletionAgent, ChatCompletionAgent]:
    """
    Create and return the two specialized agents for address verification workflow
    
    Args:
        kernel: The Semantic Kernel instance for the agents to use
        
    Returns:
        Tuple of (retriever_agent, report_agent)
    """
    # Define standard arguments with function calling enabled
    agent_args = KernelArguments(
        settings=PromptExecutionSettings(
            function_choice_behavior=FunctionChoiceBehavior.Auto(),
            extension_data={}
        )
    )
    
    # Create retriever agent for address lookups
    retriever_agent = ChatCompletionAgent(
        kernel=kernel,
        service=kernel.get_service(),
        name=RETRIEVER,
        plugins=["telsearch"],
        arguments=agent_args,
        instructions="""
Address verifier via tel.search.ch API:
1. Convert names into "FirstName LastName" format
2. Use the API: telsearch.search_person(name="FirstName LastName", location="municipality")
3. Format the result: "[FirstName] [LastName]: [Street] [No], [ZIP] [City]" or "NOT FOUND"
Perform an API call for EACH name.
"""
    )
    
    # Create report agent for collecting and processing results
    report_agent = ChatCompletionAgent(
        kernel=kernel,
        service=kernel.get_service(),
        name=REPORT_AGENT,
        plugins=["report"],
        arguments=agent_args,
        instructions="""
Collect and save address verification results:
1. Monitor whether all people have been verified
2. Output "COMPLETE" when all have been verified
3. Save data in a structured format with report.save_people_data(people_data)
   - people_data should be a JSON array with all people:
   - Format: [
       {"firstname": "Hans", "lastname": "Müller", "address": "Bahnhofstrasse 10", "city": "8000 Zurich", "type": "requested"},
       {"firstname": "Max", "lastname": "Mustermann", "address": "Main Street 1", "city": "8000 Zurich", "type": "requestor"}
     ]
4. Call report.mark_complete() when all people have been processed
"""
    )
    
    return (retriever_agent, report_agent)