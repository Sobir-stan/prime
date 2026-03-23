import os
import sys
import subprocess

def main():
    venv_dir = os.path.abspath(".venv")
    
    if os.name == 'nt':
        venv_python = os.path.join(venv_dir, "Scripts", "python.exe")
        venv_pip = os.path.join(venv_dir, "Scripts", "pip.exe")
    else:
        venv_python = os.path.join(venv_dir, "bin", "python")
        venv_pip = os.path.join(venv_dir, "bin", "pip")

    
    if os.path.abspath(sys.executable) != venv_python:
        print("Checking environment...")
        if not os.path.exists(venv_python):
            print("Creating virtual environment...")
            subprocess.check_call([sys.executable, "-m", "venv", venv_dir])
        
        print("Checking and installing requirements...")
        subprocess.check_call([venv_pip, "install", "-r", "requirements.txt"])
        
        print("Starting in virtual environment...")

        sys.exit(subprocess.call([venv_python] + sys.argv))

    import uvicorn
    uvicorn.run(
        "app.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )

if __name__ == "__main__":
    main()