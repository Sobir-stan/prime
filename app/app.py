from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello from the server"}

@app.get("/ping")
def ping():
    return {"status": "ok"}