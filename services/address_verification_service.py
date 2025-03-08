"""
services/address_verification_service.py - Service for address verification using agent system

This service manages the process of verifying addresses using a multi-agent system
that interfaces with the tel.search.ch API.
"""

from typing import Dict, List, Tuple
from semantic_kernel import Kernel
from semantic_kernel.agents import AgentGroupChat
from semantic_kernel.contents import ChatMessageContent
from semantic_kernel.contents.utils.author_role import AuthorRole

from models.core import Person, DocumentContext, MAX_MESSAGE_COUNT, COMPLETION_MARKER
from plugins.report_plugin import ReportPlugin
from plugins.telsearch_plugin import TelsearchPlugin
from utils.semantic_kernel_setup import create_kernel
from agents.agent_chat import setup_agent_chat

class AddressVerificationService:
    """Service for verifying addresses using multi-agent system."""
    
    def __init__(self):
        """Initialize service with a new kernel and agent chat."""
        self.kernel = create_kernel()
        
        # Initialize and register plugins
        self.report_plugin = ReportPlugin()
        self.telsearch_plugin = TelsearchPlugin()
        
        # Register plugins with the kernel
        self.kernel.add_plugin(self.report_plugin, plugin_name="report")
        self.kernel.add_plugin(self.telsearch_plugin, plugin_name="telsearch")
        
        # Setup agent chat after plugins are registered
        self.agent_chat = setup_agent_chat(self.kernel)
    
    def reset(self):
        """Reset the service state."""
        self.report_plugin.reset()
        
    async def verify_addresses(self, context: DocumentContext) -> Tuple[Dict[str, str], str, List[dict]]:
        """
        Verify addresses for all people in the context.
        
        Args:
            context: Document context with people to verify
            
        Returns:
            Tuple containing:
            - Dictionary mapping names to verified addresses
            - Summary of verification results
            - List of agent messages for debugging
            
        Raises:
            ValueError: If context is invalid
            RuntimeError: If verification process fails
        """
        self.reset()
        
        if not context.gemeinde or not context.gemeinde.strip():
            raise ValueError("Municipality (gemeinde) cannot be empty")
        
        # Create the verification prompt
        prompt = self._create_verification_prompt(context)
        
        # Start the agent chat
        await self.agent_chat.add_chat_message(ChatMessageContent(
            role=AuthorRole.USER,
            content=prompt
        ))
        
        agent_messages = []
        verification_complete = False
        
        try:
            message_count = 0
            async for response in self.agent_chat.invoke():
                message_count += 1
                if message_count > MAX_MESSAGE_COUNT:
                    raise RuntimeError(
                        f"Verification exceeded {MAX_MESSAGE_COUNT} messages without completion"
                    )
                
                if response and response.name:
                    agent_messages.append({
                        "role": "assistant",
                        "name": response.name,
                        "content": response.content
                    })
                    
                    if response.name == "Report_Agent" and COMPLETION_MARKER in response.content:
                        verification_complete = True
                        break
        
        except Exception as e:
            agent_messages.append({
                "role": "system",
                "content": f"Error: {str(e)}"
            })
            raise RuntimeError(f"Address verification failed: {str(e)}") from e
        
        if not verification_complete:
            raise RuntimeError("Address verification did not complete successfully")
        
        # Get results from report plugin
        addresses_dict = self.report_plugin.get_addresses_dict()
        
        # Create summary
        summary_lines = []
        for name, addr in addresses_dict.items():
            status = addr or "NICHT GEFUNDEN"
            summary_lines.append(f"- {name}: {status}")
        
        summary = "\n".join(summary_lines) if summary_lines else "Keine Adressen gefunden."
        
        return addresses_dict, summary, agent_messages
    
    def _create_verification_prompt(self, context: DocumentContext) -> str:
        """Create the initial prompt for address verification."""
        # Add requestor information
        prompt = f"""
Ich muss Adressen für die folgenden Personen in {context.gemeinde} überprüfen (type = 'requested'):
"""
        
        # Add each requested person
        for person in context.requested_people:
            prompt += f"{person.firstname} {person.lastname}\n"
            
        # Add requestor verification request
        prompt += f"""
Zusätzlich muss ich die Adresse des Requestors finden (type = 'requestor'):
{context.requestor.firstname} {context.requestor.lastname}

Retriever Agent: Überprüfe diese Personen mit telsearch.search_person(name="Vorname Nachname", location="{context.gemeinde}")
Report Agent: Prüfe ob alle Namen überprüft wurden. Wenn ja, signalisiere "COMPLETE" und speichere mit report.save_people_data().

Hier ein Beispiel für die JSON-Struktur:
{{
  "firstname": "Hans", "lastname": "Müller",
  "address": "Bahnhofstrasse 10", "city": "8000 Zürich", "type": "requested"
}}
"""
        return prompt