from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
import os
from pathlib import Path

app = FastAPI()

# Define data models
class UserData(BaseModel):
    email: str
    name: str
    phone: str = None
    address: str = None

# Path to store user data
DATA_FILE = Path("/Users/dikshanta/Documents/MCP-SERVER-FASTMCP/users_data.json")

def load_users_data():
    """Load users data from JSON file"""
    if DATA_FILE.exists():
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users_data(data):
    """Save users data to JSON file"""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

@app.get("/health")
def health_check():
    return {"status": "healthy", "server": "simple-server"}

@app.get("/multiply")
def multiply_endpoint(a: float, b: float):
    return {
        "result": a * b,
        "operation": "multiplication",
        "inputs": [a, b]
    }

@app.post("/user")
def save_user(user: UserData):
    """Save user data with email as key"""
    try:
        users = load_users_data()
        users[user.email] = {
            "name": user.name,
            "phone": user.phone,
            "address": user.address
        }
        save_users_data(users)
        return {
            "message": "User data saved successfully",
            "email": user.email,
            "name": user.name
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving user: {str(e)}")

@app.get("/user/{email}")
def get_user(email: str):
    """Get user data by email"""
    try:
        users = load_users_data()
        if email in users:
            return {
                "email": email,
                "name": users[email]["name"],
                "phone": users[email].get("phone"),
                "address": users[email].get("address")
            }
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving user: {str(e)}")

@app.get("/users")
def get_all_users():
    """Get all users"""
    try:
        users = load_users_data()
        return {"users": users, "count": len(users)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving users: {str(e)}")

@app.delete("/user/{email}")
def delete_user(email: str):
    """Delete user by email"""
    try:
        users = load_users_data()
        if email in users:
            del users[email]
            save_users_data(users)
            return {"message": f"User {email} deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting user: {str(e)}") 
   