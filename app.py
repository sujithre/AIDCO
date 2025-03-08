"""
app.py - Main application interface using Gradio

This module provides a web interface for the document generation system,
allowing users to:
1. Input requestor and requested people information
2. Verify addresses using tel.search.ch API
3. Generate and validate legal documents
4. Export documents to Word format
"""

import os
import gradio as gr
import asyncio
from datetime import datetime
from typing import List, Dict, Tuple
from dotenv import load_dotenv

from models.core import Person, PersonType, DocumentContext
from services.address_verification_service import AddressVerificationService
from services.document_service import DocumentService
from services.export_service import ExportService
from utils.semantic_kernel_setup import create_kernel
from plugins.telsearch_plugin import TelsearchPlugin
from plugins.report_plugin import ReportPlugin

AZURE_CSS = """
:root {
    --primary-color: #3b82f6;
    --secondary-color: #4c93d7;
    --background-color: #F8F9FA;
    --text-color: #323130;
    --border-color: #EDEBE9;
    --shadow-color: rgba(0, 0, 0, 0.1);
}

body {
    background-color: var(--background-color);
    color: var(--text-color);
    font-family: 'Segoe UI', sans-serif;
}

h1, h2, h3, h4 {
    color: var(--primary-color);
    font-weight: 600;
}

.gradio-container {
    max-width: 1200px !important;
    margin: 0 auto;
}

.tabs > .tab-nav {
    background-color: white;
    border-bottom: 1px solid var(--border-color);
    box-shadow: 0 2px 4px var(--shadow-color);
}

.tabs > .tab-nav > button {
    font-weight: 600;
    color: var(--text-color);
}

.tabs > .tab-nav > button.selected {
    color: var(--primary-color);
    border-bottom-color: var(--primary-color);
}

.primary-button {
    background-color: var(--primary-color) !important;
    color: white !important;
    border: none !important;
    border-radius: 2px !important;
}

.primary-button:hover {
    background-color: var(--secondary-color) !important;
}

.tab-content {
    padding: 20px;
    background-color: white;
    border-radius: 4px;
    box-shadow: 0 2px 8px var(--shadow-color);
    margin-top: 10px;
}

.validation-results {
    border-left: 4px solid var(--primary-color);
    padding-left: 15px;
}

.header-section {
    background-color: var(--primary-color);
    padding: 20px;
    border-radius: 4px 4px 0 0;
    color: white;
    margin-bottom: 20px;
}

.card {
    background-color: white;
    border-radius: 4px;
    box-shadow: 0 2px 8px var(--shadow-color);
    padding: 20px;
    margin-bottom: 20px;
}
"""

class DocumentGeneratorApp:
    """Main application class for document generation system."""
    
    def __init__(self):
        """Initialize services and load templates."""
        # Initialize services
        self.kernel = create_kernel()
        
        # Initialize and register plugins
        self.telsearch_plugin = TelsearchPlugin()
        self.report_plugin = ReportPlugin()
        self.kernel.add_plugin(self.telsearch_plugin, plugin_name="telsearch")
        self.kernel.add_plugin(self.report_plugin, plugin_name="report")
        
        # Initialize services with configured kernel
        self.address_service = AddressVerificationService()
        self.document_service = DocumentService(self.kernel)
        self.export_service = ExportService()
        
        # Create required directories
        os.makedirs("output", exist_ok=True)
        os.makedirs("templates", exist_ok=True)
        
        # Load environment variables for default values
        load_dotenv()
        self.default_requestor = os.environ.get("ORDER_PERSON", "")
        self.default_person_list = os.environ.get("PERSON_LIST", "")
        
    def create_interface(self) -> gr.Blocks:
        """Create and return the Gradio interface."""
        
        # Parse default values
        default_firstname = ""
        default_lastname = ""
        if self.default_requestor:
            # Parse "Lastname, Firstname" format
            parts = self.default_requestor.split(",")
            if len(parts) == 2:
                default_lastname = parts[0].strip()
                default_firstname = parts[1].strip()
        
        # List of available purposes (Zweck options)
        ZWECK_OPTIONS = [
            "Nachbarschaftliche Kontaktaufnahme",
            "Einmaliger Versand eines Spendenaufrufs",
            "Organisation eines Quartierfests",
            "Bürgerinitiative",
            "Vereinsgründung"
        ]
        
        with gr.Blocks(
            title="Gemeinde Contoso Verpflichtungserklärungsgenerator",
            css=AZURE_CSS,
            theme=gr.themes.Base()
        ) as interface:
            with gr.Blocks(elem_classes=["header-section"]):
                gr.Markdown("""
                # Gemeinde Contoso Verpflichtungserklärungsgenerator
                
                Generiere rechtskonforme Verpflichtungserklärung für Einwohneranfragen.
                """)
            
            # Phase 1: Data Collection
            with gr.Tab("📝 Phase 1: Datenerfassung"):
                with gr.Blocks(elem_classes=["card"]):
                    with gr.Row():
                        with gr.Column():
                            gr.Markdown("### Antragsteller")
                            req_firstname = gr.Textbox(
                                label="Vorname",
                                placeholder="Max",
                                value=default_firstname
                            )
                            req_lastname = gr.Textbox(
                                label="Nachname",
                                placeholder="Mustermann",
                                value=default_lastname
                            )
                        
                        with gr.Column():
                            gr.Markdown("### Anfrage Details")
                            gemeinde = gr.Textbox(
                                label="Gemeinde",
                                value="Zürich",
                                placeholder="z.B. Zürich"
                            )
                            zweck = gr.Dropdown(
                                label="Zweck der Anfrage",
                                choices=ZWECK_OPTIONS,
                                value=ZWECK_OPTIONS[0]
                            )
                            
                with gr.Blocks(elem_classes=["card"]):
                    people_list = gr.TextArea(
                        label="Angefragte Personen (eine pro Zeile)",
                        placeholder="Hans Meier\nAnna Schmidt\nPeter Müller",
                        value=self.default_person_list,
                        lines=5
                    )
                    
                    verify_btn = gr.Button("Adressen Verifizieren", elem_classes=["primary-button"])
                    
                    with gr.Row():
                        verification_output = gr.Markdown(
                            label="Verifikationsergebnisse",
                            value=""
                        )
                        verification_chat = gr.Chatbot(
                            label="Adressverifikation Agenten",
                            height=300
                        )
            
            # Phase 2: Document Generation
            with gr.Tab("📋 Phase 2: Dokument Generierung"):
                with gr.Blocks(elem_classes=["card"]):
                    generate_btn = gr.Button("Dokument Generieren", elem_classes=["primary-button"])
                    document_text = gr.TextArea(
                        label="Generiertes Dokument",
                        lines=20,
                        interactive=True
                    )
            
            # Phase 3: Validation
            with gr.Tab("✅ Phase 3: Validierung"):
                with gr.Blocks(elem_classes=["card"]):
                    validate_btn = gr.Button("Dokument Validieren", elem_classes=["primary-button"])
                    with gr.Row():
                        validation_output = gr.Markdown(
                            label="Validierungsergebnisse",
                            value="",
                            elem_classes=["validation-results"]
                        )
                        validation_chat = gr.Chatbot(
                            label="Validierungs-Agenten",
                            height=300
                        )

            # Phase 4: Export
            with gr.Tab("💾 Phase 4: Export"):
                with gr.Blocks(elem_classes=["card"]):
                    gr.Markdown("""
                    ### Dokument Exportieren
                    
                    Exportiere das Dokument als Word-Datei mit professionellem Layout.
                    """)
                    export_btn = gr.Button("Als DOCX Exportieren", elem_classes=["primary-button"])
                    export_status = gr.Markdown()
            
            # Wire up the interface
            def parse_people_list(text: str) -> List[Person]:
                """Parse the people list text into Person objects.
                Handles both "Firstname Lastname" and "Lastname, Firstname" formats."""
                people = []
                for line in text.strip().split("\n"):
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        # Handle "Lastname, Firstname" format
                        if "," in line:
                            lastname, firstname = [part.strip() for part in line.split(",", 1)]
                        # Handle "Firstname Lastname" format
                        else:
                            parts = line.split()
                            if len(parts) < 2:
                                raise ValueError(f"Name needs at least two parts: {line}")
                            firstname = parts[0]
                            lastname = " ".join(parts[1:])
                        
                        people.append(Person(
                            firstname=firstname,
                            lastname=lastname,
                            type=PersonType.REQUESTED
                        ))
                    except ValueError:
                        raise ValueError(f"Ungültiges Format für Person: {line}")
                return people
            
            async def verify_addresses(
                req_firstname: str,
                req_lastname: str,
                gemeinde: str,
                people_text: str
            ) -> Tuple[str, List[Tuple[str, str]]]:
                """Handle address verification."""
                try:
                    # Create requestor - handle comma format
                    firstname = req_firstname
                    lastname = req_lastname
                    if "," in firstname:  # If someone pasted full name in firstname field
                        lastname, firstname = [part.strip() for part in firstname.split(",", 1)]
                    
                    requestor = Person(
                        firstname=firstname,
                        lastname=lastname,
                        type=PersonType.REQUESTOR
                    )
                    
                    # Parse and validate people list
                    requested_people = parse_people_list(people_text)
                    
                    # Create context
                    context = DocumentContext(
                        requestor=requestor,
                        requested_people=requested_people,
                        gemeinde=gemeinde,
                        zweck="Adressverifikation" 
                    )
                    
                    # Verify addresses
                    _, summary, messages = await self.address_service.verify_addresses(context)
                    
                    # Format messages for Gradio chatbot - each message needs to be a tuple of (user, assistant)
                    chat_messages = []
                    for msg in messages:
                        if msg["role"] == "assistant":
                            # Add as assistant message with empty user message
                            chat_messages.append((None, f"{msg['name']}: {msg['content']}"))
                        elif msg["role"] == "user":
                            # Add as user message with empty assistant message
                            chat_messages.append((msg['content'], None))
                    
                    return summary, chat_messages
                    
                except Exception as e:
                    return f"⚠️ Fehler: {str(e)}", []
            
            async def generate_document(
                req_firstname: str,
                req_lastname: str,
                gemeinde: str,
                zweck: str,
                people_text: str
            ) -> str:
                """Handle document generation."""
                try:
                    # First verify addresses to get the latest data
                    requestor = Person(
                        firstname=req_firstname,
                        lastname=req_lastname,
                        type=PersonType.REQUESTOR
                    )
                    requested_people = parse_people_list(people_text)
                    
                    # Create initial context for verification
                    verification_context = DocumentContext(
                        requestor=requestor,
                        requested_people=requested_people,
                        gemeinde=gemeinde,
                        zweck=zweck
                    )
                    
                    # Verify addresses
                    await self.address_service.verify_addresses(verification_context)
                    
                    # Get structured data from report plugin
                    verified_requestor = self.address_service.report_plugin.get_requestor()
                    verified_people = self.address_service.report_plugin.get_requested_people()
                    
                    # Create new Person objects with verified data
                    if verified_requestor:
                        requestor = Person(
                            firstname=verified_requestor["firstname"],
                            lastname=verified_requestor["lastname"],
                            address=verified_requestor.get("address"),
                            city=verified_requestor.get("city"),
                            type=PersonType.REQUESTOR
                        )
                    
                    requested_people = []
                    for person_data in verified_people:
                        person = Person(
                            firstname=person_data["firstname"],
                            lastname=person_data["lastname"],
                            address=person_data.get("address"),
                            city=person_data.get("city"),
                            type=PersonType.REQUESTED
                        )
                        requested_people.append(person)
                    
                    # Create final context with verified data
                    final_context = DocumentContext(
                        requestor=requestor,
                        requested_people=requested_people,
                        gemeinde=gemeinde,
                        zweck=zweck
                    )
                    
                    # Generate document
                    document = await self.document_service.generate_document(final_context)
                    return document
                    
                except Exception as e:
                    return f"⚠️ Fehler bei der Dokumentgenerierung: {str(e)}"
            
            async def validate_document(document_text: str) -> Tuple[str, List[Tuple[str, str]]]:
                """Handle document validation."""
                try:
                    report, _, messages = await self.document_service.validate_document(document_text)
                    
                    # Format messages for Gradio chatbot
                    chat_messages = []
                    for msg in messages:
                        if msg["role"] == "assistant":
                            chat_messages.append((None, f"{msg['name']}: {msg['content']}"))
                        elif msg["role"] == "user":
                            chat_messages.append((msg['content'], None))
                    
                    return report, chat_messages
                    
                except Exception as e:
                    return f"⚠️ Validierungsfehler: {str(e)}", []
            
            async def export_document(document_text: str) -> str:
                """Handle document export to Word format."""
                try:
                    # Add current date
                    date = datetime.now().strftime("%d.%m.%Y")
                    
                    # Convert to Word
                    _, output_path = self.export_service.markdown_to_docx(
                        document_text,
                        date=date
                    )
                    
                    return f"""✅ Dokument erfolgreich exportiert!
                    
                    Das Dokument wurde hier gespeichert: `{output_path}`"""
                    
                except Exception as e:
                    return f"⚠️ Exportfehler: {str(e)}"
            
            # Connect components
            verify_btn.click(
                fn=verify_addresses,
                inputs=[req_firstname, req_lastname, gemeinde, people_list],
                outputs=[verification_output, verification_chat]
            )
            
            generate_btn.click(
                fn=generate_document,
                inputs=[req_firstname, req_lastname, gemeinde, zweck, people_list],
                outputs=document_text
            )
            
            validate_btn.click(
                fn=validate_document,
                inputs=[document_text],
                outputs=[validation_output, validation_chat]
            )
            
            export_btn.click(
                fn=export_document,
                inputs=[document_text],
                outputs=export_status
            )
            
            return interface
    
def main():
    """Start the application server."""
    app = DocumentGeneratorApp()
    interface = app.create_interface()
    interface.queue()
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )

if __name__ == "__main__":
    main()