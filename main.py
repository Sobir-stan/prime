import uvicorn
import webbrowser

if __name__ == "__main__":
    uvicorn.run(
        "app.app:app",
        host="0.0.0.0",   # IMPORTANT for cloud
        port=8000,
        reload=True,
    )

def open_browser():
    webbrowser.open("http://localhost:8000/test")

open_browser()