import subprocess
import sys

# Daftar dependencies
REQUIREMENTS = [
    "streamlit==1.28.0",
    "fastapi==0.104.1",
    "uvicorn[standard]==0.24.0",
    "python-multipart==0.0.6",
    "pandas==2.1.3",
    "plotly==5.17.0",
    "requests==2.31.0",
    "python-dotenv==1.0.0",
    "rich==10.0.0",
    "markdown-it-py==2.1.0",
    "mdurl==0.1.0",
    "pygments==2.7.4",
    "openpyxl==3.1.2"
]

def install(package):
    """Install a Python package via pip."""
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def main():
    print("🔍 Checking and installing missing packages...")
    for pkg in REQUIREMENTS:
        try:
            __import__(pkg.split("==")[0].split("[")[0])  # import to check if installed
            print(f"✅ {pkg} is already installed")
        except ImportError:
            print(f"⚠️  {pkg} is missing. Installing...")
            install(pkg)
    print("\n🎉 All requirements are installed!")

if __name__ == "__main__":
    main()