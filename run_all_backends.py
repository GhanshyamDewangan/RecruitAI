import subprocess
import time
import sys
import os

def run_backends():
    # Paths to the backend scripts
    aptitude_backend = os.path.join("Aptitude_Generator", "backend", "main.py")
    jd_backend = os.path.join("JD_Generator", "backend", "main.py")

    print("🚀 Starting Selected Backends...")

    # Start Aptitude Generator Backend
    print(f"📦 Starting Aptitude Generator Backend on port 8002...")
    aptitude_proc = subprocess.Popen([sys.executable, aptitude_backend])

    # Start JD Generator Backend
    print(f"📦 Starting JD Generator Backend on port 8001...")
    jd_proc = subprocess.Popen([sys.executable, jd_backend])

    try:
        while True:
            time.sleep(1)
            if aptitude_proc.poll() is not None:
                print("❌ Aptitude Generator Backend stopped unexpectedly.")
                break
            if jd_proc.poll() is not None:
                print("❌ JD Generator Backend stopped unexpectedly.")
                break
    except KeyboardInterrupt:
        print("\n🛑 Stopping all backends...")
        aptitude_proc.terminate()
        jd_proc.terminate()
        print("✅ Backends stopped.")

if __name__ == "__main__":
    run_backends()
