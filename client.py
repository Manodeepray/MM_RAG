
    
import requests
import src.auth as auth  

# url = "http://0.0.0.0:8000/login-register"

# login_reg_payload = {
#     'userid': "rick",
#     'password': "12345",
#     'action': "register",
# }

# def send_payload(payload):
#     jwt_token = auth.encode(json_payload=payload)

#     payload_to_send = {"payload": jwt_token}

#     print(f"Payload sent: {payload_to_send}")

#     response = requests.post(url, json=payload_to_send)

#     print(f"Response status: {response.status_code}")
#     print(f"Response body: {response.text}")

#     return response

# print(send_payload(login_reg_payload))



import requests

# Replace with your actual FastAPI server URL and db_id
url = "http://localhost:8000/users/user_db_rick/add_contacts"

# List of image file paths to send
image_files = [
    "20240625_154117.jpg"
]

# Prepare the multipart form-data
files = [("contact_images", (open(path, "rb"))) for path in image_files]

# Send the POST request
response = requests.post(url, files=files)

# Print response
print("Status Code:", response.status_code)
print("Response:", response.text)

    
    