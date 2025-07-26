import sqlite3
import pandas as pd
from datetime import datetime
from config import DATABASE_PATH
from typing import List, Dict, Optional
import json

class DatabaseManager:
    def __init__(self):
        self.db_path = DATABASE_PATH
        self.init_database()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Initialize database with required tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Domains table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS domains (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                domain TEXT NOT NULL,
                brand TEXT NOT NULL,
                status TEXT DEFAULT 'aktif',
                kategori TEXT DEFAULT 'normal',
                expired_date TEXT,
                catatan TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Reports table for JS agent data
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                domain TEXT NOT NULL,
                brand TEXT NOT NULL,
                status TEXT,
                kategori TEXT,
                expired_date TEXT,
                catatan TEXT,
                api_key TEXT,
                reported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Files table for uploaded files
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS uploaded_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                file_type TEXT,
                file_size INTEGER,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'processed'
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_domain(self, domain: str, brand: str, status: str = 'aktif', 
                   kategori: str = 'normal', expired_date: str = None, 
                   catatan: str = None) -> bool:
        """Add new domain to database"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO domains (domain, brand, status, kategori, expired_date, catatan)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (domain, brand, status, kategori, expired_date, catatan))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding domain: {e}")
            return False
    
    def get_domains(self) -> pd.DataFrame:
        """Get all domains as DataFrame"""
        try:
            conn = self.get_connection()
            df = pd.read_sql_query("SELECT * FROM domains ORDER BY created_at DESC", conn)
            conn.close()
            return df
        except Exception as e:
            print(f"Error getting domains: {e}")
            return pd.DataFrame()
    
    def update_domain(self, domain_id: int, **kwargs) -> bool:
        """Update domain information"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Build dynamic update query
            set_clause = []
            values = []
            for key, value in kwargs.items():
                if key in ['domain', 'brand', 'status', 'kategori', 'expired_date', 'catatan']:
                    set_clause.append(f"{key} = ?")
                    values.append(value)
            
            if not set_clause:
                return False
            
            set_clause.append("updated_at = CURRENT_TIMESTAMP")
            values.append(domain_id)
            
            query = f"UPDATE domains SET {', '.join(set_clause)} WHERE id = ?"
            cursor.execute(query, values)
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating domain: {e}")
            return False
    
    def delete_domain(self, domain_id: int) -> bool:
        """Delete domain by ID"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM domains WHERE id = ?", (domain_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting domain: {e}")
            return False
    
    def add_report(self, domain: str, brand: str, status: str, kategori: str,
                   expired_date: str, catatan: str, api_key: str) -> bool:
        """Add report from JS agent"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO reports (domain, brand, status, kategori, expired_date, catatan, api_key)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (domain, brand, status, kategori, expired_date, catatan, api_key))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding report: {e}")
            return False
    
    def get_reports(self) -> pd.DataFrame:
        """Get all reports as DataFrame"""
        try:
            conn = self.get_connection()
            df = pd.read_sql_query("SELECT * FROM reports ORDER BY reported_at DESC", conn)
            conn.close()
            return df
        except Exception as e:
            print(f"Error getting reports: {e}")
            return pd.DataFrame()
    
    def add_uploaded_file(self, filename: str, file_type: str, file_size: int) -> bool:
        """Add uploaded file record"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO uploaded_files (filename, file_type, file_size)
                VALUES (?, ?, ?)
            ''', (filename, file_type, file_size))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding file record: {e}")
            return False
    
    def get_uploaded_files(self) -> pd.DataFrame:
        """Get all uploaded files as DataFrame"""
        try:
            conn = self.get_connection()
            df = pd.read_sql_query("SELECT * FROM uploaded_files ORDER BY uploaded_at DESC", conn)
            conn.close()
            return df
        except Exception as e:
            print(f"Error getting files: {e}")
            return pd.DataFrame()
    
    def get_dashboard_stats(self) -> Dict:
        """Get dashboard statistics"""
        try:
            conn = self.get_connection()
            
            # Total domains
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM domains")
            total_domains = cursor.fetchone()[0]
            
            # Active domains
            cursor.execute("SELECT COUNT(*) FROM domains WHERE status = 'aktif'")
            active_domains = cursor.fetchone()[0]
            
            # Domains by brand
            cursor.execute("SELECT brand, COUNT(*) FROM domains GROUP BY brand")
            brand_stats = dict(cursor.fetchall())
            
            # Recent reports
            cursor.execute("SELECT COUNT(*) FROM reports WHERE date(reported_at) = date('now')")
            today_reports = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'total_domains': total_domains,
                'active_domains': active_domains,
                'inactive_domains': total_domains - active_domains,
                'brand_stats': brand_stats,
                'today_reports': today_reports
            }
        except Exception as e:
            print(f"Error getting dashboard stats: {e}")
            return {
                'total_domains': 0,
                'active_domains': 0,
                'inactive_domains': 0,
                'brand_stats': {},
                'today_reports': 0
            }