# 
import sys
import os
from pathlib import Path
from fastmcp import FastMCP

parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

api_dir = parent_dir / "api"
sys.path.insert(0, str(api_dir))

from main import app   # FastAPI app

mcp = FastMCP.from_fastapi(app)

if __name__ == "__main__":
    mcp.run(
        transport="sse",
        host="127.0.0.1",
        port=8001
    )
