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

    # ✅ IMPORTANT FIX:
    # MongoDB may return password as str (old users) or bytes (new users)
    if isinstance(stored_password, str):
        stored_password = stored_password.encode("utf-8")

    return bcrypt.checkpw(
        password.encode("utf-8"),
        stored_password
    )


# ---------------------------------
# SIGNUP USER
# ---------------------------------
def signup_user(username, password, email, mobile):
    if users_col.find_one({"username": username}):
        return False

    hashed_password = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    )

    users_col.insert_one({
        "username": username,
        "password": hashed_password,  # ✅ STORE AS BYTES
        "email": email,
        "mobile": mobile
    })

    return True
