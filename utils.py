import pandas as pd
import requests
from datetime import datetime, timedelta
import re
from typing import List, Dict, Optional
import json

class DomainUtils:
    @staticmethod
    def validate_domain(domain: str) -> bool:
        """Validate domain format"""
        pattern = r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
        return bool(re.match(pattern, domain))
    
    @staticmethod
    def extract_domain_from_url(url: str) -> str:
        """Extract domain from URL"""
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc
        except:
            return url
    
    @staticmethod
    def check_domain_status(domain: str) -> Dict:
        """Check if domain is accessible"""
        try:
            response = requests.head(f"http://{domain}", timeout=10)
            return {
                'status': 'aktif',
                'status_code': response.status_code,
                'accessible': True
            }
        except requests.RequestException:
            try:
                response = requests.head(f"https://{domain}", timeout=10)
                return {
                    'status': 'aktif',
                    'status_code': response.status_code,
                    'accessible': True
                }
            except requests.RequestException:
                return {
                    'status': 'tidak aktif',
                    'status_code': None,
                    'accessible': False
                }

class FileUtils:
    @staticmethod
    def process_csv_file(file_content: bytes) -> pd.DataFrame:
        """Process uploaded CSV file"""
        try:
            # Try different encodings
            for encoding in ['utf-8', 'latin-1', 'cp1252']:
                try:
                    content = file_content.decode(encoding)
                    # Use StringIO to create file-like object
                    from io import StringIO
                    df = pd.read_csv(StringIO(content))
                    return df
                except UnicodeDecodeError:
                    continue
            
            # If all encodings fail
            raise ValueError("Could not decode file with any encoding")
            
        except Exception as e:
            print(f"Error processing CSV: {e}")
            return pd.DataFrame()
    
    @staticmethod
    def process_excel_file(file_content: bytes) -> pd.DataFrame:
        """Process uploaded Excel file"""
        try:
            from io import BytesIO
            df = pd.read_excel(BytesIO(file_content))
            return df
        except Exception as e:
            print(f"Error processing Excel: {e}")
            return pd.DataFrame()
    
    @staticmethod
    def validate_domain_file(df: pd.DataFrame) -> Dict:
        """Validate domain file structure"""
        required_columns = ['domain', 'brand']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            return {
                'valid': False,
                'error': f"Missing required columns: {', '.join(missing_columns)}",
                'columns': list(df.columns)
            }
        
        # Check for empty domains
        empty_domains = df[df['domain'].isna() | (df['domain'] == '')].shape[0]
        
        return {
            'valid': True,
            'rows': len(df),
            'empty_domains': empty_domains,
            'columns': list(df.columns)
        }

class DateUtils:
    @staticmethod
    def format_date(date_str: str) -> str:
        """Format date string to standard format"""
        if not date_str:
            return ""
        
        try:
            # Try parsing different date formats
            formats = ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y']
            for fmt in formats:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    return dt.strftime('%Y-%m-%d')
                except ValueError:
                    continue
            
            # If no format matches, return as is
            return date_str
        except:
            return date_str
    
    @staticmethod
    def days_until_expiry(expiry_date: str) -> int:
        """Calculate days until domain expiry"""
        if not expiry_date:
            return -1
        
        try:
            expiry = datetime.strptime(expiry_date, '%Y-%m-%d')
            today = datetime.now()
            delta = expiry - today
            return delta.days
        except:
            return -1
    
    @staticmethod
    def is_expired(expiry_date: str) -> bool:
        """Check if domain is expired"""
        days = DateUtils.days_until_expiry(expiry_date)
        return days < 0 if days != -1 else False

class APIUtils:
    @staticmethod
    def validate_api_key(api_key: str, brand: str) -> bool:
        """Validate API key for brand"""
        from config import API_KEYS
        return API_KEYS.get(brand) == api_key
    
    @staticmethod
    def send_to_external_api(data: Dict) -> bool:
        """Send data to external API"""
        try:
            from config import EXTERNAL_API_URL
            response = requests.post(EXTERNAL_API_URL, json=data, timeout=30)
            return response.status_code == 200
        except Exception as e:
            print(f"Error sending to external API: {e}")
            return False

class ChartUtils:
    @staticmethod
    def prepare_domain_status_chart(df: pd.DataFrame) -> Dict:
        """Prepare data for domain status pie chart"""
        if df.empty:
            return {'labels': [], 'values': []}
        
        status_counts = df['status'].value_counts()
        return {
            'labels': status_counts.index.tolist(),
            'values': status_counts.values.tolist()
        }
    
    @staticmethod
    def prepare_brand_distribution_chart(df: pd.DataFrame) -> Dict:
        """Prepare data for brand distribution chart"""
        if df.empty:
            return {'labels': [], 'values': []}
        
        brand_counts = df['brand'].value_counts()
        return {
            'labels': brand_counts.index.tolist(),
            'values': brand_counts.values.tolist()
        }
    
    @staticmethod
    def prepare_timeline_chart(df: pd.DataFrame) -> Dict:
        """Prepare data for timeline chart"""
        if df.empty:
            return {'dates': [], 'counts': []}
        
        # Convert created_at to date and count
        df['date'] = pd.to_datetime(df['created_at']).dt.date
        date_counts = df.groupby('date').size().reset_index(name='count')
        
        return {
            'dates': date_counts['date'].astype(str).tolist(),
            'counts': date_counts['count'].tolist()
        }