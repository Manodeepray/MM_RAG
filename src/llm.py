import groq
from groq import Groq
import os
from dotenv import load_dotenv
import json
from typing import Dict, Any    
from pprint import pprint

load_dotenv("./.env")



class LLM:

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
    
if __name__ == "__main__":
    
    llm = LLM()
    print(llm.get_response(prompt="hello"))