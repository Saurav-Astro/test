import os
import subprocess
import sys
import threading
import time

def print_banner(text):
    print("\n" + "=" * 50)
    print(f"  {text}")
    print("=" * 50 + "\n")

def run_command(command, cwd, name):
    print(f"[{name}] Starting: {command}")
    process = subprocess.Popen(
        command,
        cwd=cwd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True
    )
    
    for line in process.stdout:
        print(f"[{name}] {line.strip()}")
    
    process.wait()
    return process.returncode

def setup_backend():
    print_banner("Setting up Backend")
    backend_dir = os.path.join(os.getcwd(), "backend")
    
    # Create venv
    if not os.path.exists(os.path.join(backend_dir, "venv")):
        print("[Backend] Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", "venv"], cwd=backend_dir)
    
    pip_path = os.path.join(backend_dir, "venv", "Scripts", "pip") if os.name == "nt" else os.path.join(backend_dir, "venv", "bin", "pip")
    
    # Upgrade basic tools
    print("[Backend] Upgrading pip, setuptools, wheel...")
    subprocess.run([pip_path, "install", "--upgrade", "pip", "setuptools", "wheel"], cwd=backend_dir)
    
    # Install requirements
    print("[Backend] Installing requirements from requirements.txt...")
    result = subprocess.run([pip_path, "install", "-r", "requirements.txt"], cwd=backend_dir)
    
    if result.returncode != 0:
        print("[Backend] Some requirements failed. Trying to install them individually...")
        with open(os.path.join(backend_dir, "requirements.txt"), "r") as f:
            for line in f:
                pkg = line.strip()
                if not pkg or pkg.startswith("#"): continue
                print(f"[Backend] Installing {pkg}...")
                # If Pillow fails, try without version constraint
                if "Pillow" in pkg:
                    res = subprocess.run([pip_path, "install", pkg], cwd=backend_dir)
                    if res.returncode != 0:
                        print(f"[Backend] {pkg} failed. Trying latest Pillow...")
                        subprocess.run([pip_path, "install", "Pillow"], cwd=backend_dir)
                else:
                    subprocess.run([pip_path, "install", pkg], cwd=backend_dir)
    
    # Check .env
    if not os.path.exists(os.path.join(backend_dir, ".env")):
        print("[Warning] backend/.env file not found. Backend might fail to start.")

def setup_frontend():
    print_banner("Setting up Frontend")
    frontend_dir = os.path.join(os.getcwd(), "frontend")
    
    print("[Frontend] Installing node modules...")
    subprocess.run("npm install", cwd=frontend_dir, shell=True)

def start_backend():
    backend_dir = os.path.join(os.getcwd(), "backend")
    uvicorn_path = os.path.join(backend_dir, "venv", "Scripts", "uvicorn") if os.name == "nt" else os.path.join(backend_dir, "venv", "bin", "uvicorn")
    run_command(f"{uvicorn_path} app.main:app --reload --port 8000", backend_dir, "Backend")

def start_frontend():
    frontend_dir = os.path.join(os.getcwd(), "frontend")
    run_command("npm run dev", frontend_dir, "Frontend")

if __name__ == "__main__":
    try:
        print_banner("ProXM Multi-Process Starter")
        print(f"Python Version: {sys.version}")
        
        # 1. Setup
        setup_backend()
        setup_frontend()
        
        # 2. Run
        print_banner("Starting Services")
        
        backend_thread = threading.Thread(target=start_backend, daemon=True)
        frontend_thread = threading.Thread(target=start_frontend, daemon=True)
        
        backend_thread.start()
        time.sleep(3)  # Give backend a head start
        frontend_thread.start()
        
        print("\nBoth services are starting...")
        print("Backend: http://localhost:8000")
        print("Frontend: http://localhost:5173")
        print("\nPress Ctrl+C to stop both services.\n")
        
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nShutting down services...")
        sys.exit(0)
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        sys.exit(1)
