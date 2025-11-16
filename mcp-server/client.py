from fastmcp import Client
from google import genai
import asyncio
from dotenv import load_dotenv
import os

load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# FIX: Use correct MCP port (8002) and endpoint
mcp_client = Client("http://127.0.0.1:8002/mcp")

gemini_client = genai.Client(api_key=GEMINI_API_KEY)

async def main():
    try:
        async with mcp_client:
            response = await gemini_client.aio.models.generate_content(
                model="gemini-2.0-flash",
                contents="multiply two numbers 3 and 5",
                config=genai.types.GenerateContentConfig(
                    temperature=0,
                    tools=[mcp_client.session],
                ),
            )
            print(response.text)
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure the MCP server is running on port 8001")

if __name__ == "__main__":
    asyncio.run(main())
