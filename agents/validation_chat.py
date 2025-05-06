"""
agents/validation_chat.py - Configuration for the two-agent chat system for document validation

This module sets up a group chat with two specialized agents:
1. Validator agent: Checks individual compliance items
2. Reporter agent: Collects and reports validation results
"""

from semantic_kernel.agents import AgentGroupChat
from semantic_kernel.agents.strategies import KernelFunctionSelectionStrategy
from semantic_kernel.functions import KernelFunctionFromPrompt
from semantic_kernel import Kernel

from agents.validation_agents import VALIDATOR, COMPLIANCE_REPORTER, create_validation_agents

def setup_validation_chat(kernel: Kernel) -> AgentGroupChat:
    """
    Configure and return the agent group chat for document validation workflow
    
    Args:
        kernel: The Semantic Kernel instance to use
        
    Returns:
        Configured AgentGroupChat instance ready for document validation
    """
    # Create the specialized agents
    validator_agent, reporter_agent = create_validation_agents(kernel)
    
    # Configure agent selection strategy with a clear prompt
    selection_function = KernelFunctionFromPrompt(
        function_name="validation_agent_selection",
        prompt=f"""
{{{{$history}}}}

Based on the chat history above, select the next appropriate agent.
Return ONLY ONE of these names (no other text):
{VALIDATOR}
{COMPLIANCE_REPORTER}

The Validator Agent ({VALIDATOR}):
- Checks each individual item according to a strict schema
- Converts results into JSON strings
- Saves each item with compliance.save_validation_result()
- Signals "NEXT" after each checked item

The ComplianceReporter Agent ({COMPLIANCE_REPORTER}):
- Monitors the validation progress
- Summarizes the results for each section
- Signals when the validation is complete
- Creates a final report with all results

Selection criteria:
1. Choose {VALIDATOR} if:
   - A new validation item needs to be checked
   - The last item was just completed ("NEXT")
   - No section has been fully validated yet

2. Choose {COMPLIANCE_REPORTER} if:
   - A complete section has been validated
   - The validator has output "NEXT"
   - An interim summary is needed
   - All items have been validated
"""
    )

    # Create the group chat with our agent selection strategy
    chat = AgentGroupChat(
        agents=[validator_agent, reporter_agent],
        selection_strategy=KernelFunctionSelectionStrategy(
            initial_agent=validator_agent,
            function=selection_function,
            kernel=kernel,
            history_variable_name="history",
            agent_variable_name="agents",
            result_parser=lambda x: str(x) if x else VALIDATOR
        )
    )
    
    return chat