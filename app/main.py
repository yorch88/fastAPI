from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from motor.motor_asyncio import AsyncIOMotorClient
import os
import jwt
import datetime

app = FastAPI()

# JWT Secret Key
SECRET_KEY = "144364c338aa481086efed11f9332c66"  # Change this to a strong secret key

# Pydantic Model for User
class User(BaseModel):
    username: str
    email: EmailStr

# MongoDB Dependency
def get_db() -> AsyncIOMotorClient:
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongodb:27018")
    client = AsyncIOMotorClient(MONGO_URI)
    db = client["mydatabase_new"]
    return db

@app.post("/users/")
async def create_user(user: User, db: AsyncIOMotorClient = Depends(get_db)):
    users_collection = db["Users"]
    existing_user = await users_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = {"username": user.username, "email": user.email}
    result = await users_collection.insert_one(new_user)
    return {"id": str(result.inserted_id), "message": "User created successfully"}

@app.get("/users/")
async def get_users(db: AsyncIOMotorClient = Depends(get_db)):
    users_collection = db["Users"]
    users = await users_collection.find().to_list(100)
    return [{"id": str(user["_id"]), "username": user["username"], "email": user["email"]} for user in users]

# user5@example.com
# Generate JWT for a user found by email
@app.get("/emailuser/")
async def get_email_user(email: EmailStr, db: AsyncIOMotorClient = Depends(get_db)):
    users_collection = db["Users"]
    user = await users_collection.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Create a JWT that expires in 1 minute
    expiration = datetime.datetime.utcnow() + datetime.timedelta(minutes=1)
    token = jwt.encode({"email": email, "exp": expiration}, SECRET_KEY, algorithm="HS256")

    return {"token": token}


@app.get("/validate/")
async def validate_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return {"valid": True, 'email': payload['email']}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid Token")
