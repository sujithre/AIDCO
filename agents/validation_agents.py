"""
agents/validation_agents.py - Define Semantic Kernel agents for document validation

This module creates two specialized agents for the validation workflow:
1. VALIDATOR: Checks individual compliance items
2. COMPLIANCE_REPORTER: Collects and reports validation results
"""

from typing import Tuple

from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.functions.kernel_arguments import KernelArguments
from semantic_kernel.connectors.ai.prompt_execution_settings import PromptExecutionSettings
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel import Kernel

# Define agent names as constants
VALIDATOR = "Validator_Agent"
COMPLIANCE_REPORTER = "ComplianceReporter_Agent"

def create_validation_agents(kernel: Kernel) -> Tuple[ChatCompletionAgent, ChatCompletionAgent]:
    """
    Create and return the two specialized agents for document validation workflow
    
    Args:
        kernel: The Semantic Kernel instance for the agents to use
        
    Returns:
        Tuple of (validator_agent, reporter_agent)
    """
    # Define standard arguments with function calling enabled
    agent_args = KernelArguments(
        settings=PromptExecutionSettings(
            function_choice_behavior=FunctionChoiceBehavior.Auto(),
            extension_data={}
        )
    )
    
    # Create validator agent for checking compliance items
    validator_agent = ChatCompletionAgent(
        kernel=kernel,
        service=kernel.get_service(),
        name=VALIDATOR,
        plugins=["compliance"],
        arguments=agent_args,
        instructions="""
You are a validator agent for official documents. Your task is to carefully check each individual validation item.

For each validation item:
1. Check precisely whether the requirement is met.
2. Create a result package:
   ```json
   {
     "section": "Name of the section (e.g., 'Legal Basis')",
     "item": "The validation item as text",
     "status": "passed" or "failed",
     "details": "Reason for failure or important note"
   }
   ```
3. Convert the JSON to a string using JSON.stringify().
4. Save the result:
   compliance.save_validation_result('{"section": "...", "item": "...", "status": "...", "details": "..."}')
5. Output "NEXT" after checking one item.

IMPORTANT:
- Always check ONLY ONE item and wait for the reporter.
- Be precise in validation and reasoning.
- Status MUST be either "passed" or "failed."
- The JSON formatting must be exact.

Example of a call:
compliance.save_validation_result('{"section": "Legal Basis", "item": "§ 3 para. 3 RRA correctly specified", "status": "passed", "details": "The legal basis is complete and correctly cited"}')
"""
    )
    
    # Create reporter agent for collecting and summarizing results
    reporter_agent = ChatCompletionAgent(
        kernel=kernel,
        service=kernel.get_service(),
        name=COMPLIANCE_REPORTER,
        plugins=["compliance"],
        arguments=agent_args,
        instructions="""
You are a reporter agent for validation results. Your tasks:

1. Monitor the validation progress:
   - After each "NEXT" from the validator, check if the current section is complete.
   - Confirm the completion of a section.
   - Signal the next section to be validated.

2. Track these sections:
   - Legal Basis
   - Correct Details for List Inquiry
   - Declaration of Commitment - General Obligations
   - Legal Remedies

3. After each section:
   - Provide a brief summary.
   - Signal the next section for the validator.

4. When all items have been validated:
   - Call compliance.mark_validation_complete().
   - Output "COMPLETE."
   - Summarize the results.

EXAMPLE SUMMARY:
"Section 'Legal Basis' complete:
✅ 2 items passed
❌ 1 item failed: § 3 RRA not correctly cited

Next section: 'Correct Details for List Inquiry'"
"""
    )
    
    return (validator_agent, reporter_agent)