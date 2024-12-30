import requests
from requests.auth import HTTPBasicAuth
import getpass
import xml.etree.ElementTree as ET
import json

# Base URL for Windchill API
BASE_URL = "https://plm.tkelevator.com/Windchill/servlet/odata/PDM"

# Prompt user for Windchill credentials
# USERNAME = input("Enter your Windchill username: ")
USERNAME = ""
PASSWORD = getpass.getpass("Enter your Windchill password: ")

# Part numbers to retrieve
part_numbers = ["D8000743810.SLDDRW"]

def get_latest_document(part_number):
    # Search for the document by part number
    response = requests.get(
        f"{BASE_URL}/CADDocuments",
        params={"$filter": f"Number eq '{part_number}'"},  # Adjust the filter as needed
        auth=HTTPBasicAuth(USERNAME, PASSWORD)
    )
    response.raise_for_status()

    data = response.json()
    
    # Print the full response for debugging
    print(json.dumps(data, indent=4))

    # Process the documents (if any)
    if "value" in data and data["value"]:
        print(f"Found {len(data['value'])} document(s) for part number: {part_number}")
        for doc in data["value"]:
            print(f"Document ID: {doc['ID']}, Version: {doc['Version']}, Name: {doc['Name']}")
    else:
        print(f"No documents found for part number: {part_number}")
        print(f"Response: {data}")

    # print(response.text)
    return response

    # Parse the Atom feed (XML)
    tree = ET.ElementTree(ET.fromstring(response.content))
    root = tree.getroot()

    # The Atom feed structure will vary, you need to check it for the document entries
    # Look for <entry> elements that contain the document metadata
    entries = root.findall(".//a:entry", namespaces={"a": "http://www.w3.org/2005/Atom"})

    if not entries:
        print(f"No document found for part number: {part_number}")
        return None

    # Assuming the first entry is the latest document (adjust logic as needed)
    document_entry = entries[0]
    document_id = document_entry.find(".//d:Id", namespaces={"d": "http://docs.oasis-open.org/odata/ns/data"}).text

    # Now get the document content (e.g., latest file version)
    content_response = requests.get(
        f"{BASE_URL}/Documents('{document_id}')/Content/Latest",
        auth=HTTPBasicAuth(USERNAME, PASSWORD)
    )
    content_response.raise_for_status()
    return content_response.content

# Retrieve and save the latest documents
for part_number in part_numbers:
    pdf_data = get_latest_document(part_number)
    # if pdf_data:
    #     with open(f"D{part_number}_latest.pdf", "wb") as file:
    #         file.write(pdf_data)
    #     print(f"Downloaded latest PDF for part number: {part_number}")
