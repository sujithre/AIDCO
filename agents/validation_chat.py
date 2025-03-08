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

Basierend auf dem Chat-Verlauf oben, wähle den nächsten geeigneten Agenten aus.
Gib NUR EINEN dieser Namen zurück (kein anderer Text):
{VALIDATOR}
{COMPLIANCE_REPORTER}

Der Validator Agent ({VALIDATOR}):
- Prüft jeden einzelnen Punkt nach einem strikten Schema
- Konvertiert Ergebnisse in JSON-Strings
- Speichert jeden Punkt mit compliance.save_validation_result()
- Signalisiert "NEXT" nach jedem geprüften Punkt

Der ComplianceReporter Agent ({COMPLIANCE_REPORTER}):
- Überwacht den Validierungsfortschritt
- Fasst die Ergebnisse pro Abschnitt zusammen
- Signalisiert wenn die Validierung abgeschlossen ist
- Erstellt einen finalen Bericht mit allen Ergebnissen

Auswahlkriterien:
1. Wähle den {VALIDATOR} wenn:
   - Ein neuer Validierungspunkt geprüft werden muss
   - Der letzte Punkt gerade abgeschlossen wurde ("NEXT")
   - Kein Abschnitt vollständig validiert wurde

2. Wähle den {COMPLIANCE_REPORTER} wenn:
   - Ein kompletter Abschnitt geprüft wurde
   - Der Validator "NEXT" ausgegeben hat
   - Wir eine Zwischenzusammenfassung benötigen
   - Alle Punkte geprüft wurden
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