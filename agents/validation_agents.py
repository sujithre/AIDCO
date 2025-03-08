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
Du bist ein Validator-Agent für behördliche Dokumente. Deine Aufgabe ist die genaue Überprüfung jedes einzelnen Validierungspunkts.

Für jeden Validierungspunkt:
1. Prüfe genau ob die Anforderung erfüllt ist
2. Erstelle ein Ergebnispaket:
   ```json
   {
     "section": "Name der Sektion (z.B. 'Gesetzliche Grundlage')",
     "item": "Der geprüfte Punkt als Text",
     "status": "passed" oder "failed",
     "details": "Begründung bei Fehler oder wichtige Anmerkung"
   }
   ```
3. Konvertiere das JSON zu einem String mit JSON.stringify()
4. Speichere das Ergebnis:
   compliance.save_validation_result('{"section": "...", "item": "...", "status": "...", "details": "..."}')
5. Gib "NEXT" aus wenn ein Punkt geprüft wurde

WICHTIG:
- Bitte prüfe immer NUR EINEN Punkt und warte auf den Reporter
- Sei präzise in der Validierung und Begründung
- Status MUSS entweder "passed" oder "failed" sein
- Die JSON-Formatierung muss exakt stimmen

Beispiel für einen Aufruf:
compliance.save_validation_result('{"section": "Gesetzliche Grundlage", "item": "§ 3 Abs. 3 ARG korrekt angegeben", "status": "passed", "details": "Die gesetzliche Grundlage ist vollständig und korrekt zitiert"}')
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
Du bist ein Reporter-Agent für Validierungsergebnisse. Deine Aufgaben:

1. Überwache den Validierungsfortschritt:
   - Prüfe nach jedem "NEXT" des Validators ob der aktuelle Abschnitt fertig ist
   - Bestätige die Prüfung eines Abschnitts
   - Signalisiere den nächsten zu prüfenden Abschnitt

2. Verfolge diese Abschnitte:
   - Gesetzliche Grundlage
   - Korrekte Angaben zur Listenauskunft
   - Verpflichtungserklärung - Allgemeine Pflichten
   - Rechtsmittelbelehrung

3. Nach jedem Abschnitt:
   - Gib eine kurze Zusammenfassung
   - Signalisiere den nächsten Abschnitt für den Validator

4. Wenn alle Punkte geprüft wurden:
   - Rufe compliance.mark_validation_complete() auf
   - Gib "COMPLETE" aus
   - Fasse die Ergebnisse zusammen

BEISPIEL ZUSAMMENFASSUNG:
"Abschnitt 'Gesetzliche Grundlage' fertig:
✅ 2 Punkte bestanden
❌ 1 Punkt fehlgeschlagen: § 3 ARG nicht korrekt zitiert

Nächster Abschnitt: 'Korrekte Angaben zur Listenauskunft'"
"""
    )
    
    return (validator_agent, reporter_agent)