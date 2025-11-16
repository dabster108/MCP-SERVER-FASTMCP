import asyncio
from fastmcp import Client
from google import genai
import os
from dotenv import load_dotenv
import requests

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# MCP SERVER PORT FIXED (8001)
mcp_client = Client("http://127.0.0.1:8001/mcp")

gemini_client = genai.Client(api_key=GEMINI_API_KEY)


async def chat_loop():
    async with mcp_client:
        print("Chat started! Type 'exit' to quit.\n")

        while True:
            user = input("You: ")

            if user.lower() == "exit":
                break

            save_res = requests.post(
                "http://127.0.0.1:8000/user",
                json={
                    "email": "test@gmail.com",
                    "name": user,
                    "phone": "123456",
                    "address": "ktm"
                }
            )

            print("FastAPI:", save_res.json())

            # CALL GEMINI + MCP
            response = await gemini_client.aio.models.generate_content(
                model="gemini-2.0-flash",
                contents=f"User said: {user}",
                config=genai.types.GenerateContentConfig(
                    temperature=0,
                    tools=[mcp_client.session],
                ),
            )

            print("MCP/Gemini:", response.text)
            print()


async def main():
    await chat_loop()


if __name__ == "__main__":
    asyncio.run(main())
