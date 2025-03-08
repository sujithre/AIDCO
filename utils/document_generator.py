"""
utils/document_generator.py - Document generation and formatting utilities

This module handles the generation of structured documents like Verpflichtungserklärungen
by prompting an LLM to follow formatting rules specified in templates.
"""

import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.prompt_execution_settings import PromptExecutionSettings
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

async def generate_document_with_llm(
    template: str,
    req_firstname: str,
    req_lastname: str,
    addresses_dict: dict,
    gemeinde: str,
    zweck: str
) -> str:
    """
    Generate a document by having an LLM follow template instructions.
    
    Args:
        template: Document template with placeholders and LLM instructions
        req_firstname: Requestor's first name
        req_lastname: Requestor's last name
        addresses_dict: Dictionary mapping names to addresses
        gemeinde: Municipality name
        zweck: Purpose of the address request
        
    Returns:
        Fully formatted document text
    """
    # Get requestor info
    print(f"Requestor: {req_firstname} {req_lastname}")
    requestor_name = f"{req_firstname} {req_lastname}"
    
    # Handle requestor address retrieval with proper error handling
    if requestor_name in addresses_dict and addresses_dict[requestor_name]:
        requestor_address = addresses_dict[requestor_name]
    else:
        print(f"Warning: Address for requestor '{requestor_name}' not found in data")
        requestor_address = "[ADRESSE NICHT VERFÜGBAR]"

    # Build the list of people (exclude the requestor)
    people_entries = []
    for name, addr in addresses_dict.items():
        # Skip the requestor in the people list
        if name == requestor_name:
            continue
            
        if addr:
            people_entries.append(f"{name} ({addr})")
        else:
            people_entries.append(f"{name} (NICHT GEFUNDEN)")

    # Current date for the document
    current_date = datetime.now().strftime("%d. %B %Y")
    
    # Format people list as string
    people_list_str = "\n".join(people_entries) if people_entries else "Keine Personen gefunden"
    
    # Create a prompt for the LLM with clear instructions
    prompt = f"""
Du bist ein Experte für das Erstellen von behördlichen Dokumenten nach strikten Formaten.
Erstelle eine reale Verfügung (Kein Muster!) basierend auf der unten stehenden Vorlage.

INFORMATIONEN ZUM EINSETZEN:
1. Der Antragsteller heisst: {requestor_name}
2. Die Adresse des Antragstellers: {requestor_address}
3. Zweck der Auskunft: {zweck}
4. Aktuelles Datum: {current_date}
5. Liste der angefragten Personen:
```
{people_list_str}
```

ANWEISUNGEN:
1. Nutze die obige Vorlage und füge alle Daten korrekt ein.
2. Wenn es mehrere Personen gibt, formatiere sie als nummerierte Liste (1., 2., usw.).
3. Falls nur eine Person vorhanden ist, gib einfach den Namen und die Adresse direkt an.
4. Gib ein vollständiges Markdown-Dokument zurück.
5. Achte auf korrekte Absätze und Formatierung im Markdown.
6. Gib AUSSCHLIESSLICH den fertigen Dokumenttext zurück, ohne zusätzlichen Kommentar.

VORLAGE:
```markdown
{template}
```
"""

    # Initialize Semantic Kernel with Azure OpenAI
    kernel = Kernel()
    service_kwargs = {
        "deployment_name": os.environ.get("AZURE_OPENAI_REASONING_DEPLOYMENT", os.environ.get("AZURE_OPENAI_DEPLOYMENT")),
        "endpoint": os.environ.get("AZURE_OPENAI_ENDPOINT"),
        "api_key": os.environ.get("AZURE_OPENAI_KEY"),
    }
    
    # Add API version if using the new Azure OpenAI API
    if "2024" in os.environ.get("AZURE_OPENAI_API_VERSION", ""):
        service_kwargs["api_version"] = os.environ.get("AZURE_OPENAI_API_VERSION")
        
    reasoning_service = AzureChatCompletion(**service_kwargs)
    kernel.add_service(reasoning_service)
    
    # Invoke the LLM with the prompt
    result = await kernel.invoke_prompt(
        prompt=prompt,
        settings=PromptExecutionSettings(
            temperature=1,
            top_p=1,
            frequency_penalty=0.0,
            presence_penalty=0.0
        ),
    )

    # Clean result by removing any markdown code blocks
    result = "\n".join(line for line in str(result).splitlines() if "```" not in line)
    
    return str(result).strip()