import asyncio
from fastmcp import Client
from google import genai
import os
from dotenv import load_dotenv
import httpx
import json
import re

load_dotenv()

def clean_json_response(text):
    """Extract JSON from markdown code blocks or return clean text"""
    # Remove markdown code blocks
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*$', '', text)
    text = text.strip()
    return text

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ---------------------------------------
# CORRECT MCP CLIENT URL (SSE endpoint)
# ---------------------------------------
mcp_client = Client("http://127.0.0.1:8001/sse")

# Gemini client
gemini_client = genai.Client(api_key=GEMINI_API_KEY)


async def chat_loop():
    # ---------------------------------------
    # Connect to MCP server properly
    # ---------------------------------------
    async with mcp_client:
        print("Chat started! Type 'exit' to quit.\n")

        async with httpx.AsyncClient() as http:
            while True:
                user = input("You: ")

                if user.lower() == "exit":
                    break

                # ---------------------------------------
                # STEP 1: Ask Gemini to give JSON actions
                # ---------------------------------------
                prompt = f"""
You extract user information and return ONLY JSON.

If user says:
"name, email, phone, address"

Return ONLY:

{{
  "action": "save_user",
  "data": {{
     "name": "...",
     "email": "...",
     "phone": "...",
     "address": "..."
  }}
}}

If no details found:
{{
  "action": "none"
}}

User said:
{user}
"""

                gemini_response = await gemini_client.aio.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=prompt,
                    config=genai.types.GenerateContentConfig(temperature=0)
                )

                raw = gemini_response.text.strip()
                print("Gemini raw output:", raw)

                # Clean and parse JSON
                try:
                    cleaned_json = clean_json_response(raw)
                    instructions = json.loads(cleaned_json)
                    print("✅ Parsed JSON successfully:", instructions)
                except Exception as e:
                    print(f"❌ Failed to parse JSON: {e}")
                    print(f"❌ Cleaned text was: {clean_json_response(raw)}")
                    continue

                # ---------------------------------------
                # STEP 2: If action = save_user → POST to FastAPI
                # ---------------------------------------
                if instructions.get("action") == "save_user":
                    data = instructions["data"]

                    try:
                        fastapi_response = await http.post(
                            "http://127.0.0.1:8000/user",
                            json=data
                        )
                        print("✅ FastAPI:", fastapi_response.json())
                    except Exception as e:
                        print("❌ FastAPI error:", str(e))

                # ---------------------------------------
                # STEP 3: Normal chat but with MCP tools enabled
                # ---------------------------------------
                try:
                    final_response = await gemini_client.aio.models.generate_content(
                        model="gemini-2.0-flash",
                        contents=f"User said: {user}\nInstructions: {raw}",
                        config=genai.types.GenerateContentConfig(
                            temperature=0,
                            tools=[mcp_client.session],   # FIXED
                        )
                    )
                    print("🤖 MCP/Gemini:", final_response.text)
                except Exception as e:
                    print(f"❌ MCP/Gemini error: {e}")
                    print("💡 Make sure the MCP server is running: python server.py")
                print()


async def main():
    await chat_loop()


if __name__ == "__main__":
    asyncio.run(main())
