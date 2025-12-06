import subprocess
import time
import sys
import os
from threading import Thread

# Save the original directory
ORIGINAL_DIR = os.getcwd()

def run_backend():
    """Run the FastAPI backend"""
    print("🚀 Starting FastAPI backend...")
    backend_path = os.path.join(ORIGINAL_DIR, "backend")
    subprocess.run([
        sys.executable, "-m", "uvicorn", "main:app", 
        "--reload", "--port", "8000"
    ], cwd=backend_path)

def run_frontend():
    """Run the Streamlit frontend"""
    print("🎨 Starting Streamlit frontend...")
    time.sleep(3)  # Wait for backend to start
    frontend_path = os.path.join(ORIGINAL_DIR, "frontend")
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", "app.py"
    ], cwd=frontend_path)

def main():
    print("="*60)
    print("🌟 LITTLEHEROES - Pediatric Storybook Generator")
    print("="*60)
    print()
    
    # Check if required folders exist
    if not os.path.exists("backend"):
        print("❌ Error: backend folder not found!")
        sys.exit(1)
    
    if not os.path.exists("frontend"):
        print("❌ Error: frontend folder not found!")
        sys.exit(1)
    
    # Check if main.py exists in backend
    if not os.path.exists("backend/main.py"):
        print("❌ Error: backend/main.py not found!")
        sys.exit(1)
    
    # Check if app.py exists in frontend
    if not os.path.exists("frontend/app.py"):
        print("❌ Error: frontend/app.py not found!")
        sys.exit(1)
    
    print("✅ All files found!")
    print()
    print("Starting services...")
    print("📡 Backend will run on: http://localhost:8000")
    print("🌐 Frontend will run on: http://localhost:8501")
    print()
    print("Press Ctrl+C to stop both services")
    print("="*60)
    print()
    
    # Create threads for both processes
    backend_thread = Thread(target=run_backend, daemon=True)
    frontend_thread = Thread(target=run_frontend, daemon=True)
    
    # Start both threads
    backend_thread.start()
    frontend_thread.start()
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down services...")
        print("👋 Goodbye!")
        sys.exit(0)

if __name__ == "__main__":
    main()