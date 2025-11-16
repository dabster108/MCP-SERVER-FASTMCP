from google import genai
import asyncio
from dotenv import load_dotenv
import os
import requests 
import json

load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

API_BASE_URL = "http://127.0.0.1:8000"
gemini_client = genai.Client(api_key=GEMINI_API_KEY)

def save_user_data(email, name, phone=None, address=None):
    try:
        data = {
            "email": email,
            "name": name,
            "phone": phone,
            "address": address
        }
        response = requests.post(f"{API_BASE_URL}/user", json=data)
        if response.status_code == 200:
            result = response.json()
            return f"User saved successfully: {result['name']} ({result['email']})"
        else:
            return f"Error saving user: {response.text}"
    except Exception as e:
        return f"Error: {e}"

def get_user_data(email):
    try:
        response = requests.get(f"{API_BASE_URL}/user/{email}")
        if response.status_code == 200:
            user = response.json()
            return f"User Found:\n   Name: {user['name']}\n   Email: {user['email']}\n   Phone: {user.get('phone', 'N/A')}\n   Address: {user.get('address', 'N/A')}"
        elif response.status_code == 404:
            return f"User with email '{email}' not found"
        else:
            return f"Error: {response.text}"
    except Exception as e:
        return f"Error: {e}"

def get_all_users():
    try:
        response = requests.get(f"{API_BASE_URL}/users")
        if response.status_code == 200:
            result = response.json()
            if result['count'] == 0:
                return "No users found in the database"
            
            users_text = f"Found {result['count']} users:\n"
            for email, info in result['users'].items():
                users_text += f"   {info['name']} ({email})\n"
            return users_text
        else:
            return f"Error: {response.text}"
    except Exception as e:
        return f"Error: {e}"

def delete_user_data(email):
    try:
        response = requests.delete(f"{API_BASE_URL}/user/{email}")
        if response.status_code == 200:
            result = response.json()
            return f"{result['message']}"
        elif response.status_code == 404:
            return f"User with email '{email}' not found"
        else:
            return f"Error: {response.text}"
    except Exception as e:
        return f"Error: {e}"

async def chat_with_gemini(message):
    try:
        response = await gemini_client.aio.models.generate_content(
            model="gemini-2.0-flash",
            contents=message,
            config=genai.types.GenerateContentConfig(
                temperature=0.7,
            ),
        )
        return response.text
    except Exception as e:
        return f"Error communicating with Gemini: {e}"

def parse_save_command(command):
    try:
        parts = command.replace("save user", "").strip().split(",")
        if len(parts) >= 2:
            email = parts[0].strip()
            name = parts[1].strip()
            phone = parts[2].strip() if len(parts) > 2 else None
            address = parts[3].strip() if len(parts) > 3 else None
            return email, name, phone, address
        else:
            return None, None, None, None
    except:
        return None, None, None, None

async def interactive_chat_loop():
    print("Welcome to the Smart Chat Assistant!")
    print("Commands:")
    print("   save user email@example.com, John Doe, +123456789, 123 Main St")
    print("   get user email@example.com")
    print("   show users")
    print("   delete user email@example.com")
    print("   Type 'quit' to exit")
    print("=" * 60)
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("Goodbye!")
                break
            
            if user_input.lower().startswith("save user"):
                email, name, phone, address = parse_save_command(user_input)
                if email and name:
                    result = save_user_data(email, name, phone, address)
                    print(f"Assistant: {result}")
                else:
                    print("Assistant: Invalid format. Use: save user email@example.com, John Doe, +123456789, 123 Main St")
            
            elif user_input.lower().startswith("get user"):
                email = user_input.replace("get user", "").strip()
                if email:
                    result = get_user_data(email)
                    print(f"Assistant: {result}")
                else:
                    print("Assistant: Please provide an email. Use: get user email@example.com")
            
            elif user_input.lower() in ["show users", "list users", "get all users"]:
                result = get_all_users()
                print(f"Assistant: {result}")
            
            elif user_input.lower().startswith("delete user"):
                email = user_input.replace("delete user", "").strip()
                if email:
                    result = delete_user_data(email)
                    print(f"Assistant: {result}")
                else:
                    print("Assistant: Please provide an email. Use: delete user email@example.com")
            
            else:
                print("Assistant: Thinking...")
                response = await chat_with_gemini(user_input)
                print(f"Assistant: {response}")
                
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

async def main():
    await interactive_chat_loop()

if __name__ == "__main__":
    asyncio.run(main())