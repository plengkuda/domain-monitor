import streamlit as st
import hashlib
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Optional

# Simple user database (in production, use proper database)
USERS_FILE = "users.json"

# Default admin user
DEFAULT_USERS = {
    "admin": {
        "password": "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8",  # 'password'
        "role": "admin",
        "created_at": "2025-01-01 00:00:00"
    },
    "user": {
        "password": "ef92f4e2e9a4b9e5c3c6e8d7f4f8a9b2c5d3e7f1a8b9c2d5e3f7a1b8c9d2e5f3",  # 'user123'
        "role": "user",
        "created_at": "2025-01-01 00:00:00"
    }
}

class AuthManager:
    def __init__(self):
        self.users_file = USERS_FILE
        self.load_users()
    
    def load_users(self):
        """Load users from file or create default users"""
        if os.path.exists(self.users_file):
            try:
                with open(self.users_file, 'r') as f:
                    self.users = json.load(f)
            except:
                self.users = DEFAULT_USERS.copy()
                self.save_users()
        else:
            self.users = DEFAULT_USERS.copy()
            self.save_users()
    
    def save_users(self):
        """Save users to file"""
        try:
            with open(self.users_file, 'w') as f:
                json.dump(self.users, f, indent=2)
        except Exception as e:
            st.error(f"Error saving users: {e}")
    
    def hash_password(self, password: str) -> str:
        """Hash password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_credentials(self, username: str, password: str) -> bool:
        """Verify user credentials"""
        if username in self.users:
            hashed_password = self.hash_password(password)
            return self.users[username]["password"] == hashed_password
        return False
    
    def get_user_role(self, username: str) -> Optional[str]:
        """Get user role"""
        if username in self.users:
            return self.users[username].get("role", "user")
        return None
    
    def add_user(self, username: str, password: str, role: str = "user") -> bool:
        """Add new user"""
        if username in self.users:
            return False
        
        self.users[username] = {
            "password": self.hash_password(password),
            "role": role,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.save_users()
        return True
    
    def change_password(self, username: str, new_password: str) -> bool:
        """Change user password"""
        if username in self.users:
            self.users[username]["password"] = self.hash_password(new_password)
            self.save_users()
            return True
        return False
    
    def delete_user(self, username: str) -> bool:
        """Delete user"""
        if username in self.users and username != "admin":
            del self.users[username]
            self.save_users()
            return True
        return False

def init_session_state():
    """Initialize session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'user_role' not in st.session_state:
        st.session_state.user_role = None
    if 'login_time' not in st.session_state:
        st.session_state.login_time = None

def check_session_timeout():
    """Check if session has timed out (4 hours)"""
    if st.session_state.login_time:
        login_time = datetime.fromisoformat(st.session_state.login_time)
        if datetime.now() - login_time > timedelta(hours=4):
            logout()
            return True
    return False

def login(username: str, password: str) -> bool:
    """Login user"""
    auth_manager = AuthManager()
    
    if auth_manager.verify_credentials(username, password):
        st.session_state.authenticated = True
        st.session_state.username = username
        st.session_state.user_role = auth_manager.get_user_role(username)
        st.session_state.login_time = datetime.now().isoformat()
        return True
    return False

def logout():
    """Logout user"""
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.user_role = None
    st.session_state.login_time = None

def require_auth():
    """Decorator function to require authentication"""
    init_session_state()
    
    # Check session timeout
    if check_session_timeout():
        st.warning("Session expired. Please login again.")
        return False
    
    if not st.session_state.authenticated:
        show_login_page()
        return False
    
    return True

def require_admin():
    """Check if user has admin role"""
    if not require_auth():
        return False
    
    if st.session_state.user_role != "admin":
        st.error("⛔ Access denied. Admin role required.")
        return False
    
    return True

def show_login_page():
    """Show login page"""
    st.markdown("""
    <style>
        .login-container {
            max-width: 400px;
            margin: 50px auto;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            background-color: white;
        }
        .login-header {
            text-align: center;
            color: #1f77b4;
            margin-bottom: 2rem;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<h2 class="login-header">🔐 Domain Monitor Login</h2>', unsafe_allow_html=True)
    
    with st.form("login_form"):
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            login_button = st.form_submit_button("🚀 Login", use_container_width=True)
        with col2:
            demo_button = st.form_submit_button("👤 Demo Login", use_container_width=True)
        
        if login_button:
            if username and password:
                if login(username, password):
                    st.success("✅ Login successful!")
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password")
            else:
                st.warning("⚠️ Please enter both username and password")
        
        if demo_button:
            if login("admin", "password"):
                st.success("✅ Demo login successful!")
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Demo credentials info
    st.info("""
    **Demo Credentials:**
    - Admin: username=`admin`, password=`password`
    - User: username=`user`, password=`user123`
    """)

def show_user_menu():
    """Show user menu in sidebar"""
    if st.session_state.authenticated:
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 👤 User Info")
        st.sidebar.write(f"**User:** {st.session_state.username}")
        st.sidebar.write(f"**Role:** {st.session_state.user_role}")
        
        if st.session_state.login_time:
            login_time = datetime.fromisoformat(st.session_state.login_time)
            st.sidebar.write(f"**Login:** {login_time.strftime('%H:%M:%S')}")
        
        if st.sidebar.button("🚪 Logout", use_container_width=True):
            logout()
            st.rerun()
        
        # Admin menu
        if st.session_state.user_role == "admin":
            st.sidebar.markdown("---")
            st.sidebar.markdown("### ⚙️ Admin")
            if st.sidebar.button("👥 User Management", use_container_width=True):
                st.session_state.show_user_management = True

def show_user_management():
    """Show user management interface (admin only)"""
    if not require_admin():
        return
    
    st.title("👥 User Management")
    
    auth_manager = AuthManager()
    
    # Tabs for different actions
    tab1, tab2, tab3 = st.tabs(["📋 User List", "➕ Add User", "🔧 Manage Users"])
    
    with tab1:
        st.subheader("📋 Current Users")
        
        users_data = []
        for username, data in auth_manager.users.items():
            users_data.append({
                "Username": username,
                "Role": data.get("role", "user"),
                "Created": data.get("created_at", "Unknown")
            })
        
        if users_data:
            import pandas as pd
            df = pd.DataFrame(users_data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No users found.")
    
    with tab2:
        st.subheader("➕ Add New User")
        
        with st.form("add_user_form"):
            new_username = st.text_input("Username")
            new_password = st.text_input("Password", type="password")
            new_role = st.selectbox("Role", ["user", "admin"])
            
            if st.form_submit_button("➕ Add User"):
                if new_username and new_password:
                    if auth_manager.add_user(new_username, new_password, new_role):
                        st.success(f"✅ User '{new_username}' added successfully!")
                    else:
                        st.error(f"❌ User '{new_username}' already exists!")
                else:
                    st.warning("⚠️ Please fill all fields!")
    
    with tab3:
        st.subheader("🔧 Manage Users")
        
        if auth_manager.users:
            selected_user = st.selectbox("Select User", list(auth_manager.users.keys()))
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 🔑 Change Password")
                with st.form("change_password_form"):
                    new_password = st.text_input("New Password", type="password")
                    if st.form_submit_button("🔑 Change Password"):
                        if new_password:
                            if auth_manager.change_password(selected_user, new_password):
                                st.success(f"✅ Password changed for '{selected_user}'!")
                            else:
                                st.error("❌ Failed to change password!")
                        else:
                            st.warning("⚠️ Please enter new password!")
            
            with col2:
                st.markdown("#### 🗑️ Delete User")
                if selected_user != "admin":
                    if st.button(f"🗑️ Delete {selected_user}", type="secondary"):
                        if auth_manager.delete_user(selected_user):
                            st.success(f"✅ User '{selected_user}' deleted!")
                            st.rerun()
                        else:
                            st.error("❌ Failed to delete user!")
                else:
                    st.warning("⚠️ Cannot delete admin user!")

# Utility functions
def get_current_user():
    """Get current logged in user"""
    return st.session_state.username if st.session_state.authenticated else None

def get_current_role():
    """Get current user role"""
    return st.session_state.user_role if st.session_state.authenticated else None

def is_admin():
    """Check if current user is admin"""
    return st.session_state.user_role == "admin" if st.session_state.authenticated else False