import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date

st.set_page_config(
    page_title="Data Domain - Domain Monitor",
    page_icon="🌐",
    layout="wide"
)

# API Configuration
API_BASE_URL = "http://localhost:8000"

def add_domain(domain_data):
    """Add new domain via API"""
    try:
        response = requests.post(f"{API_BASE_URL}/api/submit-domain", json=domain_data, timeout=10)
        return response.status_code == 200, response.json()
    except Exception as e:
        return False, {"detail": str(e)}

def get_domains():
    """Get all domains from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/domains", timeout=10)
        if response.status_code == 200:
            return response.json()['domains']
        return []
    except:
        return []

def update_domain(domain_id, update_data):
    """Update domain via API"""
    try:
        response = requests.put(f"{API_BASE_URL}/api/domains/{domain_id}", json=update_data, timeout=10)
        return response.status_code == 200, response.json()
    except Exception as e:
        return False, {"detail": str(e)}

def delete_domain(domain_id):
    """Delete domain via API"""
    try:
        response = requests.delete(f"{API_BASE_URL}/api/domains/{domain_id}", timeout=10)
        return response.status_code == 200, response.json()
    except Exception as e:
        return False, {"detail": str(e)}

def check_domain_status(domain):
    """Check domain status via API"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/domain-check/{domain}", timeout=15)
        if response.status_code == 200:
            return response.json()['status_info']
        return None
    except:
        return None

def main():
    st.title("🌐 Manajemen Data Domain")
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["➕ Tambah Domain", "📋 Daftar Domain", "🔍 Cek Status Domain"])
    
    with tab1:
        st.subheader("➕ Tambah Domain Baru")
        
        with st.form("add_domain_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                domain = st.text_input("Domain *", placeholder="example.com")
                brand = st.selectbox("Brand *", ["slot603", "netpro"])
                status = st.selectbox("Status", ["aktif", "tidak aktif"], index=0)
            
            with col2:
                kategori = st.selectbox("Kategori", ["normal", "premium", "blocked"], index=0)
                expired_date = st.date_input("Tanggal Kadaluarsa", value=None)
                catatan = st.text_area("Catatan", placeholder="Catatan tambahan...")
            
            submitted = st.form_submit_button("💾 Simpan Domain", type="primary")
            
            if submitted:
                if not domain or not brand:
                    st.error("Domain dan Brand wajib diisi!")
                else:
                    # Prepare data
                    domain_data = {
                        "domain": domain.strip().lower(),
                        "brand": brand,
                        "status": status,
                        "kategori": kategori,
                        "expired": expired_date.isoformat() if expired_date else None,
                        "catatan": catatan if catatan else None
                    }
                    
                    # Add domain
                    success, response = add_domain(domain_data)
                    
                    if success:
                        st.success(f"✅ Domain {domain} berhasil ditambahkan!")
                        st.rerun()
                    else:
                        st.error(f"❌ Error: {response.get('detail', 'Unknown error')}")
    
    with tab2:
        st.subheader("📋 Daftar Semua Domain")
        
        # Get domains
        domains = get_domains()
        
        if not domains:
            st.info("Belum ada data domain. Tambahkan domain baru di tab pertama.")
            return
        
        # Convert to DataFrame
        df = pd.DataFrame(domains)
        
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            brand_filter = st.selectbox("Filter Brand", ["Semua"] + list(df['brand'].unique()))
        with col2:
            status_filter = st.selectbox("Filter Status", ["Semua"] + list(df['status'].unique()))
        with col3:
            search_domain = st.text_input("Cari Domain", placeholder="Ketik domain...")
        
        # Apply filters
        filtered_df = df.copy()
        
        if brand_filter != "Semua":
            filtered_df = filtered_df[filtered_df['brand'] == brand_filter]
        
        if status_filter != "Semua":
            filtered_df = filtered_df[filtered_df['status'] == status_filter]
        
        if search_domain:
            filtered_df = filtered_df[filtered_df['domain'].str.contains(search_domain, case=False, na=False)]
        
        # Display results
        st.write(f"Menampilkan {len(filtered_df)} dari {len(df)} domain")
        
        # Action buttons
        col1, col2 = st.columns([1, 5])
        with col1:
            if st.button("🔄 Refresh"):
                st.rerun()
        
        # Display table with actions
        for idx, row in filtered_df.iterrows():
            with st.expander(f"🌐 {row['domain']} ({row['brand']}) - {row['status']}"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**ID:** {row['id']}")
                    st.write(f"**Domain:** {row['domain']}")
                    st.write(f"**Brand:** {row['brand']}")
                    st.write(f"**Status:** {row['status']}")
                    st.write(f"**Kategori:** {row['kategori']}")
                    if row['expired_date']:
                        st.write(f"**Expired:** {row['expired_date']}")
                    if row['catatan']:
                        st.write(f"**Catatan:** {row['catatan']}")
                    st.write(f"**Dibuat:** {row['created_at']}")
                
                with col2:
                    # Edit form
                    with st.form(f"edit_form_{row['id']}"):
                        new_status = st.selectbox("Status", ["aktif", "tidak aktif"], 
                                                index=0 if row['status'] == 'aktif' else 1,
                                                key=f"status_{row['id']}")
                        new_kategori = st.selectbox("Kategori", ["normal", "premium", "blocked"],
                                                  index=["normal", "premium", "blocked"].index(row['kategori']) if row['kategori'] in ["normal", "premium", "blocked"] else 0,
                                                  key=f"kategori_{row['id']}")
                        new_catatan = st.text_area("Catatan", value=row['catatan'] or "", 
                                                 key=f"catatan_{row['id']}")
                        
                        col_save, col_delete = st.columns(2)
                        
                        with col_save:
                            if st.form_submit_button("💾 Update", type="primary"):
                                update_data = {
                                    "status": new_status,
                                    "kategori": new_kategori,
                                    "catatan": new_catatan if new_catatan else None
                                }
                                
                                success, response = update_domain(row['id'], update_data)
                                
                                if success:
                                    st.success("✅ Domain berhasil diupdate!")
                                    st.rerun()
                                else:
                                    st.error(f"❌ Error: {response.get('detail', 'Unknown error')}")
                        
                        with col_delete:
                            if st.form_submit_button("🗑️ Hapus", type="secondary"):
                                success, response = delete_domain(row['id'])
                                
                                if success:
                                    st.success("✅ Domain berhasil dihapus!")
                                    st.rerun()
                                else:
                                    st.error(f"❌ Error: {response.get('detail', 'Unknown error')}")
    
    with tab3:
        st.subheader("🔍 Cek Status Domain")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            check_domain = st.text_input("Domain yang akan dicek", placeholder="example.com")
        
        with col2:
            st.write("")  # spacing
            check_button = st.button("🔍 Cek Status", type="primary")
        
        if check_button and check_domain:
            with st.spinner("Mengecek status domain..."):
                status_info = check_domain_status(check_domain)
                
                if status_info:
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if status_info['accessible']:
                            st.success(f"✅ Domain {check_domain} dapat diakses")
                        else:
                            st.error(f"❌ Domain {check_domain} tidak dapat diakses")
                    
                    with col2:
                        st.info(f"Status: {status_info['status']}")
                    
                    with col3:
                        if status_info['status_code']:
                            st.info(f"HTTP Code: {status_info['status_code']}")
                        else:
                            st.warning("No HTTP response")
                
                else:
                    st.error("Gagal mengecek status domain. Periksa koneksi internet.")

if __name__ == "__main__":
    main()