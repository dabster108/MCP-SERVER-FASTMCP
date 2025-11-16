from fastapi import FastAPI

app = FastAPI()

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
