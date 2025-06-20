import jwt
import json

secret_key = "manodeepray2004"
user_data_path = "data/users.json"


def encode(json_payload):

    print(f"encoding : {json_payload}")
    encoded_payload = jwt.encode(payload= json_payload , key=secret_key , algorithm="HS256")

    print(encoded_payload)
    
    return encoded_payload



def decode(json_payload):
    print(f"decoding {json_payload}")
    decoded_payload = jwt.decode(json_payload , secret_key , algorithms=["HS256"])

    print(decoded_payload)
    
    return decoded_payload



def login(userid:str , password:str):
    with open(user_data_path , 'r') as f:
        users_auth = json.load(f) 

    
    if userid in users_auth['users']:
        
        if users_auth['users'][userid]["password"] == password:
            return {"db_id" : users_auth['users'][userid]['db_id']}
        else:
            return {"error" :f"ERROR : password is not valid"}
            
        
    else:
        return {"error": f"ERROR : user id : {userid} is not valid"}
    
    
def register(userid:str , password:str ):
    db_name = f"user_db_{userid}"
    
    with open(user_data_path , 'r') as f:
        users_auth = json.load(f) 
        
    users_auth["users"][userid] = {"password" : password , "db_id" : db_name}
    
    users_auth =  json.dumps(users_auth, indent=4)
    
    with open(user_data_path , 'w') as f:
        f.write(users_auth)
 
    
    return {"db_id" : db_name}
    
    
    
if __name__ =="_main__":
        
    print(login(userid="abc" , password="1234"))

    print(register(userid="manodeep" , password="1234"))


    print(login(userid="abc" , password="1234"))

    print(login(userid="manodeep" , password="1234"))

    