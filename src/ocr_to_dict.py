import groq
from groq import Groq
import os

from dotenv import load_dotenv
import json
from typing import Dict, Any    
import datetime 
from pprint import pprint
from .background_search  import BackgroundSearcher
  
load_dotenv("./.env")



class OCRParser:

    def __init__(self) -> None:
        
        self.llm  = Groq(
                    api_key=os.environ['GROQ_API_KEY'],
                    )   
        self.response_count : int = 0
        
        self.response_limit : int = 100

    def get_response(self  , prompt : str , ) -> str:
        
        if self.response_count <= self.response_limit:
            
            response  = self.llm.chat.completions.create(
                        messages=[
                            {
                                "role": "user",
                                "content": f"{prompt}",
                            }
                        ],
                        model="llama-3.3-70b-versatile",
                    )
            
            self.response_count += 1
        
        else : response = "rate limit exceedee"
        
        
        return response
        
    def get_structured_prompt(self , ocr_text):
        self.structure = {
                        "type": "person",              #"person" or "organization"
                        "name": "Full Name or Organization Name",
                        "title": "Job Title or Role",  # e.g., "Professor", "CEO"
                        "photo_url": "https://...",    # Optional: Link to image/avatar
                        "affiliations": [
                            {
                            "institution": "Institution Name",
                            "department": "Department Name",  # Optional
                            "role": "Position/Role",
                            "start_date": "YYYY-MM-DD",      # Optional
                            "end_date": "YYYY-MM-DD"         # Optional
                            }
                        ],
                        "contact_details": {
                            "addresses": [
                            {
                                "type": "work",               # "work", "home", "branch"
                                "street": "123 Main St",
                                "city": "City",
                                "state": "State/Province",     # Optional
                                "postal_code": "12345",
                                "country": "Country"
                            }
                            ],
                            "phones": [
                            {
                                "type": "work",               # "work", "mobile", "fax"
                                "number": "+1234567890",
                                "extension": "123"           # Optional
                            }
                            ],
                            "emails": [
                            {
                                "type": "work",              # "work", "personal"
                                "address": "name@domain.com"
                            }
                            ],
                            "websites": [
                            {
                                "type": "official",           # "official", "portfolio", "social"
                                "url": "https://..."
                            }
                            ],
                            "social_media": [                 # Optional
                            {
                                "platform": "linkedin",       # "twitter", "github", etc.
                                "url": "https://linkedin.com/..."
                            }
                            ]
                        },
                        "tags": ["physics", "academia"],   # Optional: For categorization
                        "metadata": {
                            "source": "ocr",                 # "manual", "api", "csv_import"
                            "confidence": 0.95,              # Optional: OCR confidence score
                            "created_at": "YYYY-MM-DD",
                            "last_updated": "YYYY-MM-DD"
                        },
                        "notes": "Additional context..."   # Optional
                        }

        prompt = f""" Here's your **LLM system prompt** version for an OCR-to-Structured Contact Card Parsing agent. This is formatted to guide the LLM's behavior and outputs consistently:

                ---

                **System Prompt: OCR-to-Structured Contact Card Parser**

                You are an expert information extraction agent. Your task is to **convert OCR-scanned text into a structured contact card** object by extracting and categorizing all visible entities. Follow the exact field definitions and formatting instructions strictly.

                ---

                ### **Task**

                Parse the given OCR text into a JSON object representing a structured contact card.

                ---

                ### **Field Definitions**

                * **name** (`string`):
                Full name of the person or organization.
                Format: `"FirstName LastName"` or `"Organization Name"`.
                Example: `"Rajaai Cherkaoui El Moursli"`.

                * **title** (`string | null`):
                Job title or role (e.g., `"Professor"`, `"CEO"`). Omit if not clearly present.

                * **type** (`string`):
                `"person"` or `"organization"` depending on the subject of the contact card.

                * **affiliations** (`list of objects`):
                Each affiliation must include:

                * `institution` (`string`)
                * `department` (`string | null`)
                * `role` (`string | null`)

                * **contact\_details** (`object`):

                * `addresses` (`list of objects`):
                    Each object must include:

                    * `type` (`string`): `"work"`, `"home"`, or `"branch"`
                    * `street` (`string`)
                    * `city` (`string`)
                    * `country` (`string`)
                    * `postal_code` (`string | null`)

                * `phones` (`list of objects`):
                    Each object must include:

                    * `type` (`string`): `"work"`, `"mobile"`, or `"fax"`
                    * `number` (`string`): Include country code (e.g., `"+212 661 47 11 85"`)
                    * `extension` (`string | null`)

                * `emails` (`list of objects`):
                    Each object must include:

                    * `type` (`string`): `"work"` or `"personal"`
                    * `address` (`string`): Must be valid email format

                * `websites` (`list of objects`):
                    Each object must include:

                    * `type` (`string`): `"official"`, `"portfolio"`, or `"social"`
                    * `url` (`string`): Full URL (e.g., `"https://www.fsr.ac.ma"`)

                * **tags** (`list of strings | null`):
                Domain categories, such as `["academia", "physics" , etc]`. Omit if unclear.

                * **metadata** (`object`):

                * `source` (`string`): `"ocr"`, `"manual"`, or `"api"`
                * `confidence` (`float | null`): OCR confidence score between `0.0` and `1.0`

                ---

                ### **Instructions**

                * **Extract only from the provided OCR text**. Never invent or infer data.
                * **Normalize** noisy formats (e.g., `"Tel:" → "+212..."`).
                * **Prioritize** official contact details if multiple are present.
                * **Validate** data: Omit entries that are ambiguous or unreadable.
                * **Strict typing**: All data must match exactly the expected JSON schema.
                * **Omit** any field that has no visible or validated data.

                ---

                ### **Output Format**

                Respond with a **single JSON object** following the structure and types above. Do not include explanatory text, markdown, or commentary — just valid, formatted JSON.


                OCR CONTACT INFORMATION = {ocr_text}

                STRUCTURED_JSON : 
                """

        
        return prompt

    def json_string_to_dict(self , json_str: str) -> Dict[str, Any]:
        """Converts a JSON string to a Python dictionary with validation."""
        try:
            # Convert JSON string to dictionary
            contact_dict = json.loads(json_str)
            
            # Validate required fields
            required_fields = ['name', 'type', 'contact_details']
            for field in required_fields:
                if field not in contact_dict:
                    raise ValueError(f"Missing required field: {field}")
            
            # Validate type
            if contact_dict['type'] not in ['person', 'organization']:
                raise ValueError("Type must be either 'person' or 'organization'")
                
            return contact_dict
        
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {str(e)}")
    
    
    
    
    def clean_data(self , output):
        
        cleaned = output.replace("\n" , "")
        cleaned = cleaned.replace("json" , "")
        cleaned = cleaned.replace("```" , "")
        
        
        
        return cleaned
    
    
    def generate_metadata(self , image_path):
        metadata = {}
        
        metadata["creation_time"] = datetime.datetime.now().isoformat()
        metadata["source"] = image_path

        return metadata
        
    
    
    
    def getStructuredDict(self , ocr_text , image_path):
        
        prompt = self.get_structured_prompt(ocr_text=ocr_text)
        response = self.get_response(prompt)
        output = response.choices[0].message.content
        cleaned = self.clean_data(output= output)
        
        
        contact_dict = self.json_string_to_dict(cleaned)
        
        metadata = self.generate_metadata(image_path=image_path)
        contact_dict['metadata'].update(metadata)
        
        
        
        searcher = BackgroundSearcher(llm= OCRParser())
        
        contact_dict = searcher.get_background_info(contact_dict=contact_dict)
        
        return contact_dict
    
    
    
    def parseOCRTexts(self , ocr_texts: list , image_paths: list):
        
        initial_contact_details_dicts = []
        
        
        for ocr_text , image_path in zip(ocr_texts , image_paths):
            contact_dict = self.getStructuredDict(ocr_text=ocr_text , image_path= image_path)
            initial_contact_details_dicts.append(contact_dict)
        
        return initial_contact_details_dicts
    
    
if __name__ == "__main__":
    
    llm = OCRParser()
    
    ocr_texts = [': Professor Rajaai Cherkaoui El Moursli member of Hassan II Academy of Science and Technology . <ocr> University Mohammed V Universite Faculte des Sciences Rabat Professor Rajaai Cherkaoui El Moursli Member of Hassan II Academy of Science and Technology Avenue Ibn Batouta. BP 1014 . Agdal.Rabat Tel : + 212 (0) 5 37 77 18 34/35/38 r.cherkaoui@academiesciences.ma Fax : + 212 (0) 5 37 77 42 61 Gsm : +212 661 47 11 85 / 06 62 07 94 00 Site web : www.fsr.ac.ma scholar.um5.ac.ma/rajaa.cherkaoui E-mail : rajaa.cherkaoui@um5.ac.ma r.cherkaoui@academiesciences.ma Gsm : +212 661 47 11',
                 ': Professor Rajaai Cherkaoui El Moursli member of Hassan II Academy of Science and Technology . <ocr> University Mohammed V Universite Faculte des Sciences Rabat Professor Rajaai Cherkaoui El Moursli Member of Hassan II Academy of Science and Technology Avenue Ibn Batouta. BP 1014 . Agdal.Rabat Tel : + 212 (0) 5 37 77 18 34/35/38 r.cherkaoui@academiesciences.ma Fax : + 212 (0) 5 37 77 42 61 Gsm : +212 661 47 11 85 / 06 62 07 94 00 Site web : www.fsr.ac.ma scholar.um5.ac.ma/rajaa.cherkaoui E-mail : rajaa.cherkaoui@um5.ac.ma r.cherkaoui@academiesciences.ma Gsm : +212 661 47 11']
    
    image_paths = ["20240625_154117.jpg" , "20240625_154117.jpg" ]
    
    
    
    contact_dicts = llm.parseOCRTexts(ocr_texts , image_paths)

    
    for i in range(len(contact_dicts)):
        pprint(f"contact _dict {i} : \n {contact_dicts[i]} \n\n")
    
    