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

Basierend auf dem Chat-Verlauf oben, wähle den nächsten geeigneten Agenten aus.
Gib NUR EINEN dieser Namen zurück (kein anderer Text):
{RETRIEVER}
{REPORT_AGENT}

Der Retriever Agent ({RETRIEVER}) ist verantwortlich für:
- Durchführung der telsearch API-Abfragen für jede Person mit telsearch.search_person
- Überprüfung ob Personen an der angegebenen Adresse wohnen
- Extraktion der vollständigen Adressdaten aus den API-Antworten

Der Report Agent ({REPORT_AGENT}) ist verantwortlich für:
- Überprüfen ob alle Namen bereits überprüft wurden
- Signalisieren wenn der Prozess abgeschlossen ist ("COMPLETE")
- Zusammenfassung der Ergebnisse am Ende
- Strukturierte Speicherung der Ergebnisse mit report.save_people_data()

Auswahlkriterien:
- Wähle den {RETRIEVER}, wenn noch Namen überprüft werden müssen
- Wähle den {REPORT_AGENT}, wenn mindestens eine Adressprüfung durchgeführt wurde und wir überprüfen sollten, ob alle Namen abgearbeitet sind
- Wähle {REPORT_AGENT} auch, wenn der Retriever Agent bereits einige Zeit gearbeitet hat
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