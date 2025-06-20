from . import retriever
from . import llm


class Chatbot:
    
    def __init__(self , retriever  = retriever.Retriever()):
        self.llm = llm.LLM()
        self.retriever = retriever
        
        
        
    def chatcompletion(self , query:str , memory = None):
        
        
        
        retrieved_context = self.retriever.query(query=query)
        
        
        prompt = f"""
        GOAL:
        you are an inteligent ai assistant .. your job is to take the user given query and context and provide suitable and structured response.
        
        INSTRUCTIONs:
        The response should be strucured and in .md format
        
        ignore the memory unless the user query needs previous conversation
        
    
        query = {query}
        
        context = {retrieved_context}
        
        memory = {memory}
        
        output = "
        
        """
        
        response = self.llm.get_response(prompt=prompt)
        
        
    
        return response.choices[0].message.content
        
        