import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from auth import require_auth, show_user_menu, get_current_user, is_admin

st.set_page_config(
    page_title="Visualisasi - Domain Monitor",
    page_icon="📊",
    layout="wide"
)

# Check authentication
if not require_auth():
    st.stop()

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

def create_status_pie_chart(domains_df):
    """Create domain status pie chart"""
    if domains_df.empty:
        return None
    
    status_counts = domains_df['status'].value_counts()
    
    fig = px.pie(
        values=status_counts.values,
        names=status_counts.index,
        title="📊 Distribusi Status Domain",
        color_discrete_sequence=px.colors.qualitative.Set3,
        hole=0.4
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        textfont_size=12
    )
    
    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2),
        margin=dict(t=50, b=80, l=50, r=50)
    )
    
    return fig

def create_brand_distribution_chart(domains_df):
    """Create brand distribution chart"""
    if domains_df.empty:
        return None
    
    brand_counts = domains_df['brand'].value_counts()
    
    fig = px.bar(
        x=brand_counts.index,
        y=brand_counts.values,
        title="🏢 Distribusi Domain per Brand",
        labels={'x': 'Brand', 'y': 'Jumlah Domain'},
        color=brand_counts.values,
        color_continuous_scale='viridis'
    )
    
    fig.update_layout(
        showlegend=False,
        xaxis_title="Brand",
        yaxis_title="Jumlah Domain"
    )
    
    return fig

def create_category_chart(domains_df):
    """Create category distribution chart"""
    if domains_df.empty or 'kategori' not in domains_df.columns:
        return None
    
    category_counts = domains_df['kategori'].value_counts()
    
    fig = px.donut(
        values=category_counts.values,
        names=category_counts.index,
        title="📂 Distribusi Kategori Domain",
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    
    return fig

def create_timeline_chart(domains_df, reports_df):
    """Create timeline chart showing domain additions and reports"""
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Domain Registration Timeline', 'Reports Timeline'),
        vertical_spacing=0.1
    )
    
    # Domain timeline
    if not domains_df.empty and 'created_at' in domains_df.columns:
        domains_df['created_date'] = pd.to_datetime(domains_df['created_at']).dt.date
        domain_daily = domains_df.groupby('created_date').size().reset_index(name='count')
        
        fig.add_trace(
            go.Scatter(
                x=domain_daily['created_date'],
                y=domain_daily['count'],
                mode='lines+markers',
                name='Domains Added',
                line=dict(color='blue', width=2),
                marker=dict(size=6)
            ),
            row=1, col=1
        )
    
    # Reports timeline
    if not reports_df.empty and 'reported_at' in reports_df.columns:
        reports_df['reported_date'] = pd.to_datetime(reports_df['reported_at']).dt.date
        reports_daily = reports_df.groupby('reported_date').size().reset_index(name='count')
        
        fig.add_trace(
            go.Scatter(
                x=reports_daily['reported_date'],
                y=reports_daily['count'],
                mode='lines+markers',
                name='Reports Received',
                line=dict(color='green', width=2),
                marker=dict(size=6)
            ),
            row=2, col=1
        )
    
    fig.update_layout(
        title="📈 Timeline Aktivitas",
        height=600,
        showlegend=True
    )
    
    return fig

def create_heatmap_chart(reports_df):
    """Create heatmap of domain activity"""
    if reports_df.empty:
        return None
    
    # Create hour-day heatmap
    reports_df['reported_at'] = pd.to_datetime(reports_df['reported_at'])
    reports_df['hour'] = reports_df['reported_at'].dt.hour
    reports_df['day_name'] = reports_df['reported_at'].dt.day_name()
    
    # Create pivot table
    heatmap_data = reports_df.groupby(['day_name', 'hour']).size().reset_index(name='count')
    heatmap_pivot = heatmap_data.pivot(index='day_name', columns='hour', values='count').fillna(0)
    
    # Reorder days
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    heatmap_pivot = heatmap_pivot.reindex(day_order)
    
    fig = px.imshow(
        heatmap_pivot,
        title="🔥 Heatmap Aktivitas Laporan (Jam vs Hari)",
        labels=dict(x="Jam", y="Hari", color="Jumlah Laporan"),
        color_continuous_scale='YlOrRd'
    )
    
    return fig

def create_domain_growth_chart(domains_df):
    """Create cumulative domain growth chart"""
    if domains_df.empty:
        return None
    
    domains_df['created_date'] = pd.to_datetime(domains_df['created_at']).dt.date
    daily_counts = domains_df.groupby('created_date').size().reset_index(name='daily_count')
    daily_counts['cumulative'] = daily_counts['daily_count'].cumsum()
    
    fig = go.Figure()
    
    # Add cumulative line
    fig.add_trace(
        go.Scatter(
            x=daily_counts['created_date'],
            y=daily_counts['cumulative'],
            mode='lines',
            name='Total Kumulatif',
            line=dict(color='blue', width=3),
            fill='tonexty'
        )
    )
    
    # Add daily bars
    fig.add_trace(
        go.Bar(
            x=daily_counts['created_date'],
            y=daily_counts['daily_count'],
            name='Penambahan Harian',
            marker_color='lightblue',
            opacity=0.7,
            yaxis='y2'
        )
    )
    
    fig.update_layout(
        title="📈 Pertumbuhan Domain dari Waktu ke Waktu",
        xaxis_title="Tanggal",
        yaxis=dict(title="Total Kumulatif", side="left"),
        yaxis2=dict(title="Penambahan Harian", side="right", overlaying="y"),
        legend=dict(x=0.02, y=0.98),
        hovermode='x unified'
    )
    
    return fig

def create_brand_comparison_chart(domains_df, reports_df):
    """Create brand comparison chart"""
    if domains_df.empty:
        return None
    
    # Domain counts by brand
    domain_brand_counts = domains_df['brand'].value_counts()
    
    # Report counts by brand
    report_brand_counts = reports_df['brand'].value_counts() if not reports_df.empty else pd.Series()
    
    brands = list(set(domain_brand_counts.index.tolist() + report_brand_counts.index.tolist()))
    
    fig = go.Figure()
    
    # Add domain counts
    fig.add_trace(
        go.Bar(
            name='Total Domain',
            x=brands,
            y=[domain_brand_counts.get(brand, 0) for brand in brands],
            marker_color='lightblue'
        )
    )
    
    # Add report counts
    fig.add_trace(
        go.Bar(
            name='Total Laporan',
            x=brands,
            y=[report_brand_counts.get(brand, 0) for brand in brands],
            marker_color='lightcoral'
        )
    )
    
    fig.update_layout(
        title="🔄 Perbandingan Domain vs Laporan per Brand",
        xaxis_title="Brand",
        yaxis_title="Jumlah",
        barmode='group'
    )
    
    return fig

def main():
    # Show user menu in sidebar
    show_user_menu()
    
    st.title("📊 Visualisasi Data Domain")
    
    # User info and permissions
    current_user = get_current_user()
    user_is_admin = is_admin()
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.info(f"👤 User: **{current_user}** | Role: **{'Admin' if user_is_admin else 'User'}**")
    with col2:
        if user_is_admin:
            st.success("🔓 Full Access")
        else:
            st.warning("👁️ View Only")
    
    # Get data
    domains = get_domains()
    reports = get_reports()
    
    if not domains and not reports:
        st.warning("⚠️ Tidak ada data untuk divisualisasikan. Pastikan backend API berjalan dan ada data domain.")
        return
    
    # Convert to DataFrames
    domains_df = pd.DataFrame(domains) if domains else pd.DataFrame()
    reports_df = pd.DataFrame(reports) if reports else pd.DataFrame()
    
    # Sidebar filters
    st.sidebar.header("🎛️ Filter Data")
    
    # Show current user in sidebar
    st.sidebar.markdown(f"**Current User:** {current_user}")
    st.sidebar.markdown(f"**Access Level:** {'Full' if user_is_admin else 'Read-Only'}")
    st.sidebar.markdown("---")
    
    # Date range filter
    if not domains_df.empty and 'created_at' in domains_df.columns:
        domains_df['created_at'] = pd.to_datetime(domains_df['created_at'])
        min_date = domains_df['created_at'].min().date()
        max_date = domains_df['created_at'].max().date()
        
        date_range = st.sidebar.date_input(
            "Rentang Tanggal Domain",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        
        if len(date_range) == 2:
            start_date, end_date = date_range
            domains_df = domains_df[
                (domains_df['created_at'].dt.date >= start_date) &
                (domains_df['created_at'].dt.date <= end_date)
            ]
    
    # Brand filter
    if not domains_df.empty:
        all_brands = ['Semua'] + list(domains_df['brand'].unique())
        selected_brand = st.sidebar.selectbox("Filter Brand", all_brands)
        
        if selected_brand != 'Semua':
            domains_df = domains_df[domains_df['brand'] == selected_brand]
            if not reports_df.empty:
                reports_df = reports_df[reports_df['brand'] == selected_brand]
    
    # Status filter
    if not domains_df.empty:
        all_statuses = ['Semua'] + list(domains_df['status'].unique())
        selected_status = st.sidebar.selectbox("Filter Status", all_statuses)
        
        if selected_status != 'Semua':
            domains_df = domains_df[domains_df['status'] == selected_status]
    
    # Display filtered data info
    if not domains_df.empty or not reports_df.empty:
        st.sidebar.markdown("---")
        st.sidebar.markdown("**📊 Data Terfilter:**")
        st.sidebar.metric("Total Domain", len(domains_df))
        st.sidebar.metric("Total Laporan", len(reports_df))
    
    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📈 Timeline", "🔥 Heatmap", "🔄 Perbandingan"])
    
    with tab1:
        st.subheader("📊 Overview Visualisasi")
        
        if not domains_df.empty:
            # Metrics row
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Domain", len(domains_df))
            with col2:
                active_count = len(domains_df[domains_df['status'] == 'aktif'])
                st.metric("Domain Aktif", active_count)
            with col3:
                brands_count = domains_df['brand'].nunique()
                st.metric("Jumlah Brand", brands_count)
            with col4:
                st.metric("Total Laporan", len(reports_df))
            
            # Charts row 1
            col1, col2 = st.columns(2)
            
            with col1:
                # Status pie chart
                status_fig = create_status_pie_chart(domains_df)
                if status_fig:
                    st.plotly_chart(status_fig, use_container_width=True)
            
            with col2:
                # Brand distribution
                brand_fig = create_brand_distribution_chart(domains_df)
                if brand_fig:
                    st.plotly_chart(brand_fig, use_container_width=True)
            
            # Charts row 2
            col1, col2 = st.columns(2)
            
            with col1:
                # Category chart
                category_fig = create_category_chart(domains_df)
                if category_fig:
                    st.plotly_chart(category_fig, use_container_width=True)
                else:
                    st.info("Data kategori tidak tersedia")
            
            with col2:
                # Domain growth
                growth_fig = create_domain_growth_chart(domains_df)
                if growth_fig:
                    st.plotly_chart(growth_fig, use_container_width=True)
        else:
            st.info("Tidak ada data domain untuk ditampilkan dengan filter yang dipilih.")
    
    with tab2:
        st.subheader("📈 Timeline Analisis")
        
        # Timeline chart
        timeline_fig = create_timeline_chart(domains_df, reports_df)
        if timeline_fig:
            st.plotly_chart(timeline_fig, use_container_width=True)
        else:
            st.info("Tidak ada data timeline untuk ditampilkan.")
        
        # Additional timeline insights
        if not domains_df.empty:
            st.subheader("📊 Insight Timeline")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Most active day
                if 'created_at' in domains_df.columns:
                    domains_df['day_name'] = pd.to_datetime(domains_df['created_at']).dt.day_name()
                    most_active_day = domains_df['day_name'].value_counts().index[0]
                    st.metric("Hari Paling Aktif", most_active_day)
                
                # Average domains per day
                if 'created_at' in domains_df.columns:
                    days_count = pd.to_datetime(domains_df['created_at']).dt.date.nunique()
                    avg_per_day = len(domains_df) / days_count if days_count > 0 else 0
                    st.metric("Rata-rata Domain/Hari", f"{avg_per_day:.1f}")
            
            with col2:
                # Peak registration day
                if 'created_at' in domains_df.columns:
                    daily_counts = domains_df.groupby(pd.to_datetime(domains_df['created_at']).dt.date).size()
                    peak_day = daily_counts.idxmax()
                    peak_count = daily_counts.max()
                    st.metric("Hari Tertinggi", f"{peak_day}")
                    st.metric("Jumlah Domain", peak_count)
    
    with tab3:
        st.subheader("🔥 Heatmap Aktivitas")
        
        if not reports_df.empty:
            heatmap_fig = create_heatmap_chart(reports_df)
            if heatmap_fig:
                st.plotly_chart(heatmap_fig, use_container_width=True)
                
                # Heatmap insights
                st.subheader("💡 Insight Heatmap")
                reports_df['reported_at'] = pd.to_datetime(reports_df['reported_at'])
                reports_df['hour'] = reports_df['reported_at'].dt.hour
                reports_df['day_name'] = reports_df['reported_at'].dt.day_name()
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    # Most active hour
                    most_active_hour = reports_df['hour'].value_counts().index[0]
                    st.metric("Jam Paling Aktif", f"{most_active_hour}:00")
                
                with col2:
                    # Most active day
                    most_active_day = reports_df['day_name'].value_counts().index[0]
                    st.metric("Hari Paling Aktif", most_active_day)
                
                with col3:
                    # Peak activity
                    hourly_counts = reports_df.groupby(['day_name', 'hour']).size()
                    peak_activity = hourly_counts.max()
                    st.metric("Aktivitas Tertinggi", f"{peak_activity} laporan")
        else:
            st.info("Tidak ada data laporan untuk heatmap.")
    
    with tab4:
        st.subheader("🔄 Perbandingan Brand")
        
        # Brand comparison chart
        comparison_fig = create_brand_comparison_chart(domains_df, reports_df)
        if comparison_fig:
            st.plotly_chart(comparison_fig, use_container_width=True)
        
        # Detailed comparison table
        if not domains_df.empty:
            st.subheader("📋 Tabel Perbandingan Detail")
            
            comparison_data = []
            for brand in domains_df['brand'].unique():
                brand_domains = domains_df[domains_df['brand'] == brand]
                brand_reports = reports_df[reports_df['brand'] == brand] if not reports_df.empty else pd.DataFrame()
                
                comparison_data.append({
                    'Brand': brand,
                    'Total Domain': len(brand_domains),
                    'Domain Aktif': len(brand_domains[brand_domains['status'] == 'aktif']),
                    'Domain Tidak Aktif': len(brand_domains[brand_domains['status'] != 'aktif']),
                    'Total Laporan': len(brand_reports),
                    'Rasio Laporan/Domain': len(brand_reports) / len(brand_domains) if len(brand_domains) > 0 else 0
                })
            
            comparison_df = pd.DataFrame(comparison_data)
            st.dataframe(comparison_df, use_container_width=True)
    
    # Refresh button with permission check
    st.markdown("---")
    col1, col2 = st.columns([1, 4])
    
    with col1:
        if st.button("🔄 Refresh Data", type="primary"):
            st.rerun()
    
    with col2:
        if user_is_admin:
            if st.button("⚙️ Advanced Analytics", type="secondary"):
                st.info("🚧 Advanced analytics features available for admin users")
        else:
            st.text("ℹ️ Contact admin for advanced analytics access")

if __name__ == "__main__":
    main()