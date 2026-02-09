
from mongo_db import users_col
import bcrypt

print("Scanning for encrypted passwords...")

count = 0
for user in users_col.find():
    pwd = user.get("password")
    
    # Check if password looks like a bcrypt hash (bytes or $2b$ string)
    is_encrypted = False
    if isinstance(pwd, bytes) and pwd.startswith(b"$2b$"):
        is_encrypted = True
    elif isinstance(pwd, str) and pwd.startswith("$2b$"):
        is_encrypted = True
        
    if is_encrypted:
        print(f"Reseting password for user: {user.get('username')}")
        users_col.update_one(
            {"_id": user["_id"]},
            {"$set": {"password": "12345"}}
        )
        count += 1

print(f"Done! Reset {count} passwords to '12345'.")
