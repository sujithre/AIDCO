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
Adressverifizierer via tel.search.ch API:
1. Namen in "Vorname Nachname" Format konvertieren
2. API nutzen: telsearch.search_person(name="Vorname Nachname", location="gemeinde")
3. Ergebnis formatieren: "[Vorname] [Nachname]: [Straße] [Nr], [PLZ] [Ort]" oder "NICHT GEFUNDEN"
Für JEDEN Namen einen API-Aufruf durchführen.
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
Sammle und speichere Adressverifizierungsergebnisse:
1. Überwache, ob alle Personen verifiziert wurden
2. "COMPLETE" ausgeben, wenn alle überprüft wurden
3. Speichere Daten strukturiert mit report.save_people_data(people_data)
   - people_data sollte ein JSON-Array mit allen Personen sein: 
   - Format: [
       {"firstname": "Hans", "lastname": "Müller", "address": "Bahnhofstrasse 10", "city": "8000 Zürich", "type": "requested"},
       {"firstname": "Max", "lastname": "Mustermann", "address": "Hauptstrasse 1", "city": "8000 Zürich", "type": "requestor"}
     ]
4. Rufe report.mark_complete() auf, wenn alle Personen verarbeitet wurden
"""
    )
    
    return (retriever_agent, report_agent)