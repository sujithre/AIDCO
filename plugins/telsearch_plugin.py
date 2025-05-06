"""
plugins/telsearch_plugin.py - Plugin for Swiss address and phone lookup using tel.search.ch

This plugin interfaces with the tel.search.ch API to look up and validate
Swiss addresses and phone numbers.
"""

import requests
import re
import os
from typing import Annotated, Dict, Optional, Tuple
from dotenv import load_dotenv
from semantic_kernel.functions.kernel_function_decorator import kernel_function

class TelsearchPlugin:
    """
    A plugin to call the tel.search.ch API for looking up Swiss addresses and phone numbers.
    Uses the public API endpoint that doesn't require authentication.
    Returns results in Atom feed format.
    """

    def __init__(self):
        """Initialize the plugin with the tel.search.ch API base URL"""
        self.base_url = "https://search.ch/tel/api/"
        # Load environment variables for possible API key
        load_dotenv()
        self.api_key = os.environ.get("TELSEARCH_API_KEY")

    @kernel_function(
        name="search_person",
        description="Search for a person's contact information in a given Swiss location using tel.search.ch"
    )
    def search_person(
        self,
        name: Annotated[str, "Name to search for"],
        location: Annotated[str, "Location to search in (e.g. Zurich, Basel)"]
    ) -> str:
        """
        Returns the raw API result as an Atom feed if found.
        If an error occurs, returns a JSON-like string with 'error'.
        
        Args:
            name: Name of the person to search for
            location: Location/municipality to search within
            
        Returns:
            Atom feed XML as string or error message
        """
        print(f"DEBUG: Searching for '{name}' in '{location}'")
        
        params = {
            "was": name,
            "wo": location,
            "maxnum": 10  # Return up to 10 results
        }
        
        # Add API key if available
        if self.api_key:
            params["key"] = self.api_key
            print(f"DEBUG: Using API key: {self.api_key[:5]}...")
        
        try:
            url = self.base_url
            print(f"DEBUG: Requesting URL: {url} with params: {params}")
            
            resp = requests.get(url, params=params, timeout=10)
            print(f"DEBUG: Response status code: {resp.status_code}")
            
            # Print a sample of the response for debugging
            resp_sample = resp.text[:200] + "..." if len(resp.text) > 200 else resp.text
            print(f"DEBUG: Response sample: {resp_sample}")
            
            if resp.status_code != 200:
                return f'{{"error":"Telsearch returned {resp.status_code}"}}'
            
            # Extract entry titles for debugging
            entry_titles = re.findall(r"<entry>.*?<title[^>]*>(.*?)</title>", resp.text, re.DOTALL)
            if entry_titles:
                print(f"DEBUG: Found entry titles: {entry_titles}")
                print(f"DEBUG: ResponseText: {resp.text}...")
            return resp.text
        except Exception as e:
            print(f"DEBUG: Error during API call: {str(e)}")
            return f'{{"error":"Exception occurred: {str(e)}"}}'
    
    def parse_address(self, xml_response: str) -> Optional[Dict[str, str]]:
        """
        Parse a tel.search.ch Atom feed response to extract address information.
        
        Args:
            xml_response: The XML response from tel.search.ch API
            
        Returns:
            Dictionary with address components or None if parsing fails
        """
        if not xml_response or "error" in xml_response.lower():
            print(f"DEBUG: Invalid XML response or error in response")
            return None
        
        # Check if valid Atom feed
        if "<feed" not in xml_response:
            print(f"DEBUG: Response does not appear to be a valid Atom feed")
            return None
            
        # Check for entries
        entries_count = xml_response.count("<entry")
        print(f"DEBUG: Found {entries_count} entries in response")
        
        if entries_count == 0:
            print("DEBUG: No entries found in response")
            return None
            
        # Extract first entry
        entry_match = re.search(r"<entry>(.*?)</entry>", xml_response, re.DOTALL)
        if not entry_match:
            print("DEBUG: Could not extract entry from XML")
            return None
            
        entry_content = entry_match.group(1)
        print(f"DEBUG: Processing entry: {entry_content[:100]}...")
            
        address = {}
        
        # Extract name
        name_match = re.search(r"<title[^>]*>(.*?)</title>", entry_content)
        if name_match:
            print(f"DEBUG: Found name: {name_match.group(1)}")
        
        # Try to extract address from content field
        content_match = re.search(r"<content[^>]*>(.*?)</content>", entry_content, re.DOTALL)
        if content_match:
            content = content_match.group(1)
            print(f"DEBUG: Found content: {content}")
            
            # Parse address components
            address_pattern = r"([^,\d]+)\s+(\d+),\s*(\d{4})\s+([^,]+)"
            addr_match = re.search(address_pattern, content)
            if addr_match:
                address["street"] = addr_match.group(1).strip()
                address["streetno"] = addr_match.group(2).strip()
                address["zip"] = addr_match.group(3).strip()
                address["city"] = addr_match.group(4).strip()
                print(f"DEBUG: Extracted address from content: {address}")
        
        # If content parsing failed, try to extract structured fields
        if not address:
            # Extract address components from XML tags
            fields_to_extract = {
                "street": r"<tel:street>(.*?)</tel:street>",
                "streetno": r"<tel:streetno>(.*?)</tel:streetno>",
                "zip": r"<tel:zip>(.*?)</tel:zip>",
                "city": r"<tel:city>(.*?)</tel:city>"
            }
            
            for field, pattern in fields_to_extract.items():
                field_match = re.search(pattern, xml_response)
                if field_match:
                    address[field] = field_match.group(1)
        
        print(f"DEBUG: Final extracted address components: {address}")
        
        # Only return if we have at least one piece of information
        if address:
            return address
        
        # Try to extract address from title as last resort
        title_match = re.search(r"<title[^>]*>.*?(\d{4}\s+[^<]+)</title>", xml_response)
        if title_match:
            partial_address = title_match.group(1).strip()
            print(f"DEBUG: Found address in title: {partial_address}")
            return {"partial": partial_address}
        
        return None

    def format_address(self, name: str, address_info: Optional[Dict[str, str]]) -> Tuple[str, Optional[str]]:
        """
        Format the name and address data into a standardized string format.
        
        Args:
            name: The person's name to format
            address_info: Dictionary with address components
            
        Returns:
            Tuple of (formatted_name, formatted_address) where address can be None
        """
        # Parse name to get firstname and lastname
        if "," in name:
            parts = name.split(",", 1)
            if len(parts) == 2:
                lastname = parts[0].strip()
                firstname = parts[1].strip()
                formatted_name = f"{firstname} {lastname}"
            else:
                formatted_name = name
        else:
            parts = name.split()
            if len(parts) >= 2:
                firstname = parts[0]
                lastname = " ".join(parts[1:])
                formatted_name = f"{firstname} {lastname}"
            else:
                formatted_name = name
        
        # If no address found
        if not address_info:
            return formatted_name, None
            
        # If we have all address components
        if "street" in address_info and "zip" in address_info and "city" in address_info:
            street = address_info.get("street", "")
            streetno = address_info.get("streetno", "")
            zip_code = address_info.get("zip", "")
            city = address_info.get("city", "")
            
            # Format as "Street StreetNo, ZIP City"
            addr_str = f"{street} {streetno}, {zip_code} {city}"
            return formatted_name, addr_str.strip()
        
        # If we only have partial address
        if "partial" in address_info:
            return formatted_name, address_info["partial"]
            
        # If we have some components but not all
        addr_parts = []
        if "street" in address_info:
            addr_parts.append(f"{address_info['street']} {address_info.get('streetno', '')}")
        if "zip" in address_info or "city" in address_info:
            addr_parts.append(f"{address_info.get('zip', '')} {address_info.get('city', '')}")
            
        if addr_parts:
            return formatted_name, ", ".join(addr_parts).strip()
            
        return formatted_name, None