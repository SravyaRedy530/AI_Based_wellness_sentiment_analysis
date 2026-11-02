"""
MoodMentor Unified Launcher
Starts both the Flask REST Backend API and the Streamlit Frontend simultaneously.
"""
import os
import sys
import time
import subprocess
import signal

def main():
    print("=" * 65)
    print("[*] Starting MoodMentor - AI Emotion Journal Platform")
    print("=" * 65)

    base_dir = os.path.abspath(os.path.dirname(__file__))
    python_exe = sys.executable

    # 1. Start Flask Backend
    backend_script = os.path.join(base_dir, "backend", "app.py")
    print(f"[*] Launching Flask REST Backend on port 5000...")
    backend_proc = subprocess.Popen(
        [python_exe, backend_script],
        cwd=base_dir,
        env=os.environ.copy()
    )

    # Allow Flask backend to initialize
    time.sleep(2)

    # 2. Start Streamlit Frontend
    frontend_script = os.path.join(base_dir, "frontend", "app.py")
    print(f"[*] Launching Streamlit UI on port 8501...")
    frontend_proc = subprocess.Popen(
        [python_exe, "-m", "streamlit", "run", frontend_script, "--server.port=8501", "--server.headless=true"],
        cwd=base_dir,
        env=os.environ.copy()
    )

    print("=" * 65)
    print("[OK] MoodMentor is now LIVE!")
    print("  - Frontend UI : http://localhost:8501")
    print("  - Backend API : http://localhost:5000/api/health")
    print("=" * 65)
    print("Press Ctrl+C to stop both servers.")

    try:
        while True:
            time.sleep(1)
            # Check if any process terminated unexpectedly
            if backend_proc.poll() is not None:
                print("[!] Backend process exited unexpectedly.")
                break
            if frontend_proc.poll() is not None:
                print("[!] Frontend process exited unexpectedly.")
                break
    except KeyboardInterrupt:
        print("\nShutting down MoodMentor services...")
    finally:
        try:
            backend_proc.terminate()
            frontend_proc.terminate()
            backend_proc.wait(timeout=3)
            frontend_proc.wait(timeout=3)
        except Exception:
            backend_proc.kill()
            frontend_proc.kill()
        print("[OK] All services stopped gracefully.")


if __name__ == "__main__":
    main()
