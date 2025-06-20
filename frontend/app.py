from flask import Flask, render_template, request, redirect, session, jsonify
import requests


import sys
import os

# Add root dir (parent of frontend) to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src import auth

app = Flask(__name__)
app.secret_key = "your_secret"

FASTAPI_URL = "http://localhost:8000"  # Your FastAPI base URL

@app.route("/")
def home():
    return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():
    error_message = None  # Default: no error

    if request.method == "POST":
        userid = request.form["userid"]
        password = request.form["password"]
        action = request.form["action"]

        raw_payload = {
            "userid": userid,
            "password": password,
            "action": action
        }

        try:
            jwt_payload = auth.encode(raw_payload)
            response = requests.post(f"{FASTAPI_URL}/login-register", json={"payload": jwt_payload})

            if response.status_code != 200:
                error_message = "Invalid credentials or user not found."
                return render_template("login.html", error=error_message)

            data = response.json()
            session["db_id"] = data["db_id"]

            init_resp = requests.get(f"{FASTAPI_URL}/user/{session['db_id']}")
            
            if init_resp.status_code != 200:
                error_message = "Failed to initialize chatbot."
                return render_template("login.html", error=error_message)

            return redirect("/chat")

        except Exception as e:
            error_message = f"An unexpected error occurred: {str(e)}"
            return render_template("login.html", error=error_message)

    return render_template("login.html", error=error_message)





@app.route("/chat")
def chat():
    if "db_id" not in session:
        return redirect("/login")
    return render_template("chat.html")

@app.route("/query", methods=["POST"])
def query():
    db_id = session.get("db_id")
    user_message = request.json.get("message")
    response = requests.post(f"{FASTAPI_URL}/users/{db_id}/query", json={"message": user_message})
    return jsonify(response.json())

@app.route("/add_contacts", methods=["POST"])
def add_contacts():
    db_id = session.get("db_id")
    files = request.files.getlist("images")
    files_to_send = [("contact_images", (f.filename, f.stream, f.mimetype)) for f in files]
    response = requests.post(f"{FASTAPI_URL}/users/{db_id}/add_contacts", files=files_to_send)
    return response.text, response.status_code
