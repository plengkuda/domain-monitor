import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Dashboard - Domain Monitor",
    page_icon="📊",
    layout="wide"
)

# API Configuration
API_BASE_URL = "http://localhost:8000"

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

def main():
    st.title("📊 Dashboard Analytics")
    
    # Get data
    domains = get_domains()
    reports = get_reports()
    
    if not domains and not reports:
        st.warning("Tidak ada data untuk ditampilkan. Pastikan backend API berjalan dan ada data domain.")
        return
    
    # Convert to DataFrames
    domains_df = pd.DataFrame(domains) if domains else pd.DataFrame()
    reports_df = pd.DataFrame(reports) if reports else pd.DataFrame()
    
    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Overview", "🌐 Domain Analysis", "📊 Reports Analysis", "📅 Timeline"])
    
    with tab1:
        st.subheader("📈 System Overview")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if not domains_df.empty:
                # Status distribution pie chart
                status_counts = domains_df['status'].value_counts()
                fig_status = px.pie(
                    values=status_counts.values,
                    names=status_counts.index,
                    title="Distribusi Status Domain",
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                st.plotly_chart(fig_status, use_container_width=True)
            else:
                st.info("Tidak ada data domain untuk chart status.")
        
        with col2:
            if not domains_df.empty:
                # Brand distribution pie chart
                brand_counts = domains_df['brand'].value_counts()
                fig_brand = px.pie(
                    values=brand_counts.values,
                    names=brand_counts.index,
                    title="Distribusi Domain per Brand",
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                st.plotly_chart(fig_brand, use_container_width=True)
            else:
                st.info("Tidak ada data domain untuk chart brand.")
    
    with tab2:
        st.subheader("🌐 Analisis Domain")
        
        if not domains_df.empty:
            # Metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Domain", len(domains_df))
            with col2:
                active_count = len(domains_df[domains_df['status'] == 'aktif'])
                st.metric("Domain Aktif", active_count)
            with col3:
                inactive_count = len(domains_df[domains_df['status'] != 'aktif'])
                st.metric("Domain Tidak Aktif", inactive_count)
            with col4:
                unique_brands = domains_df['brand'].nunique()
                st.metric("Total Brand", unique_brands)
            
            # Category analysis
            col1, col2 = st.columns(2)
            
            with col1:
                if 'kategori' in domains_df.columns:
                    kategori_counts = domains_df['kategori'].value_counts()
                    fig_kategori = px.bar(
                        x=kategori_counts.index,
                        y=kategori_counts.values,
                        title="Distribusi Kategori Domain",
                        labels={'x': 'Kategori', 'y': 'Jumlah Domain'}
                    )
                    st.plotly_chart(fig_kategori, use_container_width=True)
            
            with col2:
                # Domain list by brand
                st.subheader("Domain per Brand")
                for brand in domains_df['brand'].unique():
                    brand_domains = domains_df[domains_df['brand'] == brand]
                    with st.expander(f"{brand} ({len(brand_domains)} domain)"):
                        st.dataframe(brand_domains[['domain', 'status', 'kategori']], use_container_width=True)
            
            # Full domain table
            st.subheader("📋 Semua Domain")
            st.dataframe(domains_df, use_container_width=True)
            
        else:
            st.info("Tidak ada data domain untuk dianalisis.")
    
    with tab3:
        st.subheader("📊 Analisis Laporan (JS Agents)")
        
        if not reports_df.empty:
            # Convert timestamp
            reports_df['reported_at'] = pd.to_datetime(reports_df['reported_at'])
            
            # Metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Laporan", len(reports_df))
            with col2:
                today_reports = len(reports_df[reports_df['reported_at'].dt.date == datetime.now().date()])
                st.metric("Laporan Hari Ini", today_reports)
            with col3:
                unique_domains_reported = reports_df['domain'].nunique()
                st.metric("Domain Dilaporkan", unique_domains_reported)
            with col4:
                brands_reporting = reports_df['brand'].nunique()
                st.metric("Brand Aktif", brands_reporting)
            
            # Reports timeline
            reports_daily = reports_df.groupby(reports_df['reported_at'].dt.date).size().reset_index()
            reports_daily.columns = ['date', 'count']
            
            fig_timeline = px.line(
                reports_daily,
                x='date',
                y='count',
                title="Timeline Laporan Harian",
                markers=True
            )
            st.plotly_chart(fig_timeline, use_container_width=True)
            
            # Recent reports
            st.subheader("📋 Laporan Terbaru")
            recent_reports = reports_df.sort_values('reported_at', ascending=False).head(20)
            recent_reports['reported_at'] = recent_reports['reported_at'].dt.strftime('%Y-%m-%d %H:%M:%S')
            st.dataframe(recent_reports, use_container_width=True)
            
        else:
            st.info("Tidak ada data laporan dari JS agents.")
    
    with tab4:
        st.subheader("📅 Timeline Aktivitas")
        
        # Combined timeline
        timeline_data = []
        
        if not domains_df.empty:
            for _, row in domains_df.iterrows():
                timeline_data.append({
                    'date': pd.to_datetime(row['created_at']).date(),
                    'type': 'Domain Added',
                    'details': f"{row['domain']} ({row['brand']})"
                })
        
        if not reports_df.empty:
            for _, row in reports_df.iterrows():
                timeline_data.append({
                    'date': pd.to_datetime(row['reported_at']).date(),
                    'type': 'Report Received',
                    'details': f"{row['domain']} ({row['brand']})"
                })
        
        if timeline_data:
            timeline_df = pd.DataFrame(timeline_data)
            timeline_df = timeline_df.sort_values('date', ascending=False)
            
            # Activity count by date
            activity_counts = timeline_df.groupby(['date', 'type']).size().reset_index(name='count')
            
            fig_activity = px.bar(
                activity_counts,
                x='date',
                y='count',
                color='type',
                title="Aktivitas Harian",
                labels={'count': 'Jumlah Aktivitas', 'date': 'Tanggal'}
            )
            st.plotly_chart(fig_activity, use_container_width=True)
            
            # Activity list
            st.subheader("📋 Log Aktivitas")
            st.dataframe(timeline_df, use_container_width=True)
            
        else:
            st.info("Tidak ada data aktivitas untuk ditampilkan.")
    
    # Refresh button
    if st.button("🔄 Refresh Data", type="primary"):
        st.rerun()

if __name__ == "__main__":
    main()