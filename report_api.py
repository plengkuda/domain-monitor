from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, Dict, Any
import json
from datetime import datetime

from config import ALLOWED_ORIGINS, API_KEYS
from db import DatabaseManager
from utils import APIUtils, DomainUtils

app = FastAPI(
    title="Domain Monitor API",
    description="API for domain monitoring system",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Initialize database
db = DatabaseManager()
security = HTTPBearer(auto_error=False)

# Pydantic models
class DomainSubmission(BaseModel):
    domain: str
    brand: str
    status: Optional[str] = "aktif"
    kategori: Optional[str] = "normal"
    expired: Optional[str] = None
    catatan: Optional[str] = None

class ReportSubmission(BaseModel):
    domain: str
    brand: str
    status: str
    kategori: str
    expired: str
    catatan: str
    api_key: str

class DomainUpdate(BaseModel):
    domain: Optional[str] = None
    brand: Optional[str] = None
    status: Optional[str] = None
    kategori: Optional[str] = None
    expired_date: Optional[str] = None
    catatan: Optional[str] = None

# API Routes
@app.get("/")
async def root():
    return {
        "message": "Domain Monitor API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/submit-domain")
async def submit_domain(submission: DomainSubmission):
    """Submit domain from internal sources (Streamlit)"""
    try:
        # Validate domain format
        if not DomainUtils.validate_domain(submission.domain):
            raise HTTPException(status_code=400, detail="Invalid domain format")
        
        # Validate brand
        if submission.brand not in API_KEYS:
            raise HTTPException(status_code=400, detail="Invalid brand")
        
        # Add to database
        success = db.add_domain(
            domain=submission.domain,
            brand=submission.brand,
            status=submission.status,
            kategori=submission.kategori,
            expired_date=submission.expired,
            catatan=submission.catatan
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to save domain")
        
        return {
            "message": "Domain berhasil ditambahkan",
            "domain": submission.domain,
            "brand": submission.brand,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/api/report")
async def receive_report(report: ReportSubmission):
    """Receive report from JS agents"""
    try:
        # Validate API key
        if not APIUtils.validate_api_key(report.api_key, report.brand):
            raise HTTPException(status_code=401, detail="Invalid API key")
        
        # Validate domain format
        if not DomainUtils.validate_domain(report.domain):
            raise HTTPException(status_code=400, detail="Invalid domain format")
        
        # Add report to database
        success = db.add_report(
            domain=report.domain,
            brand=report.brand,
            status=report.status,
            kategori=report.kategori,
            expired_date=report.expired,
            catatan=report.catatan,
            api_key=report.api_key
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to save report")
        
        return {
            "message": "Report received successfully",
            "domain": report.domain,
            "brand": report.brand,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/domains")
async def get_domains():
    """Get all domains"""
    try:
        df = db.get_domains()
        if df.empty:
            return {"domains": [], "count": 0}
        
        domains = df.to_dict('records')
        return {
            "domains": domains,
            "count": len(domains),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/reports")
async def get_reports():
    """Get all reports from JS agents"""
    try:
        df = db.get_reports()
        if df.empty:
            return {"reports": [], "count": 0}
        
        reports = df.to_dict('records')
        return {
            "reports": reports,
            "count": len(reports),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.put("/api/domains/{domain_id}")
async def update_domain(domain_id: int, update_data: DomainUpdate):
    """Update domain information"""
    try:
        # Filter out None values
        update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
        
        if not update_dict:
            raise HTTPException(status_code=400, detail="No data to update")
        
        success = db.update_domain(domain_id, **update_dict)
        
        if not success:
            raise HTTPException(status_code=404, detail="Domain not found or update failed")
        
        return {
            "message": "Domain updated successfully",
            "domain_id": domain_id,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.delete("/api/domains/{domain_id}")
async def delete_domain(domain_id: int):
    """Delete domain"""
    try:
        success = db.delete_domain(domain_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Domain not found")
        
        return {
            "message": "Domain deleted successfully",
            "domain_id": domain_id,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/dashboard/stats")
async def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        stats = db.get_dashboard_stats()
        return {
            "stats": stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/domain-check/{domain}")
async def check_domain_status(domain: str):
    """Check domain accessibility status"""
    try:
        if not DomainUtils.validate_domain(domain):
            raise HTTPException(status_code=400, detail="Invalid domain format")
        
        status_info = DomainUtils.check_domain_status(domain)
        
        return {
            "domain": domain,
            "status_info": status_info,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    from config import FASTAPI_HOST, FASTAPI_PORT
    
    uvicorn.run(app, host=FASTAPI_HOST, port=FASTAPI_PORT)