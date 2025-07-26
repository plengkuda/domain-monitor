import streamlit as st
import requests
from datetime import datetime
import pandas as pd
from auth import require_auth, show_user_menu

# Page config
st.set_page_config(
    page_title="Domain Monitor Dashboard",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Check authentication
if not require_auth():
    st.stop()

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 0.75rem;
        border-radius: 0.375rem;
        border: 1px solid #c3e6cb;
    }
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 0.75rem;
        border-radius: 0.375rem;
        border: 1px solid #f5c6cb;
    }
</style>
""", unsafe_allow_html=True)

# API Configuration
API_BASE_URL = "http://localhost:8000"

def check_api_connection():
    """Check if FastAPI backend is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def get_dashboard_stats():
    """Get dashboard statistics from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/dashboard/stats", timeout=10)
        if response.status_code == 200:
            return response.json()['stats']
        return None
    except:
        return None

def main():
    # Show user menu in sidebar
    show_user_menu()
    
    # Header
    st.markdown('<h1 class="main-header">🌐 Domain Monitor Dashboard</h1>', unsafe_allow_html=True)
    
    # Check API connection
    if not check_api_connection():
        st.error("⚠️ Backend API tidak terhubung. Pastikan FastAPI server berjalan di port 8000.")
        st.info("Jalankan perintah: `uvicorn report_api:app --port 8000`")
        return
    
    # Success message for API connection
    st.success("✅ Backend API terhubung")
    
    # Get dashboard stats
    stats = get_dashboard_stats()
    
    if stats:
        # Metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Total Domain",
                value=stats['total_domains'],
                delta=None
            )
        
        with col2:
            st.metric(
                label="Domain Aktif",
                value=stats['active_domains'],
                delta=None
            )
        
        with col3:
            st.metric(
                label="Domain Tidak Aktif",
                value=stats['inactive_domains'],
                delta=None
            )
        
        with col4:
            st.metric(
                label="Laporan Hari Ini",
                value=stats['today_reports'],
                delta=None
            )
        
        # Brand distribution
        if stats['brand_stats']:
            st.subheader("📊 Distribusi per Brand")
            brand_df = pd.DataFrame(list(stats['brand_stats'].items()), columns=['Brand', 'Jumlah Domain'])
            
            col1, col2 = st.columns([2, 1])
            with col1:
                st.bar_chart(brand_df.set_index('Brand'))
            with col2:
                st.dataframe(brand_df, use_container_width=True)
    
    else:
        st.warning("Tidak dapat mengambil data statistik dari server.")
    
    # Quick actions
    st.subheader("⚡ Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("➕ Tambah Domain Baru", use_container_width=True):
            st.switch_page("pages/2_Data_Domain.py")
    
    with col2:
        if st.button("📁 Upload File Domain", use_container_width=True):
            st.switch_page("pages/3_Upload_File.py")
    
    with col3:
        if st.button("📊 Lihat Visualisasi", use_container_width=True):
            st.switch_page("pages/5_Visualisasi.py")
    
    # Recent activity
    st.subheader("📋 Aktivitas Terbaru")
    try:
        response = requests.get(f"{API_BASE_URL}/api/domains", timeout=10)
        if response.status_code == 200:
            domains_data = response.json()
            if domains_data['domains']:
                df = pd.DataFrame(domains_data['domains'])
                # Show only recent 10 entries
                recent_df = df.head(10)[['domain', 'brand', 'status', 'created_at']]
                recent_df['created_at'] = pd.to_datetime(recent_df['created_at']).dt.strftime('%Y-%m-%d %H:%M')
                st.dataframe(recent_df, use_container_width=True)
            else:
                st.info("Belum ada data domain.")
        else:
            st.error("Gagal mengambil data domain.")
    except Exception as e:
        st.error(f"Error: {str(e)}")
    
    # Footer
    st.markdown("---")
    st.markdown(
        f"<div style='text-align: center; color: #666;'>"
        f"Domain Monitor Dashboard | Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        f"</div>", 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()