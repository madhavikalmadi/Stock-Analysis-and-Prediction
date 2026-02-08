import bcrypt
from mongo_db import users_col

def login_user(username, password):
    if users_col is None:
        return False

    user = users_col.find_one({
        "username": {"$regex": f"^{username}$", "$options": "i"}
    })

    if not user:
        return False

    return bcrypt.checkpw(
        password.encode("utf-8"),
        user["password"]
    )


def signup_user(username, password, email, mobile):
    if users_col.find_one({"username": username}):
        return False

    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    users_col.insert_one({
        "username": username,
        "password": hashed,
        "email": email,
        "mobile": mobile
    })

    return True
