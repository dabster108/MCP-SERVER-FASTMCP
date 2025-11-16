import sys
import os
from pathlib import Path
from fastmcp import FastMCP
from fastapi import FastAPI
import uvicorn

# Add the parent directory to the Python path to allow imports
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

# Add the fastapi directory to the Python path
fastapi_dir = parent_dir / "fastapi"
sys.path.insert(0, str(fastapi_dir))

# Now import the FastAPI app
from main import app

# Create MCP server from the FastAPI app
mcp = FastMCP.from_fastapi(app)

# Create a new FastAPI app that includes both original routes and MCP
server_app = FastAPI()

# Include original routes
server_app.mount("/api", app)

# Add MCP endpoints
@server_app.get("/mcp")
async def mcp_endpoint():
    return {"message": "MCP server is running", "endpoints": ["/mcp"]}

if __name__ == "__main__":
    # Run both the original FastAPI and MCP server
    import threading
    import time
    
    def run_mcp():
        mcp.run(
            transport="sse",
            host="127.0.0.1",
            port=8002
        )
    
    # Start MCP server in a separate thread
    mcp_thread = threading.Thread(target=run_mcp, daemon=True)
    mcp_thread.start()
    
    # Give MCP server time to start
    time.sleep(1)
    
    # Run the main server with both API and MCP info
    uvicorn.run(server_app, host="127.0.0.1", port=8001)
