# background_search.py

import requests
import json
import pprint
from typing import Dict, Any
from dotenv import load_dotenv
import os

load_dotenv("./.env")






class BackgroundSearcher:
    def __init__(self, llm,):
        self.llm = llm
        self.api_key = os.environ['TAVILY_API_KEY']
        self.search_url = "https://api.tavily.com/search"

    def query(self, query: str):
        payload = {
            "query": query,
            "topic": "general",
            "search_depth": "basic",
            "chunks_per_source": 3,
            "max_results": 1,
            "time_range": None,
            "days": 7,
            "include_answer": True,
            "include_raw_content": True,
            "include_images": False,
            "include_image_descriptions": False,
            "include_domains": [],
            "exclude_domains": [],
            "country": None
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        response = requests.post(self.search_url, json=payload, headers=headers)
        if not response.ok:
            raise Exception(f"API request failed: {response.status_code} - {response.text}")
        
        return json.loads(response.text)

    def generate_query(self, prompt: str) -> str:
        response = self.llm.get_response(prompt=prompt)
        return response.choices[0].message.content.strip().split("Search query:")[-1].strip()

    def get_background_info(self, contact_dict: Dict[str, Any]) -> Dict[str, Any]:
        background_info = {
            'company_details': None,
            'individual_detail': None
        }

        # 1. Individual background
        individual_prompt = f"""
        You are a search query generation assistant. Your task is to generate a short and precise web search query to learn more about the following individual based on the provided structured data:

        Data: {contact_dict}

        Generate a web search query that would help a search engine find authoritative pages about this person (Wikipedia, university page, research profile, etc.).
        Use their name, affiliation, or any other useful info.

        Output format:
        Search query: <query here>
        """
        individual_query = self.generate_query(individual_prompt)
        individual_result = self.query(individual_query)
        background_info['individual_detail'] = individual_result.get("answer")

        # 2. Company/institution background
        company_prompt = f"""
        You are a search query generation assistant. Your task is to generate a short and precise web search query to learn more about the following institution based on the provided structured data:

        Data: {contact_dict}

        Generate a web search query that would help a search engine find authoritative pages about this institution/company (Wikipedia, university page, research profile, etc.).
        Mention what the institution does, sells, or is known for. keep it small and simple

        Output format:
        Search query: <query here>
        """
        company_query = self.generate_query(company_prompt)
        
        print(company_query)
        
        # breakpoint()
        company_result = self.query(company_query)
        background_info['company_details'] = company_result.get("answer")

        contact_dict['background_info'] = background_info
        return contact_dict
