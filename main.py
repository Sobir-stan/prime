import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.app:app",
        host="0.0.0.0",   # IMPORTANT for cloud
        port=8000,
        reload=True,
    )