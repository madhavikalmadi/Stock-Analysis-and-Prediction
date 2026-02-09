import bcrypt
from mongo_db import users_col

# ---------------------------------
# LOGIN USER
# ---------------------------------
def login_user(username, password):
    if users_col is None:
        return False

    user = users_col.find_one({
        "username": {"$regex": f"^{username}$", "$options": "i"}
    })

    if not user:
        return False

    stored_password = user.get("password")

    # ✅ FIX: Support Plain Text Passwords (for Admin Visibility)
    if stored_password == password:
         return True
         
    # Fallback to bcrypt for existing hashed passwords
    try:
        # Convert to bytes for bcrypt if it's a string, BUT only if it looks like a hash
        if isinstance(stored_password, str):
             if stored_password.startswith("$2b$"):
                 stored_password = stored_password.encode("utf-8")
             else:
                 # If it's a string but doesn't look like a hash, and didn't match above, it's just wrong
                 return False

        return bcrypt.checkpw(
            password.encode("utf-8"),
            stored_password
        )
    except:
        return False


# ---------------------------------
# SIGNUP USER
# ---------------------------------
def signup_user(username, password, email, mobile):
    if len(password) < 8:
         return False
    # ✅ Case-insensitive check to prevent collisions (Madhu vs madhu)
    if users_col.find_one({"username": {"$regex": f"^{username}$", "$options": "i"}}):
         return False

    # ❌ DISABLED: bcrypt.hashpw (User requested visible passwords)
    # hashed_password = bcrypt.hashpw(
    #     password.encode("utf-8"),
    #     bcrypt.gensalt()
    # )

    users_col.insert_one({
        "username": username,
        "password": password,  # ✅ STORE AS PLAIN TEXT
        "email": email,
        "mobile": mobile
    })

    return True
