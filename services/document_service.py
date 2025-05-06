"""
services/document_service.py - Service for document generation and validation

This service handles document generation and validation using a multi-agent
system for compliance checking.
"""

import os
from typing import Optional, Dict, List, Tuple
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.prompt_execution_settings import PromptExecutionSettings
from semantic_kernel.contents import ChatMessageContent
from semantic_kernel.contents.utils.author_role import AuthorRole

from models.core import DocumentContext, MAX_MESSAGE_COUNT, COMPLETION_MARKER
from plugins.compliance_plugin import CompliancePlugin
from agents.validation_chat import setup_validation_chat

class DocumentService:
    """Service for generating and validating documents."""
    
    def __init__(self, kernel: Kernel):
        """
        Initialize the document service.
        
        Args:
            kernel: Configured Semantic Kernel instance
            
        Raises:
            RuntimeError: If required templates cannot be loaded
        """
        self.kernel = kernel
        self.verfuegung_template = self._load_template("templates/verfuegung_template.md")
        self.validation_questions = self._load_template("templates/validation_questions.md")
        
        # Initialize and register compliance plugin
        self.compliance_plugin = CompliancePlugin()
        self.kernel.add_plugin(self.compliance_plugin, plugin_name="compliance")
        
        # Setup validation chat system
        self.validation_chat = setup_validation_chat(self.kernel)
    
    def _load_template(self, path: str) -> str:
        """Load a template file and return its contents."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            raise RuntimeError(f"Failed to load template {path}: {str(e)}")
    
    async def generate_document(self, context: DocumentContext) -> str:
        """
        Generate a document based on the provided context.
        
        Args:
            context: Document context containing all required information
            
        Returns:
            Generated document text in markdown format
        """
        print(context)
        # Create prompt for document generation
        prompt = f"""
You are an expert in creating official documents following strict formats.
Create a real document (not a template!) based on the template provided below.

INFORMATION TO INCLUDE:
1. The applicant: {context.requestor.full_name}
   Address: {context.requestor.full_address or '[ADDRESS NOT AVAILABLE]'}
2. List of requested individuals:
"""
        
        # Add each requested person
        for person in context.requested_people:
            addr = person.full_address or "NOT FOUND"
            prompt += f"   - {person.full_name}: {addr}\n"
            
        prompt += f"""
3. Purpose of the request: {context.zweck}
4. Municipality: {context.gemeinde}

INSTRUCTIONS:
1. Use the template and insert all data correctly.
2. Format multiple individuals as a numbered list.
3. Ensure correct legal phrasing.
4. Return only the completed document text in markdown format.

TEMPLATE:
{self.verfuegung_template}
"""

        # Generate document using LLM
        result = await self.kernel.invoke_prompt(
            prompt=prompt,
            settings=PromptExecutionSettings(
                temperature=0.7,
                top_p=1,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )
        )
        
        return str(result).strip()
    
    async def validate_document(self, document_text: str) -> Tuple[str, List[Dict], List[Dict]]:
        """
        Validate a document against compliance rules using a multi-agent system.
        
        Args:
            document_text: The document text to validate
            
        Returns:
            Tuple containing:
            - Markdown formatted validation report
            - List of validation results
            - List of agent messages for debugging
            
        Raises:
            RuntimeError: If validation process fails or times out
        """
        # Reset compliance plugin state
        self.compliance_plugin.reset()
        
        # Create initial prompt for validation
        prompt = f"""
Perform a detailed validation of the following document.
Carefully check each item in the checklist.

DOCUMENT:
{document_text}

VALIDATION CHECKLIST:
{self.validation_questions}

Validator Agent: Check each item individually and save the result with compliance.save_validation_result()
ComplianceReporter: Monitor progress and mark when all items have been checked.
"""
        
        # Start the validation chat
        await self.validation_chat.add_chat_message(ChatMessageContent(
            role=AuthorRole.USER,
            content=prompt
        ))
        
        # Collect agent messages for UI display
        agent_messages = []
        validation_complete = False
        
        try:
            message_count = 0
            async for response in self.validation_chat.invoke():
                message_count += 1
                if message_count > MAX_MESSAGE_COUNT:
                    raise RuntimeError(
                        f"Validation exceeded {MAX_MESSAGE_COUNT} messages without completion"
                    )
                    
                if response and response.name:
                    agent_messages.append({
                        "role": "assistant",
                        "name": response.name,
                        "content": response.content
                    })
                    
                    if response.name == "ComplianceReporter_Agent" and COMPLETION_MARKER in response.content:
                        validation_complete = True
                        break
        
        except Exception as e:
            agent_messages.append({
                "role": "system",
                "content": f"Error: {str(e)}"
            })
            raise RuntimeError(f"Validation failed: {str(e)}") from e
            
        if not validation_complete:
            raise RuntimeError("Validation did not complete successfully")
            
        # Get validation results and format report
        validation_results = self.compliance_plugin.get_validation_results()
        report = self.compliance_plugin.format_markdown_report()
        
        return report, validation_results, agent_messages