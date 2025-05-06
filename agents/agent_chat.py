"""
agents/agent_chat.py - Configuration for the two-agent chat system for address verification

This module sets up a group chat with two specialized agents:
1. Retriever agent: Calls telsearch API to look up addresses
2. Report agent: Collects and structures verification results
"""

from semantic_kernel.agents import AgentGroupChat
from semantic_kernel.agents.strategies import KernelFunctionSelectionStrategy
from semantic_kernel.functions import KernelFunctionFromPrompt
from semantic_kernel import Kernel

from agents.address_agents import RETRIEVER, REPORT_AGENT, create_address_agents

def setup_agent_chat(kernel: Kernel) -> AgentGroupChat:
    """
    Configure and return the agent group chat for address verification workflow
    
    Args:
        kernel: The Semantic Kernel instance to use
        
    Returns:
        Configured AgentGroupChat instance ready for address verification
    """
    # Create the specialized agents
    retriever_agent, report_agent = create_address_agents(kernel)
    
    # Configure agent selection strategy with a clear prompt
    selection_function = KernelFunctionFromPrompt(
        function_name="agent_selection",
        prompt=f"""
{{{{$history}}}}

Based on the chat history above, select the next appropriate agent.
Return ONLY ONE of these names (no other text):
{RETRIEVER}
{REPORT_AGENT}

The Retriever Agent ({RETRIEVER}) is responsible for:
- Performing telsearch API queries for each person using telsearch.search_person
- Verifying if people reside at the specified address
- Extracting complete address data from the API responses

The Report Agent ({REPORT_AGENT}) is responsible for:
- Checking if all names have already been verified
- Signaling when the process is complete ("COMPLETE")
- Summarizing the results at the end
- Structuring and saving the results with report.save_people_data()

Selection criteria:
- Choose {RETRIEVER} if there are still names to be verified
- Choose {REPORT_AGENT} if at least one address verification has been performed and we need to check if all names have been processed
- Also choose {REPORT_AGENT} if the Retriever Agent has already been working for some time
- Choose {REPORT_AGENT} if the Retriever Agent has not been selected for a while
- Please call {REPORT_AGENT} after the {RETRIEVER} has been called  to summarize the results
"""
    )

    # Create the group chat with our agent selection strategy
    chat = AgentGroupChat(
        agents=[retriever_agent, report_agent],
        selection_strategy=KernelFunctionSelectionStrategy(
            initial_agent=retriever_agent,
            function=selection_function,
            kernel=kernel,
            history_variable_name="history",
            agent_variable_name="agents",
            result_parser=lambda x: str(x) if x else RETRIEVER
        )
    )
    
    return chat