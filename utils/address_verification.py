"""
utils/address_verification.py - Address verification workflow using multi-agent system

This module manages the process of verifying addresses using a two-agent approach:
- A retriever agent that queries the tel.search.ch API
- A report agent that collects and validates the results
"""

from typing import Dict, Tuple, List, Optional, Any
from semantic_kernel.contents import ChatMessageContent
from semantic_kernel.contents.utils.author_role import AuthorRole
from agents.address_agents import RETRIEVER, REPORT_AGENT

MAX_MESSAGE_COUNT = 20
COMPLETION_MARKER = "COMPLETE"

def _create_verification_prompt(
    requestor_firstname: str, 
    requestor_lastname: str, 
    gemeinde: str, 
    people_text: str
) -> str:
    """
    Create the initial prompt for address verification.
    
    Args:
        requestor_firstname: First name of the requestor
        requestor_lastname: Last name of the requestor
        gemeinde: Municipality name for address lookup
        people_text: List of people to verify, one person per line
        
    Returns:
        A formatted prompt string for the agent system
    """
    requestor_name = f"{requestor_firstname} {requestor_lastname}"
    
    return f"""
Ich muss Adressen für die folgenden Personen in {gemeinde} überprüfen (type = 'requested'):
{people_text}

Zusätzlich muss ich die Adresse des Requestors finden (type = 'requestor'):
{requestor_name} {requestor_lastname} 

Retriever Agent: Überprüfe diese Personen mit telsearch.search_person(name="Vorname Nachname", location="{gemeinde}")
Report Agent: Prüfe ob alle Namen überprüft wurden. Wenn ja, signalisiere "COMPLETE" und speichere mit report.save_people_data().

Hier ein Beispiel:
{{
  "firstname": "Steven", "lastname": "Hawking",
  "address": "Hauptstrasse 1", "city": "8000 Zurich", "type": "requestor"
}}

Die anderen Personen sind vom Typ "requested".
"""
        
async def verify_addresses(
    agent_chat: Any, 
    report_plugin: Any, 
    requestor_firstname: str, 
    requestor_lastname: str, 
    gemeinde: str, 
    people_text: str
) -> Tuple[Dict, str, List]:
    """
    Use two-agent system to verify addresses with telsearch.
    
    Args:
        agent_chat: The agent chat system that will handle the conversation
        report_plugin: Plugin for storing verified address data
        requestor_firstname: First name of the requestor
        requestor_lastname: Last name of the requestor
        gemeinde: Municipality name for address lookup
        people_text: List of people to verify, one person per line
        
    Returns:
        Tuple containing:
        - Dictionary of verified addresses
        - Summary string of verification results
        - List of agent messages for debugging/display
        
    Raises:
        ValueError: If input data is invalid
        RuntimeError: If agent system fails to complete verification
    """
    report_plugin.reset()
    
    if not gemeinde or not gemeinde.strip():
        raise ValueError("Municipality (gemeinde) cannot be empty")
    
    if not people_text or not people_text.strip():
        raise ValueError("People list cannot be empty")
    
    initial_prompt = _create_verification_prompt(
        requestor_firstname, requestor_lastname, gemeinde, people_text
    )
    
    await agent_chat.add_chat_message(ChatMessageContent(
        role=AuthorRole.USER, 
        content=initial_prompt
    ))

    agent_messages = []
    verification_complete = False
    
    try:
        message_count = 0
        async for response in agent_chat.invoke():
            message_count += 1
            if message_count > MAX_MESSAGE_COUNT:
                raise RuntimeError(f"Verification exceeded {MAX_MESSAGE_COUNT} messages without completion")
                
            if response and response.name:
                agent_messages.append({
                    "role": "assistant", 
                    "name": response.name, 
                    "content": response.content
                })
                
                if response.name == REPORT_AGENT and COMPLETION_MARKER in response.content:
                    verification_complete = True
                    break
    
    except Exception as e:
        agent_messages.append({
            "role": "system", 
            "content": f"Fehler: {str(e)}"
        })
        raise RuntimeError(f"Address verification failed: {str(e)}") from e
    
    if not verification_complete:
        raise RuntimeError("Address verification did not complete successfully")
    
    addresses_dict = report_plugin.get_addresses_dict()
    
    summary_lines = []
    for name, addr in addresses_dict.items():
        status = addr or "NICHT GEFUNDEN"
        summary_lines.append(f"- {name}: {status}")
    
    summary = "\n".join(summary_lines) if summary_lines else "Keine Adressen gefunden."
    
    return addresses_dict, summary, agent_messages