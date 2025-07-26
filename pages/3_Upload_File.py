import streamlit as st
import requests
import pandas as pd
import io
from datetime import datetime
from auth import require_auth, show_user_menu, get_current_user

st.set_page_config(
    page_title="Upload File - Domain Monitor",
    page_icon="📁",
    layout="wide"
)

# Check authentication
if not require_auth():
    st.stop()

# API Configuration
API_BASE_URL = "http://localhost:8000"

def add_domain(domain_data):
    """Add new domain via API"""
    try:
        response = requests.post(f"{API_BASE_URL}/api/submit-domain", json=domain_data, timeout=10)
        return response.status_code == 200, response.json()
    except Exception as e:
        return False, {"detail": str(e)}

def process_csv_content(file_content, encoding='utf-8'):
    """Process CSV file content"""
    try:
        content_str = file_content.decode(encoding)
        df = pd.read_csv(io.StringIO(content_str))
        return df, None
    except UnicodeDecodeError as e:
        return None, f"Encoding error: {str(e)}"
    except Exception as e:
        return None, f"CSV parsing error: {str(e)}"

def process_excel_content(file_content):
    """Process Excel file content"""
    try:
        df = pd.read_excel(io.BytesIO(file_content))
        return df, None
    except Exception as e:
        return None, f"Excel parsing error: {str(e)}"

def validate_domain_dataframe(df):
    """Validate uploaded domain DataFrame"""
    errors = []
    warnings = []
    
    # Check required columns
    required_columns = ['domain', 'brand']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        errors.append(f"Missing required columns: {', '.join(missing_columns)}")
        return False, errors, warnings
    
    # Check for empty required fields
    empty_domains = df[df['domain'].isna() | (df['domain'] == '')].shape[0]
    empty_brands = df[df['brand'].isna() | (df['brand'] == '')].shape[0]
    
    if empty_domains > 0:
        warnings.append(f"{empty_domains} rows have empty domain values")
    
    if empty_brands > 0:
        warnings.append(f"{empty_brands} rows have empty brand values")
    
    # Check valid brands
    valid_brands = ['slot603', 'netpro']
    invalid_brands = df[~df['brand'].isin(valid_brands + [None, ''])]['brand'].unique()
    
    if len(invalid_brands) > 0:
        warnings.append(f"Invalid brands found: {', '.join(invalid_brands)}. Valid brands: {', '.join(valid_brands)}")
    
    # Check domain format (basic validation)
    domain_pattern = r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
    import re
    
    invalid_domains = []
    for domain in df['domain'].dropna():
        if domain and not re.match(domain_pattern, str(domain)):
            invalid_domains.append(domain)
    
    if invalid_domains:
        warnings.append(f"{len(invalid_domains)} domains have invalid format")
    
    return True, errors, warnings

def main():
    # Show user menu in sidebar
    show_user_menu()
    
    st.title("📁 Upload File Domain")
    
    # User info
    current_user = get_current_user()
    st.info(f"👤 Logged in as: **{current_user}**")
    
    # Instructions
    st.markdown("""
    ### 📋 Petunjuk Upload File:
    
    **Format file yang didukung:**
    - CSV (.csv)
    - Excel (.xlsx, .xls)
    
    **Kolom yang diperlukan:**
    - `domain` (wajib) - Nama domain tanpa http/https
    - `brand` (wajib) - Brand domain (slot603 atau netpro)
    - `status` (opsional) - Status domain (aktif/tidak aktif)
    - `kategori` (opsional) - Kategori domain (normal/premium/blocked)
    - `expired_date` (opsional) - Tanggal kadaluarsa (YYYY-MM-DD)
    - `catatan` (opsional) - Catatan tambahan
    
    **Contoh format CSV:**
    ```
    domain,brand,status,kategori,expired_date,catatan
    example1.com,slot603,aktif,normal,2025-12-31,Contoh domain 1
    example2.com,netpro,tidak aktif,premium,2025-11-30,Contoh domain 2
    ```
    """)
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Pilih file untuk diupload",
        type=['csv', 'xlsx', 'xls'],
        help="Upload file CSV atau Excel yang berisi data domain"
    )
    
    if uploaded_file is not None:
        # Display file info
        st.subheader("📄 Informasi File")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Nama File", uploaded_file.name)
        with col2:
            st.metric("Ukuran File", f"{uploaded_file.size:,} bytes")
        with col3:
            st.metric("Tipe File", uploaded_file.type)
        
        # Process file
        file_content = uploaded_file.read()
        df = None
        error_message = None
        
        # Process based on file type
        if uploaded_file.name.endswith('.csv'):
            # Try different encodings for CSV
            encodings_to_try = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            
            for encoding in encodings_to_try:
                df, error_message = process_csv_content(file_content, encoding)
                if df is not None:
                    st.success(f"✅ File CSV berhasil dibaca dengan encoding: {encoding}")
                    break
            
            if df is None:
                st.error(f"❌ Gagal membaca file CSV: {error_message}")
                return
        
        elif uploaded_file.name.endswith(('.xlsx', '.xls')):
            df, error_message = process_excel_content(file_content)
            
            if df is None:
                st.error(f"❌ Gagal membaca file Excel: {error_message}")
                return
            else:
                st.success("✅ File Excel berhasil dibaca")
        
        # Display data preview
        if df is not None and not df.empty:
            st.subheader("👀 Preview Data")
            st.info(f"Total baris: {len(df)}")
            st.dataframe(df.head(10), use_container_width=True)
            
            if len(df) > 10:
                st.info(f"Menampilkan 10 baris pertama dari {len(df)} total baris.")
            
            # Validate data
            st.subheader("✅ Validasi Data")
            is_valid, errors, warnings = validate_domain_dataframe(df)
            
            # Show validation results
            if errors:
                for error in errors:
                    st.error(f"❌ {error}")
            
            if warnings:
                for warning in warnings:
                    st.warning(f"⚠️ {warning}")
            
            if not errors:
                st.success("✅ Data valid dan siap untuk diimpor!")
                
                # Data processing options
                st.subheader("⚙️ Opsi Import")
                
                col1, col2 = st.columns(2)
                with col1:
                    skip_invalid = st.checkbox("Skip baris dengan data tidak valid", value=True)
                with col2:
                    confirm_import = st.checkbox("Saya yakin ingin mengimpor data ini", value=False)
                
                # Show current user performing import
                st.info(f"📝 Import akan dilakukan oleh: **{current_user}**")
                
                # Preview processed data
                processed_df = df.copy()
                
                # Clean and prepare data
                if skip_invalid:
                    # Remove rows with empty required fields
                    initial_count = len(processed_df)
                    processed_df = processed_df.dropna(subset=['domain', 'brand'])
                    processed_df = processed_df[(processed_df['domain'] != '') & (processed_df['brand'] != '')]
                    
                    # Filter valid brands
                    valid_brands = ['slot603', 'netpro']
                    processed_df = processed_df[processed_df['brand'].isin(valid_brands)]
                    
                    removed_count = initial_count - len(processed_df)
                    if removed_count > 0:
                        st.info(f"📊 {removed_count} baris akan dilewati karena data tidak valid")
                
                # Normalize columns
                column_mapping = {
                    'domain': 'domain',
                    'brand': 'brand',
                    'status': 'status',
                    'kategori': 'kategori',
                    'expired_date': 'expired',
                    'expired': 'expired',
                    'expire': 'expired',
                    'catatan': 'catatan',
                    'notes': 'catatan',
                    'note': 'catatan'
                }
                
                # Rename columns to match API
                for old_col, new_col in column_mapping.items():
                    if old_col in processed_df.columns and old_col != new_col:
                        processed_df = processed_df.rename(columns={old_col: new_col})
                
                # Set default values
                if 'status' not in processed_df.columns:
                    processed_df['status'] = 'aktif'
                else:
                    processed_df['status'] = processed_df['status'].fillna('aktif')
                
                if 'kategori' not in processed_df.columns:
                    processed_df['kategori'] = 'normal'
                else:
                    processed_df['kategori'] = processed_df['kategori'].fillna('normal')
                
                # Clean domain names
                processed_df['domain'] = processed_df['domain'].str.strip().str.lower()
                processed_df['domain'] = processed_df['domain'].str.replace('http://', '', regex=False).str.replace('https://', '', regex=False)
                processed_df['domain'] = processed_df['domain'].str.replace('www.', '', regex=False)
                
                # Show final preview
                if len(processed_df) > 0:
                    st.subheader("📋 Data Yang Akan Diimpor")
                    st.dataframe(processed_df[['domain', 'brand', 'status', 'kategori']].head(10), use_container_width=True)
                    st.info(f"Total domain yang akan diimpor: {len(processed_df)}")
                    
                    # Import button
                    if confirm_import:
                        if st.button("🚀 Mulai Import", type="primary", use_container_width=True):
                            import_domains(processed_df)
                    else:
                        st.warning("⚠️ Centang checkbox konfirmasi untuk melanjutkan import")
                else:
                    st.error("❌ Tidak ada data valid yang dapat diimpor")
            else:
                st.error("❌ Perbaiki error di atas sebelum melanjutkan import")
        
        elif df is not None and df.empty:
            st.warning("⚠️ File kosong atau tidak berisi data")
        
    # Download template
    st.markdown("---")
    st.subheader("📥 Download Template")
    st.markdown("Jika Anda belum memiliki file, download template di bawah ini:")
    
    # Create template
    template_data = {
        'domain': ['example1.com', 'example2.com', 'example3.com'],
        'brand': ['slot603', 'netpro', 'slot603'],
        'status': ['aktif', 'aktif', 'tidak aktif'],
        'kategori': ['normal', 'premium', 'normal'],
        'expired_date': ['2025-12-31', '2025-11-30', '2025-10-15'],
        'catatan': ['Contoh domain 1', 'Contoh domain 2', 'Contoh domain 3']
    }
    
    template_df = pd.DataFrame(template_data)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # CSV template
        csv_template = template_df.to_csv(index=False)
        st.download_button(
            label="📄 Download Template CSV",
            data=csv_template,
            file_name="template_domain.csv",
            mime="text/csv"
        )
    
    with col2:
        # Excel template
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            template_df.to_excel(writer, index=False, sheet_name='Domains')
        
        st.download_button(
            label="📊 Download Template Excel",
            data=excel_buffer.getvalue(),
            file_name="template_domain.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

def import_domains(df):
    """Import domains from DataFrame"""
    current_user = get_current_user()
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    success_count = 0
    error_count = 0
    error_details = []
    
    total_rows = len(df)
    
    for index, row in df.iterrows():
        # Update progress
        progress = (index + 1) / total_rows
        progress_bar.progress(progress)
        status_text.text(f"Memproses {index + 1}/{total_rows}: {row['domain']}")
        
        # Prepare domain data with user info
        domain_data = {
            "domain": row['domain'],
            "brand": row['brand'],
            "status": row.get('status', 'aktif'),
            "kategori": row.get('kategori', 'normal'),
            "expired": row.get('expired') if pd.notna(row.get('expired')) else None,
            "catatan": f"Uploaded by {current_user} - " + (row.get('catatan', '') if pd.notna(row.get('catatan')) else '')
        }
        
        # Add domain
        success, response = add_domain(domain_data)
        
        if success:
            success_count += 1
        else:
            error_count += 1
            error_details.append({
                'domain': row['domain'],
                'error': response.get('detail', 'Unknown error')
            })
    
    # Show results
    progress_bar.progress(1.0)
    status_text.text("Import selesai!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.success(f"✅ Berhasil: {success_count} domain")
    
    with col2:
        if error_count > 0:
            st.error(f"❌ Gagal: {error_count} domain")
        else:
            st.success("✅ Semua domain berhasil diimpor!")
    
    # Show error details if any
    if error_details:
        st.subheader("❌ Detail Error")
        error_df = pd.DataFrame(error_details)
        st.dataframe(error_df, use_container_width=True)
    
    # Refresh suggestion
    if success_count > 0:
        st.info("💡 Kunjungi halaman 'Data Domain' untuk melihat domain yang telah diimpor")

if __name__ == "__main__":
    main()