
import os
from pathlib import Path
from datetime import datetime
from .src import ocr_to_dict , image_to_ocr , chatbot , retriever
from .src import auth as auth
from typing import Dict

from fastapi import FastAPI ,  Request
import  asyncio
from pydantic import BaseModel
import jwt
from fastapi import UploadFile, File, Form
from typing import List , Union

import logging
import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))



# Basic logging setup
logging.basicConfig(
    level=logging.INFO,  # Change to DEBUG for even more verbosity
    format="%(asctime)s [%(levelname)s] %(message)s",
    filename="server.log",
    filemode="a",
)

logger = logging.getLogger(__name__)

class ChatTurn(BaseModel):
    user: str
    chatbot: Union[str, Dict[str, str]]

class ChatRequest(BaseModel):
    message : str
    memory: List[ChatTurn]

class loginRegisterPayload(BaseModel):
    payload : str





IMAGE_DIR = "data/img_database"

ocr_model = image_to_ocr.OCRModel()
ocr_parser = ocr_to_dict.OCRParser()
contact_retriever = retriever.Retriever()
llm = None



llm_cache = {}



app = FastAPI()



@app.get("/")
async def chatbot_init():
    
    flags = {"ocr_model":False , "ocr_parser":False , "contact_retriever":False , "llm":False}
    
    if ocr_model:
        flags["ocr_model"] = True
        
    if ocr_parser:
        flags['ocr_parser']  = True
        
    if contact_retriever:
        flags["contact_retriever"] = True
    
    if llm:
        flags["llm"] = True
    logger.info("System component flags: %s", flags)

    return flags



@app.post("/login-register")

async def login_register(payload : loginRegisterPayload):
    db_id = "faiss_index"
    
    logger.info("Received login/register request")

    
    decoded_payload = auth.decode(json_payload=payload.payload)
    logger.info(f"Decoded JWT payload: {decoded_payload}")

    if decoded_payload['action'] == "login":
        login_json_response = auth.login(userid=decoded_payload['userid'] , password=decoded_payload["password"])
        db_id = login_json_response['db_id']
        logger.info(f"User {decoded_payload['userid']} logged in. DB ID: {db_id}")

    
    elif decoded_payload['action'] == 'register':
        
        register_json_response = auth.register(userid=decoded_payload['userid'] , password=decoded_payload["password"])
        db_id = register_json_response["db_id"]
        logger.info(f"User {decoded_payload['userid']} registered. DB ID: {db_id}")

    
    return {"db_id":db_id}    
    


@app.get("/user/{db_id}")
async def retrieve(db_id):
    
    logger.info(f"Loading retriever for db_id={db_id}")

    contact_retriever.load_index(db_id)
    llm = chatbot.Chatbot(retriever=contact_retriever) 

    llm_cache[db_id] = llm
    logger.info(f"Chatbot loaded and cached for db_id={db_id}")
    return {"response": f"retirever loaded for user databasse{db_id}"}
   
    
@app.post("/users/{db_id}/query")

async def query_retriever(db_id:str , query : ChatRequest):
    user_message = query.message
    memory = query.memory
    
    logger.info(f"Received query for db_id={db_id}: {user_message} ||  length of conversation memory {len(memory)}")
    if db_id not in llm_cache:
        logger.warning(f"LLM not loaded for db_id={db_id}")
        return {"error":"user chatot not loaded"}
    
    llm = llm_cache[db_id]
    
    response = llm.chatcompletion(query=user_message , memory = memory )
    logger.info(f"Chatbot response: {response}")
    return {"response" : response}
    
    

@app.post("/users/{db_id}/add_contacts")
async def add_to_retriever(
    db_id: str,
    contact_images: List[UploadFile] = File(...),
):
    image_paths = []
    ocr_texts = []
    
    logger.info(f"Received {len(contact_images)} image(s) for db_id: {db_id}")

    for image_file in contact_images:
        contents = await image_file.read()
        file_path = f"{IMAGE_DIR}/{image_file.filename}"

        with open(file_path, "wb") as f:
            f.write(contents)

        image_paths.append(file_path)
        logger.info(f"Saved uploaded file: {file_path}")




    logger.info("Running OCR on uploaded images...")
    ocr_texts, _ = ocr_model.getOCRtext(image_paths=image_paths)
    
    logger.info("Parsing OCR text to contact dictionaries...")
    contact_dicts = ocr_parser.parseOCRTexts(ocr_texts=ocr_texts, image_paths=image_paths)
    
    
    logger.info(f"Loading contact retriever for db_id={db_id}")
    contact_retriever.load_index(index_path=db_id)


    logger.info(f"Adding {len(contact_dicts)} contact(s) to retriever")
    contact_retriever.add_data(data_list=contact_dicts)


    logger.info(f"Successfully added contacts for db_id={db_id}")
    return {"status": "contacts added", "count": len(contact_dicts)}

# @app.post()


