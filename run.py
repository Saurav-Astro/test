import os
import subprocess
import sys
import threading
import time
import signal

def print_banner(text):
    print("\n" + "=" * 50)
    print(f"  {text}")
    print("=" * 50 + "\n")

def check_docker():
    try:
        subprocess.run(["docker", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return True
    except:
        return False

def setup_backend():
    print_banner("Setting up Backend")
    backend_dir = os.path.join(os.getcwd(), "backend")
    
    if not os.path.exists(os.path.join(backend_dir, "venv")):
        print("[Backend] Creating venv...")
        subprocess.run([sys.executable, "-m", "venv", "venv"], cwd=backend_dir)
    
    pip = os.path.join(backend_dir, "venv", "Scripts", "pip.exe") if os.name == "nt" else os.path.join(backend_dir, "venv", "bin", "pip")
    
    print("[Backend] Upgrading pip/setuptools...")
    subprocess.run([pip, "install", "--upgrade", "pip", "setuptools", "wheel"], cwd=backend_dir)
    
    print("[Backend] Installing requirements...")
    subprocess.run([pip, "install", "-r", "requirements.txt"], cwd=backend_dir)

def setup_frontend():
    print_banner("Setting up Frontend")
    frontend_dir = os.path.join(os.getcwd(), "frontend")
    print("[Frontend] npm install...")
    subprocess.run("npm install", cwd=frontend_dir, shell=True)

def run_service(command, cwd, name):
    print(f"[{name}] Starting...")
    return subprocess.Popen(command, cwd=cwd, shell=True)

if __name__ == "__main__":
    try:
        print_banner("ProXM Starter")
        
        if check_docker():
            print("[Info] Docker detected. You can also use 'docker-compose up --build'")
        else:
            print("[Info] Docker not detected. Using local Python/Node setup.")

        setup_backend()
        setup_frontend()
        
        print_banner("Starting Services")
        
        backend_dir = os.path.join(os.getcwd(), "backend")
        frontend_dir = os.path.join(os.getcwd(), "frontend")
        
        python = os.path.join(backend_dir, "venv", "Scripts", "python.exe") if os.name == "nt" else os.path.join(backend_dir, "venv", "bin", "python")
        
        # Start Backend
        backend_proc = run_service(f"\"{python}\" -m uvicorn app.main:app --reload --port 8000", backend_dir, "Backend")
        
        # Start Frontend
        frontend_proc = run_service("npm run dev", frontend_dir, "Frontend")
        
        print("\nServices are running!")
        print("Backend: http://localhost:8000")
        print("Frontend: http://localhost:5173")
        print("Press Ctrl+C to stop.\n")
        
        backend_proc.wait()
        frontend_proc.wait()
            
    except KeyboardInterrupt:
        print("\nStopping...")
        if 'backend_proc' in locals(): backend_proc.terminate()
        if 'frontend_proc' in locals(): frontend_proc.terminate()
        sys.exit(0)
