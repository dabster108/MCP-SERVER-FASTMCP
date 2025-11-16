import asyncio
import subprocess
import sys
import time
import signal
import os
from pathlib import Path

def start_mcp_server():
    """Start the FastMCP server in a subprocess"""
    server_path = Path(__file__).parent / "mcp-server" / "server.py"
    return subprocess.Popen([sys.executable, str(server_path)], 
                          stdout=subprocess.PIPE, 
                          stderr=subprocess.PIPE)

def start_fastapi_server():
    """Start the FastAPI server in a subprocess"""
    fastapi_path = Path(__file__).parent / "fastapi" / "main.py"
    return subprocess.Popen(["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"], 
                          cwd=fastapi_path.parent,
                          stdout=subprocess.PIPE, 
                          stderr=subprocess.PIPE)

async def run_mcp_client():
    """Run the MCP client demo"""
    client_path = Path(__file__).parent / "mcp-server" / "client.py"
    
    # Import and run the client
    sys.path.insert(0, str(client_path.parent))
    from client import main as client_main
    await client_main()

def cleanup_processes(*processes):
    """Clean up running processes"""
    for process in processes:
        if process and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()

def main():
    print("🚀 FastMCP + FastAPI Integration Demo")
    print("======================================")
    
    while True:
        print("\nChoose an option:")
        print("1. Run MCP Server + Client Demo (Gemini + FastMCP)")
        print("2. Run MCP Server + FastAPI Server (HTTP API)")
        print("3. Run All (MCP Server + FastAPI + Client Demo)")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            run_mcp_and_client()
        elif choice == "2":
            run_mcp_and_fastapi()
        elif choice == "3":
            run_all_services()
        elif choice == "4":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please try again.")

def run_mcp_and_client():
    """Run MCP server and client demo"""
    print("\n🔧 Starting FastMCP server...")
    mcp_process = start_mcp_server()
    
    try:
        # Wait for server to start
        time.sleep(3)
        
        print("🤖 Running MCP client demo with Gemini...")
        asyncio.run(run_mcp_client())
        
    except KeyboardInterrupt:
        print("\n⏹️ Stopping services...")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        cleanup_processes(mcp_process)
        print("✅ Services stopped.")

def run_mcp_and_fastapi():
    """Run MCP server and FastAPI server"""
    print("\n🔧 Starting FastMCP server...")
    mcp_process = start_mcp_server()
    
    print("🔧 Starting FastAPI server...")
    fastapi_process = start_fastapi_server()
    
    try:
        # Wait for servers to start
        time.sleep(3)
        
        print("\n✅ Servers running:")
        print("   📡 FastMCP Server: http://localhost:8001/mcp")
        print("   🌐 FastAPI Server: http://localhost:8000")
        print("   📚 FastAPI Docs: http://localhost:8000/docs")
        print("\n🧪 Try the multiply endpoint:")
        print("   curl -X POST http://localhost:8000/multiply -H 'Content-Type: application/json' -d '{\"a\": 3, \"b\": 5}'")
        print("\n⏹️ Press Ctrl+C to stop...")
        
        # Keep running until interrupted
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n⏹️ Stopping services...")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        cleanup_processes(mcp_process, fastapi_process)
        print("✅ Services stopped.")

def run_all_services():
    """Run all services"""
    print("\n🔧 Starting all services...")
    mcp_process = start_mcp_server()
    fastapi_process = start_fastapi_server()
    
    try:
        # Wait for servers to start
        time.sleep(3)
        
        print("\n✅ All services running:")
        print("   📡 FastMCP Server: http://localhost:8000/mcp")
        print("   🌐 FastAPI Server: http://localhost:8000")
        print("   📚 FastAPI Docs: http://localhost:8000/docs")
        
        print("\n🤖 Running MCP client demo...")
        asyncio.run(run_mcp_client())
        
        print("\n⏹️ Press Ctrl+C to stop servers...")
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n⏹️ Stopping services...")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        cleanup_processes(mcp_process, fastapi_process)
        print("✅ All services stopped.")

if __name__ == "__main__":
    main()
