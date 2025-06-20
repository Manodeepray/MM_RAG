####basic gui with two functions -> upload image abd add to the Vetordb -> talk to the db



import streamlit as st
import os
from pathlib import Path
from datetime import datetime
from src import ocr_to_dict , image_to_ocr , chatbot , retriever


# ----------------------
# initializing the models
# -----------------------


# ---------------------------
# CONFIGURATION
# ---------------------------
st.set_page_config(page_title="Image + Chatbot App", layout="wide")

ocr_model = image_to_ocr.OCRModel()
ocr_parser = ocr_to_dict.OCRParser()
contact_retriever = retriever.Retriever()
llm = chatbot.Chatbot() 






UPLOAD_DIR = "img_database"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ---------------------------
# SIDEBAR: Image Upload
# ---------------------------
st.sidebar.title("Upload Images")
uploaded_files = st.sidebar.file_uploader(
    "Upload up to 3 images", 
    type=["png", "jpg", "jpeg"], 
    accept_multiple_files=True
)

if uploaded_files and len(uploaded_files) > 3:
    st.sidebar.error("You can upload a maximum of 3 images.")
    uploaded_files = uploaded_files[:3]

saved_paths = []
if uploaded_files:
    for file in uploaded_files:
        save_path = os.path.join(UPLOAD_DIR, f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.name}")
        with open(save_path, "wb") as f:
            f.write(file.getbuffer())
        saved_paths.append(save_path)

    st.sidebar.success(f"{len(saved_paths)} image(s) uploaded successfully!")
    st.sidebar.write("Saved paths:")
    for path in saved_paths:
        st.sidebar.code(path)

    # Dummy function to represent model inference
    def image_to_vectordb(image_paths):
        
        ocr_texts , image_paths = ocr_model.getOCRtext(image_paths= image_paths)
        contact_dicts = ocr_parser.parseOCRTexts(ocr_texts=ocr_texts , image_paths= image_paths)
        
        contact_retriever.add_data(data_list=contact_dicts)
        
        print(f" {len(image_paths)} image(s) added to the database.")
        return f" {len(image_paths)} image(s) added to the database."

    st.sidebar.write(image_to_vectordb(saved_paths))

# ---------------------------
# MAIN: Chatbot Section
# ---------------------------
st.title("🧠 Chatbot with Memory")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

user_input = st.text_input("Ask your question:")

if user_input:
    memory = st.session_state.chat_history[-3:]  # last 5 interactions
    
    memory_text = "\n".join([f"User: {m['user']}\nBot: {m['bot']}" for m in memory])
    
    
    
    response = llm.chatcompletion(query=user_input , memory= memory_text)

    # Save to chat history
    st.session_state.chat_history.append({
        "user": user_input,
        "bot": response
    })

# Display chat history
for chat in st.session_state.chat_history[-10:]:
    st.markdown(f"**🧑 You:** {chat['user']}")
    st.markdown(f"**🤖 Bot:** {chat['bot']}")
    st.markdown("---")
