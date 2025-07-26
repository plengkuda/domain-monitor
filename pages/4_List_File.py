import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import os
from auth import require_auth, show_user_menu, get_current_user, is_admin

st.set_page_config(
    page_title="List File - Domain Monitor",
    page_icon="📋",
    layout="wide"
)

# Check authentication
if not require_auth():
    st.stop()

# API Configuration
API_BASE_URL = "http://localhost:8000"

def get_uploaded_files():
    """Get uploaded files from database (simulated)"""
    # Since we don't have actual file storage, we'll create a mock function
    # In real implementation, this would query the uploaded_files table
    try:
        # Mock data for demonstration
        mock_files = [
            {
                'id': 1,
                'filename': 'domains_batch_1.csv',
                'file_type': 'text/csv',
                'file_size': 2048,
                'uploaded_at': '2025-01-20 10:30:00',
                'status': 'processed',
                'records_imported': 25
            },
            {
                'id': 2,
                'filename': 'slot603_domains.xlsx',
                'file_type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                'file_size': 4096,
                'uploaded_at': '2025-01-19 15:45:00',
                'status': 'processed',
                'records_imported': 50
            },
            {
                'id': 3,
                'filename': 'netpro_update.csv',
                'file_type': 'text/csv',
                'file_size': 1536,
                'uploaded_at': '2025-01-18 09:15:00',
                'status': 'error',
                'records_imported': 0
            }
        ]
        return mock_files
    except Exception as e:
        print(f"Error getting uploaded files: {e}")
        return []

def get_domains():
    """Get all domains from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/domains", timeout=10)
        if response.status_code == 200:
            return response.json()['domains']
        return []
    except:
        return []

def get_reports():
    """Get all reports from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/reports", timeout=10)
        if response.status_code == 200:
            return response.json()['reports']
        return []
    except:
        return []

def export_domains_to_csv(domains):
    """Export domains to CSV format"""
    if not domains:
        return None
    
    df = pd.DataFrame(domains)
    return df.to_csv(index=False)

def export_domains_to_excel(domains):
    """Export domains to Excel format"""
    if not domains:
        return None
    
    import io
    df = pd.DataFrame(domains)
    
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Domains')
    
    return excel_buffer.getvalue()

def format_file_size(size_bytes):
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    
    return f"{s} {size_names[i]}"

def main():
    # Show user menu in sidebar
    show_user_menu()
    
    st.title("📋 Manajemen File")
    
    # User info and permissions
    current_user = get_current_user()
    user_is_admin = is_admin()
    
    if user_is_admin:
        st.success(f"👤 **{current_user}** - Full File Management Access")
    else:
        st.info(f"👤 **{current_user}** - Export Access Only")
        st.warning("⚠️ File upload history and management requires admin access")
    
    # Tabs based on user permission
    if user_is_admin:
        tab1, tab2, tab3 = st.tabs(["📁 File Upload History", "💾 Export Data", "📊 File Statistics"])
    else:
        tab1, tab2 = st.tabs(["💾 Export Data", "📊 Basic Statistics"])
        tab3 = None
    
    if user_is_admin:
        with tab1:
            st.subheader("📁 Riwayat Upload File")
            
            # Get uploaded files
            uploaded_files = get_uploaded_files()
            
            if not uploaded_files:
                st.info("Belum ada file yang diupload.")
                st.markdown("💡 **Tip:** Upload file domain di halaman 'Upload File' untuk melihat riwayat di sini.")
            else:
                # Display files
                for file_info in uploaded_files:
                    with st.expander(f"📄 {file_info['filename']} - {file_info['status'].upper()}"):
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.write(f"**Nama File:** {file_info['filename']}")
                            st.write(f"**Tipe:** {file_info['file_type']}")
                            st.write(f"**Ukuran:** {format_file_size(file_info['file_size'])}")
                            st.write(f"**Upload:** {file_info['uploaded_at']}")
                            st.write(f"**Status:** {file_info['status']}")
                            if file_info['status'] == 'processed':
                                st.write(f"**Records Imported:** {file_info['records_imported']}")
                        
                        with col2:
                            if file_info['status'] == 'processed':
                                st.success("✅ Berhasil Diproses")
                            elif file_info['status'] == 'error':
                                st.error("❌ Error Processing")
                            else:
                                st.warning("⏳ Processing")
                            
                            # Action buttons (simulated)
                            if st.button(f"🗑️ Hapus", key=f"delete_{file_info['id']}"):
                                st.success(f"File {file_info['filename']} akan dihapus (simulasi)")
    
    with (tab2 if user_is_admin else tab1):
        st.subheader("💾 Export Data")
        
        # Get current data
        domains = get_domains()
        reports = get_reports()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🌐 Export Domain Data")
            
            if domains:
                st.info(f"Total domains: {len(domains)}")
                
                # Filter options
                df = pd.DataFrame(domains)
                
                # Brand filter
                selected_brands = st.multiselect(
                    "Filter Brand",
                    options=df['brand'].unique(),
                    default=df['brand'].unique(),
                    key="export_brand_filter"
                )
                
                # Status filter
                selected_status = st.multiselect(
                    "Filter Status",
                    options=df['status'].unique(),
                    default=df['status'].unique(),
                    key="export_status_filter"
                )
                
                # Apply filters
                filtered_df = df[
                    (df['brand'].isin(selected_brands)) & 
                    (df['status'].isin(selected_status))
                ]
                
                st.write(f"Data yang akan diekspor: {len(filtered_df)} domain")
                
                # Export buttons
                if len(filtered_df) > 0:
                    filtered_domains = filtered_df.to_dict('records')
                    
                    # CSV Export
                    csv_data = export_domains_to_csv(filtered_domains)
                    if csv_data:
                        st.download_button(
                            label="📄 Download CSV",
                            data=csv_data,
                            file_name=f"domains_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                    
                    # Excel Export
                    excel_data = export_domains_to_excel(filtered_domains)
                    if excel_data:
                        st.download_button(
                            label="📊 Download Excel",
                            data=excel_data,
                            file_name=f"domains_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                else:
                    st.warning("Tidak ada data untuk diekspor dengan filter yang dipilih.")
            else:
                st.warning("Tidak ada data domain untuk diekspor.")
        
        with col2:
            st.markdown("#### 📊 Export Report Data")
            
            if reports:
                st.info(f"Total reports: {len(reports)}")
                
                reports_df = pd.DataFrame(reports)
                
                # Date filter
                if 'reported_at' in reports_df.columns:
                    reports_df['reported_at'] = pd.to_datetime(reports_df['reported_at'])
                    
                    min_date = reports_df['reported_at'].min().date()
                    max_date = reports_df['reported_at'].max().date()
                    
                    date_range = st.date_input(
                        "Filter Tanggal Laporan",
                        value=(min_date, max_date),
                        min_value=min_date,
                        max_value=max_date,
                        key="export_date_filter"
                    )
                    
                    if len(date_range) == 2:
                        start_date, end_date = date_range
                        filtered_reports = reports_df[
                            (reports_df['reported_at'].dt.date >= start_date) &
                            (reports_df['reported_at'].dt.date <= end_date)
                        ]
                    else:
                        filtered_reports = reports_df
                    
                    st.write(f"Data yang akan diekspor: {len(filtered_reports)} laporan")
                    
                    # Export buttons
                    if len(filtered_reports) > 0:
                        # CSV Export
                        csv_data = filtered_reports.to_csv(index=False)
                        st.download_button(
                            label="📄 Download Reports CSV",
                            data=csv_data,
                            file_name=f"reports_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                        
                        # Excel Export
                        import io
                        excel_buffer = io.BytesIO()
                        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                            filtered_reports.to_excel(writer, index=False, sheet_name='Reports')
                        
                        st.download_button(
                            label="📊 Download Reports Excel",
                            data=excel_buffer.getvalue(),
                            file_name=f"reports_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                    else:
                        st.warning("Tidak ada data laporan untuk diekspor.")
            else:
                st.warning("Tidak ada data laporan untuk diekspor.")
    
    if user_is_admin and tab3:
        with tab3:
            st.subheader("📊 Statistik File & Data")
            
            # File statistics
            uploaded_files = get_uploaded_files()
            domains = get_domains()
            reports = get_reports()
            
            # Metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total File Upload", len(uploaded_files))
            
            with col2:
                processed_files = len([f for f in uploaded_files if f['status'] == 'processed'])
                st.metric("File Berhasil", processed_files)
            
            with col3:
                st.metric("Total Domain", len(domains))
            
            with col4:
                st.metric("Total Reports", len(reports))
            
            # File size analysis
            if uploaded_files:
                st.subheader("📈 Analisis Ukuran File")
                
                file_df = pd.DataFrame(uploaded_files)
                
                # File size distribution
                col1, col2 = st.columns(2)
                
                with col1:
                    # File size chart
                    import plotly.express as px
                    
                    fig_size = px.bar(
                        file_df,
                        x='filename',
                        y='file_size',
                        title="Ukuran File Upload",
                        labels={'file_size': 'Ukuran (bytes)', 'filename': 'Nama File'}
                    )
                    fig_size.update_layout(xaxis_tickangle=45)
                    st.plotly_chart(fig_size, use_container_width=True)
                
                with col2:
                    # File status pie chart
                    status_counts = file_df['status'].value_counts()
                    fig_status = px.pie(
                        values=status_counts.values,
                        names=status_counts.index,
                        title="Status Processing File"
                    )
                    st.plotly_chart(fig_status, use_container_width=True)
            
            # Data growth timeline
            if domains:
                st.subheader("📅 Timeline Pertumbuhan Data")
                
                domains_df = pd.DataFrame(domains)
                if 'created_at' in domains_df.columns:
                    domains_df['created_at'] = pd.to_datetime(domains_df['created_at'])
                    domains_df['date'] = domains_df['created_at'].dt.date
                    
                    daily_counts = domains_df.groupby('date').size().reset_index(name='count')
                    daily_counts['cumulative'] = daily_counts['count'].cumsum()
                    
                    import plotly.express as px
                    
                    fig_timeline = px.line(
                        daily_counts,
                        x='date',
                        y='cumulative',
                        title="Pertumbuhan Kumulatif Domain",
                        markers=True,
                        labels={'cumulative': 'Total Domain', 'date': 'Tanggal'}
                    )
                    st.plotly_chart(fig_timeline, use_container_width=True)
    elif not user_is_admin:
        with tab2:
            st.subheader("📊 Basic Statistics")
            
            domains = get_domains()
            reports = get_reports()
            
            # Basic metrics for non-admin users
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Total Domain", len(domains))
            with col2:
                st.metric("Total Reports", len(reports))
            
            if domains:
                # Simple domain status chart
                domains_df = pd.DataFrame(domains)
                status_counts = domains_df['status'].value_counts()
                
                import plotly.express as px
                fig = px.pie(
                    values=status_counts.values,
                    names=status_counts.index,
                    title="Domain Status Distribution"
                )
                st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()