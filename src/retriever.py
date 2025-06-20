
from langchain.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.schema import Document
import json
import os


class Retriever:
    def __init__(self, index_path="faiss_index", model_name="sentence-transformers/all-MiniLM-L6-v2"):
        self.index_path = os.path.join("vector_dbs" ,index_path)
        self.embedder = HuggingFaceEmbeddings(model_name=model_name)
        self.vectordb = None
        # self.load_index(index_path=index_path)
        

    def _dict_to_doc(self, d: dict):
        content = json.dumps(d, indent=2)
        metadata = d.get("metadata", {})
        return Document(page_content=content, metadata=metadata)

    def add_data(self, data_list: list[dict]):
        docs = [self._dict_to_doc(d) for d in data_list]
        self.vectordb.add_documents(docs)
        self.vectordb.save_local(self.index_path)

    def query(self, query: str, k: int = 3):
        return self.vectordb.similarity_search(query, k=k)
    
    
    
    def load_index(self , index_path):
        
        self.index_path = os.path.join("vector_dbs" ,index_path)

        if os.path.exists(self.index_path):
            self.vectordb = FAISS.load_local(self.index_path, self.embedder , allow_dangerous_deserialization = True)
        else:
            dummy_doc = Document(page_content="dummy", metadata={"source": "init"})
            self.vectordb = FAISS.from_documents([dummy_doc], self.embedder)
            self.vectordb.save_local(self.index_path)
            
        
        


if __name__ == "__main__":
    
    contact_dict = {
        "name": "Rajaai Cherkaoui El Moursli",
        "title": "Professor",
        "type": "Person",
        "metadata": {"source": "contacts.json"}
    }

    retriever = Retriever()
    

    # Add data to the vector store
    retriever.add_data([contact_dict])

    # Query the vector store
    results = retriever.query("Who is Rajaai Cherkaoui El Moursli?")
    for doc in results:
        print(doc.page_content)