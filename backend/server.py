from src.app import app

# Entrypoint for the FastAPI development server with reload enabled
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "__main__:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )