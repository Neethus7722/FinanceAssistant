"""
Finance Assistant - Unified Portal Launcher
Run this to start the complete Finance Analytics Portal
"""

import subprocess
import sys
import time
import webbrowser
from pathlib import Path

def check_backend_health():
    """Check if backend is running"""
    try:
        import requests
        response = requests.get("http://127.0.0.1:8001/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def start_backend():
    """Start the backend server"""
    print("🚀 Starting Finance Assistant Backend...")
    backend_process = subprocess.Popen([
        sys.executable, "-m", "uvicorn", 
        "backend.main:app", 
        "--reload", "--port", "8001"
    ], cwd=Path(__file__).parent)
    
    # Wait for backend to start
    for i in range(30):  # Wait up to 30 seconds
        if check_backend_health():
            print("✅ Backend is running on http://127.0.0.1:8001")
            return backend_process
        time.sleep(1)
        print(f"⏳ Waiting for backend to start... ({i+1}/30)")
    
    print("❌ Backend failed to start within 30 seconds")
    return backend_process

def start_frontend():
    """Start the unified frontend portal"""
    print("🎨 Starting Finance Analytics Portal...")
    frontend_process = subprocess.Popen([
        sys.executable, "-m", "streamlit", "run", 
        "frontend/app.py", 
        "--server.port", "8500"
    ], cwd=Path(__file__).parent)
    
    # Wait a moment then open browser
    time.sleep(3)
    print("✅ Finance Analytics Portal is starting on http://localhost:8500")
    
    # Open browser
    try:
        webbrowser.open("http://localhost:8500")
        print("🌐 Opening portal in your default browser...")
    except:
        print("🌐 Please open http://localhost:8500 in your browser")
    
    return frontend_process

def main():
    print("=" * 60)
    print("🏦 FINANCE ANALYTICS PORTAL LAUNCHER")
    print("=" * 60)
    print()
    
    # Check if backend is already running
    if check_backend_health():
        print("✅ Backend is already running")
        backend_process = None
    else:
        backend_process = start_backend()
    
    # Start frontend
    frontend_process = start_frontend()
    
    print()
    print("=" * 60)
    print("🎯 FINANCE ANALYTICS PORTAL IS READY!")
    print("=" * 60)
    print("📊 Backend API: http://127.0.0.1:8001")
    print("🏦 Analytics Portal: http://localhost:8500")
    print()
    print("Features available:")
    print("• 📈 Executive Dashboard with KPIs")
    print("• 💰 Revenue Analytics & Trends")
    print("• 🏢 Client Performance Analysis")
    print("• 📊 Profitability Deep Dive")
    print("• 🤖 AI-Powered Financial Assistant")
    print("• 🎯 Strategic Business Insights")
    print()
    print("Press Ctrl+C to stop all services")
    print("=" * 60)
    
    try:
        # Keep running until user interrupts
        if backend_process:
            backend_process.wait()
        else:
            frontend_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Finance Analytics Portal...")
        if backend_process:
            backend_process.terminate()
        frontend_process.terminate()
        print("✅ All services stopped")

if __name__ == "__main__":
    main()
