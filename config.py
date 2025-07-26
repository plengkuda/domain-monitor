import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
API_KEYS = {
    "slot603": os.getenv("SLOT603_API_KEY", "SLOT603-KEY"),
    "netpro": os.getenv("NETPRO_API_KEY", "NETPRO-KEY")
}

# Database Configuration
DATABASE_PATH = "domain_monitor.db"

# Server Configuration
FASTAPI_HOST = "0.0.0.0"
FASTAPI_PORT = 8000
STREAMLIT_PORT = 8501

# External API
EXTERNAL_API_URL = "https://www.dewipemikat.com/api/report"

# Security
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALLOWED_ORIGINS = ["http://localhost:8501", "http://127.0.0.1:8501"]