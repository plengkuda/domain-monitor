import subprocess
import sys
import time
import os
import signal
from pathlib import Path

def check_requirements():
    """Check if all required packages are installed"""
    print("🔍 Checking requirements...")
    
    required_packages = {
        'streamlit': 'streamlit',
        'fastapi': 'fastapi', 
        'uvicorn': 'uvicorn',
        'pandas': 'pandas',
        'plotly': 'plotly',
        'requests': 'requests',
        'python-dotenv': 'dotenv',  # Import name is different from package name
        'openpyxl': 'openpyxl',
        'python-multipart': 'multipart'  # Import name is different
    }
    
    missing_packages = []
    
    for package_name, import_name in required_packages.items():
        try:
            __import__(import_name)
            print(f"✅ {package_name}")
        except ImportError:
            missing_packages.append(package_name)
            print(f"❌ {package_name}")
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Install with: pip install " + " ".join(missing_packages))
        return False
    
    print("✅ All requirements satisfied!")
    return True

def check_files():
    """Check if all required files exist"""
    print("\n🔍 Checking required files...")
    
    required_files = [
        'main.py',
        'report_api.py',
        'config.py',
        'db.py',
        'utils.py',
        'pages/1_Dashboard.py',
        'pages/2_Data_Domain.py',
        'pages/3_Upload_File.py',
        'pages/4_List_File.py',
        'pages/5_Visualisasi.py'
    ]
    
    missing_files = []
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            missing_files.append(file)
            print(f"❌ {file}")
    
    if missing_files:
        print(f"\n❌ Missing files: {', '.join(missing_files)}")
        return False
    
    print("✅ All required files found!")
    return True

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")
    
    directories = ['pages', 'logs', 'uploads']
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Directory: {directory}")

def start_fastapi_server():
    """Start FastAPI server"""
    print("\n🚀 Starting FastAPI server...")
    
    try:
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "report_api:app", 
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print("✅ FastAPI server starting on http://localhost:8000")
        return process
    
    except Exception as e:
        print(f"❌ Failed to start FastAPI server: {e}")
        return None

def start_streamlit_app():
    """Start Streamlit application"""
    print("\n🚀 Starting Streamlit application...")
    
    try:
        process = subprocess.Popen([
            "streamlit", "run", "main.py", 
            "--server.port", "8501",
            "--server.address", "0.0.0.0",
            "--server.headless", "true"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print("✅ Streamlit app starting on http://localhost:8501")
        return process
    
    except Exception as e:
        print(f"❌ Failed to start Streamlit app: {e}")
        return None

def wait_for_server(url, timeout=30):
    """Wait for server to be ready"""
    import requests
    import time
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return True
        except:
            pass
        time.sleep(1)
    
    return False

def cleanup_processes(processes):
    """Clean up running processes"""
    print("\n🧹 Cleaning up processes...")
    
    for process in processes:
        if process and process.poll() is None:
            try:
                process.terminate()
                process.wait(timeout=5)
                print("✅ Process terminated gracefully")
            except subprocess.TimeoutExpired:
                process.kill()
                print("⚠️ Process force killed")
            except Exception as e:
                print(f"❌ Error terminating process: {e}")

def main():
    """Main execution function"""
    print("🌐 Domain Monitor Dashboard Startup")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Requirements check failed. Please install missing packages.")
        return False
    
    # Check files
    if not check_files():
        print("\n❌ File check failed. Please ensure all required files exist.")
        return False
    
    # Create directories
    create_directories()
    
    # Initialize database
    print("\n💾 Initializing database...")
    try:
        from db import DatabaseManager
        db = DatabaseManager()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False
    
    processes = []
    
    try:
        # Start FastAPI server
        fastapi_process = start_fastapi_server()
        if not fastapi_process:
            return False
        processes.append(fastapi_process)
        
        # Wait for FastAPI to be ready
        print("⏳ Waiting for FastAPI server to be ready...")
        time.sleep(5)
        
        if wait_for_server("http://localhost:8000/health"):
            print("✅ FastAPI server is ready!")
        else:
            print("⚠️ FastAPI server may not be fully ready, but continuing...")
        
        # Start Streamlit app
        streamlit_process = start_streamlit_app()
        if not streamlit_process:
            cleanup_processes(processes)
            return False
        processes.append(streamlit_process)
        
        # Wait for Streamlit to be ready
        print("⏳ Waiting for Streamlit app to be ready...")
        time.sleep(10)
        
        # Success message
        print("\n" + "=" * 50)
        print("🎉 Domain Monitor Dashboard is ready!")
        print("=" * 50)
        print("📊 Streamlit Dashboard: http://localhost:8501")
        print("🔌 FastAPI Backend: http://localhost:8000")
        print("📖 API Documentation: http://localhost:8000/docs")
        print("=" * 50)
        print("\n💡 Tips:")
        print("- Add domains via 'Data Domain' page")
        print("- Upload bulk domains via 'Upload File' page")
        print("- View analytics in 'Visualisasi' page")
        print("- Monitor JS agent reports in 'Dashboard' page")
        print("\n⚠️ Press Ctrl+C to stop all services")
        
        # Keep running until interrupted
        while True:
            # Check if processes are still running
            if any(p.poll() is not None for p in processes):
                print("\n⚠️ One or more processes stopped unexpectedly")
                break
            time.sleep(5)
    
    except KeyboardInterrupt:
        print("\n\n🛑 Shutdown requested by user")
    
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
    
    finally:
        cleanup_processes(processes)
        print("👋 Domain Monitor Dashboard stopped")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)