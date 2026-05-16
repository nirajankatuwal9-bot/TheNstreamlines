import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timezone, timedelta
import os
import re
from google import genai
from pdf2image import convert_from_path
import io
import base64
import bcrypt
from PIL import Image
import google.generativeai as genai
import fitz
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time 
from streamlit_autorefresh import st_autorefresh


# ========== BEAUTIFUL REFINED CYBERPUNK UI (HIGH VISIBILITY EDITION) ==========
st.markdown("""
<style>
    /* 1. Beautiful Sci-Fi Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Oxanium:wght@500;700&family=Space+Grotesk:wght@400;500;600&display=swap');

    /* 2. Deep Void Background */
    .stApp {
        background-color: #060612 !important;
        background-image: 
            radial-gradient(circle at 10% 20%, rgba(213, 0, 249, 0.05), transparent 40%),
            radial-gradient(circle at 90% 80%, rgba(0, 229, 255, 0.05), transparent 40%) !important;
    }

    /* 3. Force Global Text, Labels, and Inactive Radio Options to be Fully Visible */
    html, body, span, p, label, 
    [data-testid="stWidgetLabel"], 
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stRadio"] label span {
        font-family: 'Space Grotesk', sans-serif !important;
        color: #E2EFFF !important; /* Crisp, bright soft ice-white */
        font-size: 1.02rem !important;
    }

    /* 4. Beautiful Resized Glowing Headers */
    h1, h2, h3, h4 {
        font-family: 'Oxanium', sans-serif !important;
        color: #00E5FF !important; /* Neon Cyan */
        text-shadow: 0 0 8px rgba(0, 229, 255, 0.5), 0 0 15px rgba(0, 229, 255, 0.3); 
        letter-spacing: 1.2px;
        font-weight: 700;
    }
    h1 { font-size: 2.2rem !important; margin-bottom: 1rem !important; }
    h2 { font-size: 1.7rem !important; margin-bottom: 0.8rem !important; }
    h3 { font-size: 1.3rem !important; margin-bottom: 0.5rem !important; }

    /* 5. Fix Top Navigation Tabs (Remove Red Line & Add Cyan Hover Glow) */
    button[data-baseweb="tab"] {
        color: #C1D5EE !important; /* Clear visibility for inactive tabs */
        font-family: 'Space Grotesk', sans-serif !important;
        background: transparent !important;
        border: none !important;
        transition: all 0.3s ease !important;
    }

    /* Target the text container inside the tab button directly */
    button[data-baseweb="tab"] div {
        color: inherit !important;
    }

    /* Hover State: Make tabs glow cyan when mouse moves over them */
    button[data-baseweb="tab"]:hover {
        color: #00E5FF !important;
        text-shadow: 0 0 10px rgba(0, 229, 255, 0.8) !important;
        cursor: pointer;
    }

    /* Active Selected Tab: Replace default red highlight bar with Neon Cyan line */
    button[aria-selected="true"] {
        color: #00E5FF !important;
        border-bottom: 2px solid #00E5FF !important;
        text-shadow: 0 0 8px rgba(0, 229, 255, 0.5) !important;
    }
    
    /* Suppress default Streamlit indicator lines that cause the red color bleed */
    [data-testid="stTabs"] div[role="tablist"] div {
        background-color: transparent !important;
    }

    /* 6. Sleek Dark Glass Input Dropdowns & Text Boxes */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div>div {
        background-color: rgba(10, 15, 30, 0.9) !important;
        color: #00E5FF !important; /* Active selected text is cyan */
        border: 1px solid rgba(0, 229, 255, 0.4) !important; /* Cyan borders */
        border-radius: 6px !important;
        font-family: 'Space Grotesk', sans-serif;
    }

    /* Force option text dropdown items to be clearly readable */
    div[data-baseweb="select"] * {
        color: #00E5FF !important;
    }

    /* 7. Refined Multi-Color Neon Action Buttons */
    .stButton>button {
        background: rgba(6, 6, 18, 0.8) !important;
        border: 1px solid transparent !important;
        border-image: linear-gradient(90deg, #00E5FF, #D500F9) 1 !important;
        color: #FFFFFF !important;
        font-family: 'Oxanium', sans-serif !important;
        font-size: 1.1rem !important;
        letter-spacing: 1px;
        transition: all 0.3s ease-in-out;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, rgba(0, 229, 255, 0.2), rgba(213, 0, 249, 0.2)) !important;
        color: #00E5FF !important;
        box-shadow: 0 0 15px rgba(0, 229, 255, 0.4), 0 0 25px rgba(213, 0, 249, 0.3) !important;
        transform: translateY(-2px);
    }

    /* 8. Sidebar Clock Styling */
    .sidebar-clock {
        background: rgba(0, 229, 255, 0.05);
        border: 1px solid rgba(0, 229, 255, 0.3);
        border-radius: 10px;
        padding: 12px;
        color: #00E5FF !important;
        font-family: 'Oxanium', sans-serif;
        font-weight: 700;
        font-size: 1.1rem;
        text-align: center;
        text-shadow: 0 0 10px rgba(0, 229, 255, 0.6);
        margin-bottom: 15px;
    }
    [data-testid="stSidebar"] {
        background-color: #05050C !important;
        border-right: 1px solid rgba(213, 0, 249, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# ====================================================
# =====================================================
# ================= TIMEZONE CONFIG =================
NST = timezone(timedelta(hours=5, minutes=45))
# ================= CONFIG =================

st.set_page_config(
    page_title="The N-streamlines",
    page_icon="🌊",
    layout="wide"
)


# ----------------------------------------

# --- CUSTOM CSS ANIMATIONS ---
st.markdown("""
<style>
    /* Target the content inside the tabs */
    div[role="tabpanel"] {
        animation: fadeInSlideUp 0.4s ease-out forwards;
    }

    /* Define the animation keyframes */
    @keyframes fadeInSlideUp {
        0% {
            opacity: 0;
            transform: translateY(15px);
        }
        100% {
            opacity: 1;
            transform: translateY(0);
        }
    }
</style>
""", unsafe_allow_html=True)
# -----------------------------
# ================= MOBILE RESPONSIVENESS =================

st.markdown("""
<style>
    /* Mobile optimizations */
    @media (max-width: 768px) {
        .block-container {
            padding: 1rem 1rem 5rem 1rem !important;
        }
        
        .stButton>button {
            width: 100%;
        }
        
        .stDataFrame {
            font-size: 12px;
        }
        
        h1 {
            font-size: 1.5rem !important;
        }
        
        h2 {
            font-size: 1.3rem !important;
        }
        
        h3 {
            font-size: 1.1rem !important;
        }
    }
    
    /* Improve button visibility */
    .stButton>button {
        font-weight: 500;
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    /* Better expander styling */
    .streamlit-expanderHeader {
        background-color: #f0f2f6;
        border-radius: 8px;
        font-weight: 500;
    }
    
    /* Improve metric cards */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)
# ================= GLOBAL FOOTER =================

st.markdown("""
    <style>
    /* Hide the default Streamlit watermark */
    footer {visibility: hidden;}
    
    /* Create the custom NiraFlow footer */
    .nira-footer {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: #ffffff;
        border-top: 1px solid #e1e4e8;
        color: #555;
        text-align: center;
        padding: 12px 0;
        font-size: 0.85em;
        z-index: 999;
    }
    
    /* Add padding to the bottom of the app so content doesn't hide behind the footer */
    .block-container {
        padding-bottom: 70px !important; 
    }
    </style>
    
    <div class="nira-footer">
        <strong>🌊 The N-Streamlines</strong> | Advanced Hydro-Informatics Platform | © 2026 Developed by Er. Nirajan Katuwal
    </div>
""", unsafe_allow_html=True)


# ================= FOLDERS =================

os.makedirs("data", exist_ok=True)
os.makedirs("assignment_files", exist_ok=True)
os.makedirs("submission_files", exist_ok=True)
os.makedirs("study_materials", exist_ok=True)
# ================= ANNOUNCEMENTS =================

def create_announcement(title, message, semester_id, priority, user_id, expires_at=None):
    """
    Create a new announcement with an optional expiration date
    Returns: (success, message)
    """
    try:
        c.execute("""
        INSERT INTO announcements(title, message, semester_id, created_by, created_at, priority, expires_at)
        VALUES(?,?,?,?,?,?,?)
        """, (
            title.strip(),
            message.strip(),
            int(semester_id) if semester_id else None,
            int(user_id),
            str(datetime.now(NST)),
            priority,
            expires_at  # The calculated future time goes here!
        ))
        
        conn.commit()
        return True, "Announcement created successfully"
    except Exception as e:
        return False, "Error: {}".format(str(e))


def get_announcements_for_semester(semester_id=None):
    """
    Get valid announcements (unexpired or permanent) for a specific semester or all
    """
    # Get exact current time in your NST timezone for accurate comparison
    current_time = str(datetime.now(NST))
    
    if semester_id:
        df = pd.read_sql_query("""
        SELECT announcements.*, users.full_name as author, semesters.name as semester
        FROM announcements
        LEFT JOIN users ON announcements.created_by = users.id
        LEFT JOIN semesters ON announcements.semester_id = semesters.id
        WHERE (announcements.semester_id=? OR announcements.semester_id IS NULL)
          AND (announcements.expires_at IS NULL OR announcements.expires_at >= ?)
        ORDER BY announcements.created_at DESC
        """, conn, params=(int(semester_id), current_time))
    else:
        df = pd.read_sql_query("""
        SELECT announcements.*, users.full_name as author, semesters.name as semester
        FROM announcements
        LEFT JOIN users ON announcements.created_by = users.id
        LEFT JOIN semesters ON announcements.semester_id = semesters.id
        WHERE announcements.expires_at IS NULL OR announcements.expires_at >= ?
        ORDER BY announcements.created_at DESC
        """, conn, params=(current_time,))
    
    return df
# ================= SEMESTERS =================

def create_(title, message, semester_id, priority, user_id):
    """
    Create a new 
    Returns: (success, message)
    """
    try:
        c.execute("""
        INSERT INTO s(title, message, semester_id, created_by, created_at, priority)
        VALUES(?,?,?,?,?,?)
        """, (
            title.strip(),
            message.strip(),
            int(semester_id) if semester_id else None,
            int(user_id),
            str(datetime.now(NST)),
            priority
        ))
        
        conn.commit()
        return True, " created successfully"
    except Exception as e:
        return False, "Error: {}".format(str(e))


def get_s_for_semester(semester_id=None):
    """
    Get s for a specific semester or all
    """
    if semester_id:
        df = pd.read_sql_query("""
        SELECT s.*, users.full_name as author, semesters.name as semester
        FROM s
        LEFT JOIN users ON s.created_by = users.id
        LEFT JOIN semesters ON s.semester_id = semesters.id
        WHERE s.semester_id=? OR s.semester_id IS NULL
        ORDER BY s.created_at DESC
        """, conn, params=(int(semester_id),))
    else:
        df = pd.read_sql_query("""
        SELECT s.*, users.full_name as author, semesters.name as semester
        FROM s
        LEFT JOIN users ON s.created_by = users.id
        LEFT JOIN semesters ON s.semester_id = semesters.id
        ORDER BY s.created_at DESC
        """, conn)
    
    return df
# ================= DATABASE =================

DB_PATH = "data/lecturer.db"
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
c = conn.cursor()

# USERS
c.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT,
    username TEXT UNIQUE,
    password TEXT,
    role TEXT,
    semester_id INTEGER
)
""")
# Safe auto-migration for existing users table
try:
    c.execute("ALTER TABLE users ADD COLUMN email TEXT")
    conn.commit()
except:
    pass # Column already exists
# SEMESTERS
c.execute("""
CREATE TABLE IF NOT EXISTS semesters(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE
)
""")

# SUBJECTS
c.execute("""
CREATE TABLE IF NOT EXISTS subjects(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    semester_id INTEGER
)
""")

# ASSIGNMENTS
c.execute("""
CREATE TABLE IF NOT EXISTS assignments(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    subject_id INTEGER,
    deadline TEXT,
    question_file TEXT,
    rubric TEXT
)
""")

# Safe auto-migration for existing databases
try:
    c.execute("ALTER TABLE assignments ADD COLUMN rubric TEXT")
    conn.commit()
except:
    pass # Column already exists

# SUBMISSIONS
c.execute("""
CREATE TABLE IF NOT EXISTS submissions(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    assignment_id INTEGER,
    student_id INTEGER,
    submission_time TEXT,
    submission_file TEXT,
    marks TEXT,
    ai_summary TEXT
)
""")
# STUDY MATERIALS
c.execute("""
CREATE TABLE IF NOT EXISTS study_materials(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    subject_id INTEGER,
    semester_id INTEGER,
    file_path TEXT,
    description TEXT,
    upload_date TEXT,
    uploaded_by INTEGER
)
""")
# --- INTERNAL MARKS & SCHEME TABLES ---
# 1. Stores the 'Rules' for each subject
c.execute("""
CREATE TABLE IF NOT EXISTS subject_schemes(
    subject_id INTEGER PRIMARY KEY,
    theory_full_marks REAL DEFAULT 40,
    prac_full_marks REAL DEFAULT 25,
    t_weight_att REAL DEFAULT 0.10,
    t_weight_hw REAL DEFAULT 0.25,
    t_weight_other REAL DEFAULT 0.15,
    t_weight_mid REAL DEFAULT 0.25,
    t_weight_final REAL DEFAULT 0.25,
    p_weight_att REAL DEFAULT 0.20,
    p_weight_perf REAL DEFAULT 0.20,
    p_weight_report REAL DEFAULT 0.20,
    p_weight_test REAL DEFAULT 0.20,
    p_weight_viva REAL DEFAULT 0.20,
    FOREIGN KEY(subject_id) REFERENCES subjects(id)
)
""")

# 2. Stores actual student performance data
c.execute("""
CREATE TABLE IF NOT EXISTS student_marks(
    student_id INTEGER,
    subject_id INTEGER,
    t_att_present INTEGER DEFAULT 0,
    t_att_total INTEGER DEFAULT 0,
    t_mid_raw REAL DEFAULT 0,
    t_final_raw REAL DEFAULT 0,
    t_other_raw REAL DEFAULT 0,
    t_grace REAL DEFAULT 0,
    p_att_present INTEGER DEFAULT 0,
    p_att_total INTEGER DEFAULT 0,
    p_perf_raw REAL DEFAULT 0,
    p_report_raw REAL DEFAULT 0,
    p_test_raw REAL DEFAULT 0,
    p_viva_raw REAL DEFAULT 0,
    PRIMARY KEY (student_id, subject_id),
    FOREIGN KEY(student_id) REFERENCES users(id),
    FOREIGN KEY(subject_id) REFERENCES subjects(id)
)
""")
conn.commit()
# --- SAFE AUTO-MIGRATION FOR EXISTING STUDENT_MARKS TABLE ---
try:
    c.execute("ALTER TABLE student_marks ADD COLUMN t_hw_raw REAL DEFAULT 0")
    conn.commit()
except Exception:
    pass  # Column already exists

try:
    c.execute("ALTER TABLE student_marks ADD COLUMN t_mid_raw REAL DEFAULT 0")
    conn.commit()
except Exception:
    pass

try:
    c.execute("ALTER TABLE student_marks ADD COLUMN t_final_raw REAL DEFAULT 0")
    conn.commit()
except Exception:
    pass

try:
    c.execute("ALTER TABLE student_marks ADD COLUMN t_other_raw REAL DEFAULT 0")
    conn.commit()
except Exception:
    pass

try:
    c.execute("ALTER TABLE student_marks ADD COLUMN t_grace REAL DEFAULT 0")
    conn.commit()
except Exception:
    pass
#========ANNOUNCEMENTS======================
c.execute("""
CREATE TABLE IF NOT EXISTS s(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    message TEXT,
    semester_id INTEGER,
    created_by INTEGER,
    created_at TEXT,
    priority TEXT
)
""")
try:
    c.execute("ALTER TABLE announcements ADD COLUMN expires_at TEXT")
    conn.commit()
except Exception:
    pass

    
conn.commit()


conn.commit()
conn.commit()

# ================= PASSWORD HELPERS =================

def hash_password(p):
    return bcrypt.hashpw(p.encode(), bcrypt.gensalt()).decode()

def check_password(p, hashed):
    try:
        return bcrypt.checkpw(p.encode(), hashed.encode())
    except:
        return False

# ================= DEFAULT LECTURER =================

# 1. Pull the secure credentials from your Streamlit vault
secure_username = st.secrets["admin_setup"]["username"]
secure_password = st.secrets["admin_setup"]["password"]

# 2. Check if THIS secure user already exists in the database
admin_exists = pd.read_sql_query(
    "SELECT * FROM users WHERE username=?",
    conn,
    params=(secure_username,)
)

# 3. If they don't exist yet, create the account!
if admin_exists.empty:
    c.execute("""
    INSERT INTO users(full_name, username, password, role, semester_id)
    VALUES(?,?,?,?,?)
    """, (
        "Administrator",
        secure_username,
        hash_password(secure_password),
        "lecturer",
        None
    ))
    conn.commit()
try:
    c.execute("DELETE FROM users WHERE username= 'admin'")
    conn.commit()
except Exception:
    pass
    
# ================= SESSION =================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.role = None
    st.session_state.username = None

# ================= SESSION SECURITY =================

import time

# Session timeout in seconds (30 minutes)
SESSION_TIMEOUT = 1800

def check_session_timeout():
    """
    Check if session has timed out
    Returns: True if session is valid, False if timed out
    """
    if "last_activity" not in st.session_state:
        st.session_state.last_activity = time.time()
        return True
    
    current_time = time.time()
    elapsed = current_time - st.session_state.last_activity
    
    if elapsed > SESSION_TIMEOUT:
        return False  # Session expired
    
    # Update last activity time
    st.session_state.last_activity = current_time
    return True


def require_login():
    """
    Check login and session validity
    """
    if not st.session_state.get("logged_in", False):
        st.error("🔒 Please login to access this page")
        st.stop()
    
    if not check_session_timeout():
        st.warning("⏰ Your session has expired due to inactivity. Please login again.")
        st.session_state.clear()
        st.rerun()
# ================= LOGIN =================

if not st.session_state.logged_in:

    st.markdown("""
        <div style='text-align: center; padding-bottom: 20px;'>
            <h1 style='color: #004b87; font-size: 3em; margin-bottom: 0px;'>🌊 THE N-STREAMLINES</h1>
            <p style='color: #555; font-size: 1.2em; font-weight: 500; margin-top: 5px;'>
                Developed by Nirajan Katuwal
            </p>
        </div>
        """, unsafe_allow_html=True)
    #-------------------------------------------
    with st.container(border=True):
        user = st.text_input("Username")
        pw = st.text_input("Password", type="password")

        if st.button("Enter the Flow"):

            res = pd.read_sql_query(
                "SELECT * FROM users WHERE username=?",
                conn,
                params=(user,)
            )

            if not res.empty and check_password(pw, res.iloc[0]["password"]):
                st.session_state.logged_in = True
                st.session_state.user_id = res.iloc[0]["id"]
                st.session_state.role = res.iloc[0]["role"]
                st.session_state.username = res.iloc[0]["username"]
                st.session_state.semester_id = res.iloc[0]["semester_id"]
                st.session_state.full_name = res.iloc[0]["full_name"]
                st.session_state.show_splash = True
                st.rerun()
            else:
                st.error("Invalid credentials")

        st.stop()
# =====================================================================
# IF LOGGED IN, THE DASHBOARD STARTS HERE
# =====================================================================

# ========== 1. TIME & GREETING SETUP ==========
now_nst = datetime.now(NST)
current_hour = now_nst.hour

if current_hour < 12:
    greeting = "🌅 Good Morning"
elif 12 <= current_hour < 18:
    greeting = "☀️ Good Afternoon"
else:
    greeting = "🌙 Good Evening"

user_name = st.session_state.full_name
current_date = now_nst.strftime("%A, %B %d, %Y")
current_time = now_nst.strftime("%I:%M %p")


# ========== 2. THE WELCOME SPLASH SCREEN ==========
if st.session_state.get("show_splash"):
    # Push it down to the center of the screen
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    
    # I used your #004b87 blue color to match your login screen!
    st.markdown(f"<h1 style='text-align: center; color: #004b87;'>{greeting}, {user_name}!</h1>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align: center; color: #555555;'>{current_date} &nbsp;|&nbsp; {current_time} (NST)</h3>", unsafe_allow_html=True)
    
    with st.spinner("Loading your secure workspace..."):
        time.sleep(2.5) 
        
    # Turn off the splash screen so it doesn't loop forever
    st.session_state.show_splash = False
    st.rerun()
    
    
# ========== 3. THE MAIN DASHBOARD HEADER ==========
else:
    # This draws the small header at the top
    header_col1, header_col2 = st.columns([2, 1])
    
    with header_col1:
        st.markdown(f"### {greeting}, {user_name}!")
        
    with header_col2:
        st.markdown(f"""
        <div style='text-align: right; color: #555555;'>
            <strong>{current_date}</strong><br>
            {current_time} (NST)
        </div>
        """, unsafe_allow_html=True)
        
    st.divider()

    # =================================================================
    # ALL YOUR SIDEBAR AND TAB CODE SHOULD CONTINUE BELOW THIS LINE
    # =================================================================
#=================GREETING FUNCTION===============
def get_greeting():
    """Returns a greeting based on current Nepal Standard Time"""
    current_hour = datetime.now(NST).hour
    
    if current_hour < 12:
        return "Good morning ☀️"
    elif 12 <= current_hour < 18:
        return "Good afternoon 🌤️"
    else:
        return "Good evening 🌙"
# ================= SYSTEM & SIDEBAR =================

#check session timeout
require_login()

with st.sidebar:
    st_autorefresh(interval=60000, key="sidebar_clock_refresh")
    sidebar_time = datetime.now(NST).strftime ("%b %d, %y | %I:%M %p")
    st.markdown(f'<div class="sidebar-clock">🕒 {sidebar_time}</div>', unsafe_allow_html=True)
    st.divider()
    greeting = get_greeting()
    display_name = st.session_state.get('full_name', st.session_state.username)
    st.markdown(f"### 👤 {display_name}")
    st.markdown(f"*{greeting}*")
    st.caption(f"Role: {str(st.session_state.role).capitalize()}")
    
    st.divider()
    
    if st.button("Logout", use_container_width=True):
        st.session_state.clear()
        st.rerun()

    # 2. Lecturer Emergency Controls
    if st.session_state.role == "lecturer":
        with st.expander("⚙️ Danger Zone"):
            if st.button("🧨 Wipe Database", use_container_width=True):
                tables = ["users", "submissions", "assignments", "subjects", "semesters"]
                for t in tables: c.execute(f"DROP TABLE IF EXISTS {t}")
                conn.commit(); st.rerun()

    # 3. Global Developer Branding (Pushed to the bottom)
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    
    st.markdown("""
        <div style='text-align: center; padding: 15px; background-color: #ffffff; border: 1px solid #e1e4e8; border-radius: 10px; border-top: 4px solid #004b87;'>
            <h4 style='color: #004b87; margin-bottom: 5px; font-size: 1.1em;'>🌊 The N-Streamlines</h4>
            <p style='font-size: 0.85em; color: #555; margin-bottom: 10px; line-height: 1.4;'>
                Advanced Hydro-Informatics &<br>Learning Management
            </p>
            <div style='background-color: #f4f7f9; padding: 8px; border-radius: 5px;'>
                <p style='font-size: 0.8em; color: #333; margin-bottom: 0;'>
                    Developed & Architected by<br>
                    <strong>Er. Nirajan Katuwal</strong>
                </p>
            </div>
            <p style='font-size: 0.7em; color: #999; margin-top: 10px; margin-bottom: 0;'>
                © 2026 | Version 1.0.0 Pro
            </p>
        </div>
    """, unsafe_allow_html=True)

role = st.session_state.role

# ================= AI FUNCTIONS =================

def vision_grade(pdf_path, rubric):
    try:
        import google.generativeai as genai
        from PIL import Image
        
        #CONFIGURE WITH api KEY
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

        #CONVERT pdf TO IMAGES
        images = convert_from_path(pdf_path)

        #Use Gemini Flash Model
        model=genai.GenerativeModel('gemini-3-flash-preview')

        #prepare the text prompt
        prompt = """
You are a strict civil engineering professor.

MODEL ANSWER/Rubric:
{}

#please grade the submitted assignment shown in the images.

Grade the assignment and Return your response in EXACTLY this format:
FINAL_MARKS: X/10
FEEDBACK:
- Point 1
- Point 2
- Point #
Now grade the assignment shown the images below:""".format(rubric)

        #Prepare content-text first, then PIL images directly
        content_parts = [prompt]

        #ADD images (limit to first 5 pages to avoid token limits)
        for idx,img in enumerate(images[:5]):
            content_parts.append(img)
        #Generate Response
        response = model.generate_content(content_parts)
        if response and hasattr(response, 'text'):
            return response.text
        else:
            return "Error: AI returned empty response"
            
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return "Error: {}\n\nDetails:\n{}".format(str(e), error_details)

def extract_marks(text):
    """
    Extract marks from AI response text.
    Returns aninteger between 1-10, or None if not found.
    """
    if not text:
        return None
    #convert to string in case it's not
    text = str(text)
    
    #Try multiple patterns to extract marks 
    patterns = [
        r"FINAL_MARKS:\s*(|d+)/10",
        r"FINAL MARKS:\s*(\d+)/10",
        r"Marks:\s*(\d+)/10",
        r"Score:\s*(\d+)/10",
        r"(\d+)\s*/\s*10"
    ]

    for pattern in patterns:
        m = re.search(pattern, text, re.IGNORECASE)
        
        if m:
            try:
                marks = int(m.group(1))
                #Ensure marks are within valid range
                if 0 <= marks <=10:
                    return marks
            except (ValueError, IndexError):
                continue
    return none
def apply_watermark(file_path, watermark_text="🌊 The N-Streamlines | Er. Nirajan Katuwal | Do Not Distribute"):
    """Stamps a watermark on every page of a PDF."""
    try:
        doc = fitz.open(file_path)
        for page in doc:
            page_rect = page.rect
            x_position = 30
            y_position = page_rect.height - 30
            
            page.insert_text(
                (x_position, y_position),
                watermark_text,
                fontsize=12,
                color=(0.6, 0.6, 0.6), 
                fill_opacity=0.5,      
                overlay=True           
            )
        temp_path = file_path + "_wm.pdf"
        doc.save(temp_path)
        doc.close()
        os.replace(temp_path, file_path)
    except Exception as e:
        st.error(f"Watermark Engine Error: {e}")    

#===================PUSH Email===============================
def send_email_notification(target_semester_id, subject, message_body):
    """Fetches student emails and sends a secure BCC email broadcast."""
    
    # 1. Fetch student emails for this semester
    if target_semester_id:
        df = pd.read_sql_query("SELECT email FROM users WHERE role='student' AND semester_id=? AND email IS NOT NULL AND email != ''", conn, params=(int(target_semester_id),))
    else:
        df = pd.read_sql_query("SELECT email FROM users WHERE role='student' AND email IS NOT NULL AND email != ''", conn)
    
    emails = df['email'].tolist()
    if not emails:
        return False, "No valid student emails found."

    # 2. Your Platform Credentials (Update these!)
    SENDER_EMAIL = "nstreamlines@gmail.com" 
    APP_PASSWORD = "baqz gkqs yyiz ijep"

    try:
        # 3. Construct the Email
        msg = MIMEMultipart()
        msg['From'] = f"The N-Streamlines <{SENDER_EMAIL}>"
        msg['Subject'] = subject
        msg.attach(MIMEText(message_body, 'plain'))
        
        # 4. Connect to Gmail and Send
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, APP_PASSWORD)
        
        # We send as BCC to protect student privacy!
        server.sendmail(SENDER_EMAIL, emails, msg.as_string())
        server.quit()
        return True, f"Emailed {len(emails)} students."
    except Exception as e:
        return False, f"Email error: {str(e)}"

# ================= DEADLINE HELPER FUNCTIONS =================

def get_deadline_status(deadline_str):
    """
    Calculate days until deadline and return status
    Returns: (days_remaining, status, color)
    """
    from datetime import datetime, timedelta
    
    try:
        # Parse deadline
        deadline = datetime.strptime(deadline_str, "%Y-%m-%d")
        today = datetime.now(NST)
        
        # Calculate difference
        days_remaining = (deadline - today).days
        
        # Determine status
        if days_remaining < 0:
            return days_remaining, "Overdue", "🔴"
        elif days_remaining == 0:
            return days_remaining, "Due Today", "🟠"
        elif days_remaining <= 3:
            return days_remaining, "Due Soon", "🟡"
        elif days_remaining <= 7:
            return days_remaining, "This Week", "🟢"
        else:
            return days_remaining, "Upcoming", "🔵"
    except:
        return None, "Unknown", "⚪"


def format_deadline_display(deadline_str):
    """
    Format deadline string for display with countdown
    """
    days, status, color = get_deadline_status(deadline_str)
    
    if days is None:
        return "{}  {}".format(color, deadline_str)
    elif days < 0:
        return "{}  {} ({} days overdue)".format(color, deadline_str, abs(days))
    elif days == 0:
        return "{}  {} (Due Today!)".format(color, deadline_str)
    elif days == 1:
        return "{}  {} (Tomorrow)".format(color, deadline_str)
    else:
        return "{}  {} ({} days left)".format(color, deadline_str, days)
# ================= FILE CLEANUP UTILITIES =================

def cleanup_orphaned_files():
    """
    Clean up files that exist on disk but not in database
    Returns: (files_deleted, space_freed_mb)
    """
    deleted_count = 0
    space_freed = 0
    
    # Get all files referenced in database
    db_files = set()
    
    # 1. Assignment question files
    assignments = pd.read_sql_query("SELECT question_file FROM assignments WHERE question_file IS NOT NULL AND question_file != ''", conn)
    for _, row in assignments.iterrows():
        if row['question_file']:
            db_files.add(row['question_file'])
    
    # 2. Submission files
    submissions = pd.read_sql_query("SELECT submission_file FROM submissions WHERE submission_file IS NOT NULL AND submission_file != ''", conn)
    for _, row in submissions.iterrows():
        if row['submission_file']:
            db_files.add(row['submission_file'])
    
    # 3. Study material files
    materials = pd.read_sql_query("SELECT file_path FROM study_materials WHERE file_path IS NOT NULL AND file_path != ''", conn)
    for _, row in materials.iterrows():
        if row['file_path']:
            db_files.add(row['file_path'])
    
    # Check each folder for orphaned files
    folders = ['assignment_files', 'submission_files', 'study_materials']
    
    for folder in folders:
        if os.path.exists(folder):
            for filename in os.listdir(folder):
                file_path = os.path.join(folder, filename)
                
                # If file exists on disk but not in database
                if file_path not in db_files and os.path.isfile(file_path):
                    try:
                        file_size = os.path.getsize(file_path)
                        os.remove(file_path)
                        deleted_count += 1
                        space_freed += file_size
                    except Exception as e:
                        st.warning("Could not delete {}: {}".format(file_path, str(e)))
    
    space_freed_mb = space_freed / (1024 * 1024)  # Convert to MB
    return deleted_count, round(space_freed_mb, 2)


def get_storage_stats():
    """
    Get storage usage statistics
    Returns: dict with folder sizes
    """
    stats = {}
    
    folders = {
        'assignment_files': 'Assignment Questions',
        'submission_files': 'Student Submissions',
        'study_materials': 'Study Materials',
        'data': 'Database Files'
    }
    
    for folder, label in folders.items():
        if os.path.exists(folder):
            total_size = 0
            file_count = 0
            
            for dirpath, dirnames, filenames in os.walk(folder):
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename)
                    if os.path.isfile(file_path):
                        try:
                            total_size += os.path.getsize(file_path)
                            file_count += 1
                        except:
                            continue
            
            stats[label] = {
                'size_mb': round(total_size / (1024 * 1024), 2),
                'file_count': file_count
            }
    
    return stats
# ================= FILE VALIDATION & SECURITY =================

# Configuration constants
MAX_FILE_SIZE_MB = 25  # Maximum file size in MB
ALLOWED_ASSIGNMENT_TYPES = ['pdf']
ALLOWED_SUBMISSION_TYPES = ['pdf']
ALLOWED_MATERIAL_TYPES = ['pdf', 'docx', 'pptx', 'zip', 'jpg', 'png']

def validate_file_upload(uploaded_file, allowed_types, max_size_mb=MAX_FILE_SIZE_MB):
    """
    Validate uploaded file for type and size
    Returns: (is_valid, error_message)
    """
    if uploaded_file is None:
        return False, "No file uploaded"
    
    # Check file extension
    file_extension = uploaded_file.name.split('.')[-1].lower()
    if file_extension not in allowed_types:
        return False, "Invalid file type. Allowed: {}".format(', '.join(allowed_types))
    
    # Check file size
    file_size_mb = uploaded_file.size / (1024 * 1024)
    if file_size_mb > max_size_mb:
        return False, "File too large! Maximum size: {} MB (Your file: {:.2f} MB)".format(max_size_mb, file_size_mb)
    
    # Check if file is actually a PDF (magic number check for PDFs)
    if file_extension == 'pdf':
        uploaded_file.seek(0)
        header = uploaded_file.read(5)
        uploaded_file.seek(0)
        if header != b'%PDF-':
            return False, "File appears to be corrupted or not a valid PDF"
    
    return True, "File is valid"


def safe_file_operation(operation, *args, **kwargs):
    """
    Wrapper for safe file operations with error handling
    Returns: (success, result_or_error_message)
    """
    try:
        result = operation(*args, **kwargs)
        return True, result
    except PermissionError:
        return False, "Permission denied. File may be in use."
    except FileNotFoundError:
        return False, "File not found."
    except Exception as e:
        return False, "Error: {}".format(str(e))


def check_deadline_passed(deadline_str):
    """
    Check if deadline has passed
    Returns: (is_late, message)
    """
    try:
        deadline_date = datetime.strptime(str(deadline_str), '%Y-%m-%d').date()
        current_date = datetime.now(NST).date()
        
        if current_date > deadline_date:
            days_late = (current_date - deadline_date).days
            return True, "Deadline passed {} days ago".format(days_late)
        else:
            return False, "Deadline not passed"
    except:
        return False, "Invalid deadline format"

# ================= DATABASE BACKUP SYSTEM (SAFE VERSION) =================

def create_database_backup():
    """
    Create a timestamped backup of the database
    Returns: (success, message)
    """
    try:
        import shutil
        
        # Create backup directory
        backup_dir = "data/backups"
        os.makedirs(backup_dir, exist_ok=True)
        
        # Generate backup filename with timestamp
        timestamp = datetime.now(NST).strftime("%Y%m%d_%H%M%S")
        backup_filename = "lecturer_backup_{}.db".format(timestamp)
        backup_path = os.path.join(backup_dir, backup_filename)
        
        # Copy database file
        # SQLite allows copying while database is in use
        shutil.copy2(DB_PATH, backup_path)
        
        # Verify backup was created
        if not os.path.exists(backup_path):
            return False, "Backup file was not created"
        
        # Get backup file size
        backup_size = os.path.getsize(backup_path) / 1024  # KB
        
        # Clean old backups (keep only last 10)
        cleanup_old_backups(backup_dir, keep_count=10)
        
        return True, "Backup created: {} ({:.2f} KB)".format(backup_filename, backup_size)
    
    except PermissionError:
        return False, "Permission denied. Database may be locked."
    except Exception as e:
        return False, "Backup failed: {}".format(str(e))


def cleanup_old_backups(backup_dir, keep_count=10):
    """
    Keep only the most recent N backups
    """
    try:
        if not os.path.exists(backup_dir):
            return
        
        backups = []
        for filename in os.listdir(backup_dir):
            if filename.startswith("lecturer_backup_") and filename.endswith(".db"):
                file_path = os.path.join(backup_dir, filename)
                try:
                    mod_time = os.path.getmtime(file_path)
                    backups.append((file_path, mod_time))
                except:
                    continue
        
        # Sort by modification time (newest first)
        backups.sort(key=lambda x: x[1], reverse=True)
        
        # Delete old backups
        for file_path, _ in backups[keep_count:]:
            try:
                os.remove(file_path)
            except:
                pass
    
    except:
        pass  # Silently fail


def restore_database_from_backup(backup_path):
    """
    Restore database from a backup file
    
    ⚠️ WARNING: This will replace the current database!
    The app needs to be restarted after restore.
    
    Returns: (success, message)
    """
    try:
        import shutil
        
        if not os.path.exists(backup_path):
            return False, "Backup file not found: {}".format(backup_path)
        
        # Verify backup file is valid
        backup_size = os.path.getsize(backup_path)
        if backup_size < 1000:  # Less than 1KB is suspicious
            return False, "Backup file appears to be corrupted (too small)"
        
        # Create emergency backup of current database
        timestamp = datetime.now(NST).strftime("%Y%m%d_%H%M%S")
        emergency_backup = "{}.before_restore_{}".format(DB_PATH, timestamp)
        
        try:
            shutil.copy2(DB_PATH, emergency_backup)
        except:
            return False, "Could not create emergency backup of current database"
        
        # Perform restore
        try:
            shutil.copy2(backup_path, DB_PATH)
        except PermissionError:
            return False, "Permission denied. Close all database connections first."
        except Exception as e:
            # Try to restore emergency backup
            try:
                shutil.copy2(emergency_backup, DB_PATH)
            except:
                pass
            return False, "Restore failed: {}".format(str(e))
        
        return True, "✅ Database restored from backup. IMPORTANT: Please RESTART the app (refresh page) to reconnect to the restored database."
    
    except Exception as e:
        return False, "Restore error: {}".format(str(e))


def get_backup_list():
    """
    Get list of available backups with metadata
    Returns: list of dicts with backup info
    """
    backup_dir = "data/backups"
    backups = []
    
    if not os.path.exists(backup_dir):
        return backups
    
    for filename in os.listdir(backup_dir):
        if filename.startswith("lecturer_backup_") and filename.endswith(".db"):
            file_path = os.path.join(backup_dir, filename)
            
            try:
                size_kb = os.path.getsize(file_path) / 1024
                mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                
                backups.append({
                    'filename': filename,
                    'path': file_path,
                    'size_kb': round(size_kb, 2),
                    'date': mod_time.strftime("%Y-%m-%d %H:%M:%S")
                })
            except:
                continue
    
    # Sort by date (newest first)
    backups.sort(key=lambda x: x['date'], reverse=True)
    
    return backups

# ================= CONFIRMATION DIALOGS =================

def confirm_delete(item_name, item_type="item"):
    """
    Create a two-step confirmation for delete actions
    Returns: True if confirmed, False otherwise
    """
    confirm_key = "confirm_delete_{}".format(item_name.replace(" ", "_"))
    
    if confirm_key not in st.session_state:
        st.session_state[confirm_key] = False
    
    if not st.session_state[confirm_key]:
        if st.button("🗑️ Delete {}".format(item_type), key="first_{}".format(confirm_key)):
            st.session_state[confirm_key] = True
            st.rerun()
        return False
    else:
        st.warning("⚠️ Are you sure? This cannot be undone!")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Yes, Delete", key="confirm_{}".format(confirm_key), type="primary"):
                st.session_state[confirm_key] = False
                return True
        with col2:
            if st.button("❌ Cancel", key="cancel_{}".format(confirm_key)):
                st.session_state[confirm_key] = False
                st.rerun()
        return False
# ================= SEARCH FUNCTIONALITY =================

def search_students(query, semester_id=None):
    """
    Search students by name or username
    Returns: DataFrame of matching students
    """
    query = query.strip().lower()
    
    if not query:
        return pd.DataFrame()
    
    if semester_id:
        results = pd.read_sql_query("""
        SELECT users.id, users.full_name, users.username, semesters.name as semester
        FROM users
        LEFT JOIN semesters ON users.semester_id = semesters.id
        WHERE users.role='student' 
        AND users.semester_id=?
        AND (LOWER(users.full_name) LIKE ? OR LOWER(users.username) LIKE ?)
        ORDER BY users.full_name ASC
        """, conn, params=(semester_id, '%{}%'.format(query), '%{}%'.format(query)))
    else:
        results = pd.read_sql_query("""
        SELECT users.id, users.full_name, users.username, semesters.name as semester
        FROM users
        LEFT JOIN semesters ON users.semester_id = semesters.id
        WHERE users.role='student' 
        AND (LOWER(users.full_name) LIKE ? OR LOWER(users.username) LIKE ?)
        ORDER BY users.full_name ASC
        """, conn, params=('%{}%'.format(query), '%{}%'.format(query)))
    
    return results


def search_assignments(query):
    """
    Search assignments by title or subject
    Returns: DataFrame of matching assignments
    """
    query = query.strip().lower()
    
    if not query:
        return pd.DataFrame()
    
    results = pd.read_sql_query("""
    SELECT 
        assignments.id,
        assignments.title,
        subjects.name as subject,
        semesters.name as semester,
        assignments.deadline
    FROM assignments
    JOIN subjects ON assignments.subject_id = subjects.id
    JOIN semesters ON subjects.semester_id = semesters.id
    WHERE LOWER(assignments.title) LIKE ? OR LOWER(subjects.name) LIKE ?
    ORDER BY assignments.deadline DESC
    """, conn, params=('%{}%'.format(query), '%{}%'.format(query)))
    
    return results
# ================= EDIT ASSIGNMENT =================

def update_assignment(assignment_id, new_title, new_deadline,new_rubric):
    """
    Update assignment title, deadline, and rubric
    Returns: (success, message)
    """
    try:
        c.execute("""
        UPDATE assignments 
        SET title=?, deadline=?,rubric=?
        WHERE id=?
        """, (new_title.strip(), str(new_deadline), new_rubric.strip(), int(assignment_id)))
        
        conn.commit()
        return True, "Assignment updated successfully"
    except Exception as e:
        return False, "Update failed: {}".format(str(e))
# ================= STUDENT PROFILE =================

def get_student_profile(student_id):
    """
    Get complete student profile with all statistics
    Returns: dict with student data
    """
    try:
        # Basic info
        student_info = pd.read_sql_query("""
        SELECT users.*, semesters.name as semester
        FROM users
        LEFT JOIN semesters ON users.semester_id = semesters.id
        WHERE users.id=?
        """, conn, params=(int(student_id),))
        
        if student_info.empty:
            return None
        
        # Submission stats
        submissions = pd.read_sql_query("""
        SELECT 
            subjects.name as subject,
            assignments.title as assignment,
            assignments.deadline,
            submissions.submission_time,
            submissions.marks
        FROM submissions
        JOIN assignments ON submissions.assignment_id = assignments.id
        JOIN subjects ON assignments.subject_id = subjects.id
        WHERE submissions.student_id=?
        ORDER BY submissions.submission_time DESC
        """, conn, params=(int(student_id),))
        
        # Calculate statistics
        total_submissions = len(submissions)
        graded = submissions[submissions['marks'].notna() & (submissions['marks'] != '')]
        total_graded = len(graded)
        
        if total_graded > 0:
            graded['marks_numeric'] = pd.to_numeric(graded['marks'], errors='coerce')
            avg_marks = graded['marks_numeric'].mean()
            highest = graded['marks_numeric'].max()
            lowest = graded['marks_numeric'].min()
        else:
            avg_marks = 0
            highest = 0
            lowest = 0
        
        return {
            'info': student_info.iloc[0].to_dict(),
            'submissions': submissions,
            'stats': {
                'total_submissions': total_submissions,
                'total_graded': total_graded,
                'average': round(avg_marks, 2) if total_graded > 0 else 0,
                'highest': highest,
                'lowest': lowest
            }
        }
    
    except Exception as e:
        st.error("Error loading profile: {}".format(str(e)))
        return None
# ... (End of Student Profile functions) ...

# ================= INTERNAL MARKS CALCULATION ENGINE (DYNAMIC VERSION) =================
def calculate_internal_theory(row, subject_id, db_conn):
    """
    Dynamically fetches subject configurations from the database and 
    calculates weighted theory marks with a strict 70% attendance gate.
    """
    # 1. Fetch weight scheme from database for the active subject
    scheme_df = pd.read_sql_query(
        "SELECT * FROM subject_schemes WHERE subject_id = ?", 
        db_conn, 
        params=(int(subject_id),)
    )
    
    # Fallback to standard defaults if no custom configuration exists yet
    if scheme_df.empty:
        scheme = {
            'theory_full_marks': 40.0,
            't_weight_att': 0.10, 't_weight_hw': 0.25, 't_weight_other': 0.15,
            't_weight_mid': 0.25, 't_weight_final': 0.25
        }
    else:
        scheme = scheme_df.iloc[0].to_dict()

    # 2. Attendance Score Calculation
    att_ratio = row['t_att_present'] / row['t_att_total'] if row['t_att_total'] > 0 else 0
    att_score = att_ratio * (scheme['theory_full_marks'] * scheme['t_weight_att'])
    
    # 3. Scale Raw Percentages (0-100) to Dynamic Scheme Weights
    hw_score = (row['t_hw_raw'] / 100) * (scheme['theory_full_marks'] * scheme['t_weight_hw'])
    mid_score = (row['t_mid_raw'] / 100) * (scheme['theory_full_marks'] * scheme['t_weight_mid'])
    final_score = (row['t_final_raw'] / 100) * (scheme['theory_full_marks'] * scheme['t_weight_final'])
    other_score = (row['t_other_raw'] / 100) * (scheme['theory_full_marks'] * scheme['t_weight_other'])
    
    raw_total = att_score + hw_score + mid_score + final_score + other_score
    
    # 4. Enforce 70% Attendance Gate for Grace Marks
    final_total = raw_total
    is_eligible_grace = att_ratio >= 0.70
    
    if is_eligible_grace and row['t_grace'] > 0:
        final_total += min(row['t_grace'], 5) 
        
    return round(final_total, 2), is_eligible_grace


def calculate_internal_practical(row, subject_id, db_conn):
    """
    Dynamically fetches subject configurations from the database and
    calculates weighted practical marks out of lab components.
    """
    # 1. Fetch weight scheme from database
    scheme_df = pd.read_sql_query(
        "SELECT * FROM subject_schemes WHERE subject_id = ?", 
        db_conn, 
        params=(int(subject_id),)
    )
    
    if scheme_df.empty:
        scheme = {
            'prac_full_marks': 25.0,
            'p_weight_att': 0.20, 'p_weight_perf': 0.20, 'p_weight_report': 0.20,
            'p_weight_test': 0.20, 'p_weight_viva': 0.20
        }
    else:
        scheme = scheme_df.iloc[0].to_dict()

    full_p = scheme['prac_full_marks']
    
    # 2. Component Math scaled to custom weight assignments
    att_ratio = row['p_att_present'] / row['p_att_total'] if row['p_att_total'] > 0 else 0
    att_score = att_ratio * (full_p * scheme['p_weight_att'])
    
    perf_score = (row['p_perf_raw'] / 100) * (full_p * scheme['p_weight_perf'])
    report_score = (row['p_report_raw'] / 100) * (full_p * scheme['p_weight_report'])
    test_score = (row['p_test_raw'] / 100) * (full_p * scheme['p_weight_test'])
    viva_score = (row['p_viva_raw'] / 100) * (full_p * scheme['p_weight_viva'])
    
    raw_total = att_score + perf_score + report_score + test_score + viva_score
    is_eligible = att_ratio >= 0.70
    
    return round(raw_total, 2), is_eligible
  
# ==========================================================
# ===================== LECTURER ============================
# ==========================================================

if role == "lecturer":

    tabs = st.tabs([
        "Dashboard",  
        "Semesters",
        "Subjects",
        "Assignments",
        "Submissions & AI",
        "Analytics",
        "Manage Students",
        "Study Materials",
        "Storage Management",
        "Student Profiles"
    ])
    
    # DASHBOARD
    with tabs[0]:
            
        st.title("📊 Dashboard")
            
        # ========== CREATE  ==========
        with st.expander("📢 Create New "):
                
            col_ann1, col_ann2 = st.columns([2, 1])
                
            with col_ann1:
                ann_title = st.text_input(" Title", key="ann_title")
                ann_message = st.text_area("Message", key="ann_message", height=100)
                
            with col_ann2:
                sems_ann = pd.read_sql_query("SELECT * FROM semesters", conn)
                ann_sem_options = ["All Semesters"] + sems_ann["name"].tolist()
                    
                ann_sem = st.selectbox("Target Audience", ann_sem_options, key="ann_sem")
                ann_priority = st.selectbox("Priority", ["Normal", "Important", "Urgent"], key="ann_priority")
                    
                # --- NEW TIMER DROPDOWN ADDED HERE ---
                timer_option = st.selectbox(
                    "Visibility Duration", 
                    ["Permanent (No Expiry)", "24 Hours", "3 Days", "1 Week"], 
                    key="ann_timer"
                )
                # -------------------------------------
                
            if st.button("📢 Post Announcement", type="primary"):
                if not ann_title.strip() or not ann_message.strip():
                    st.error("Title and message required")
                else:
                    sem_id = None
                    if ann_sem != "All Semesters":
                        sem_id = int(sems_ann[sems_ann["name"] == ann_sem]["id"].values[0])
                        
                    # --- NEW TIME CALCULATION ---
                    from datetime import timedelta # Ensure this is imported
                    if timer_option == "24 Hours":
                        calc_expiry = str(datetime.now(NST) + timedelta(days=1))
                    elif timer_option == "3 Days":
                        calc_expiry = str(datetime.now(NST) + timedelta(days=3))
                    elif timer_option == "1 Week":
                        calc_expiry = str(datetime.now(NST) + timedelta(days=7))
                    else:
                        calc_expiry = None
                    # ----------------------------

                    # Pass calc_expiry as the 6th argument
                    success, msg = create_announcement(
                        ann_title,
                        ann_message,
                        sem_id,
                        ann_priority,
                        st.session_state.user_id,
                        calc_expiry 
                    )
                        
                    if success:
                        with st.spinner("Broadcasting emails to students..."):
                            # Format the email content
                            email_subject = f"📢 The N-Streamlines: {ann_title}"
                            email_body = f"Hello,\n\nA new announcement has been posted by Er. Nirajan Katuwal:\n\nTitle: {ann_title}\nPriority: {ann_priority}\n\nMessage:\n{ann_message}\n\nPlease log into the platform to view the details."

                            # Fire the email engine
                            e_success, e_msg = send_email_notification(sem_id, email_subject, email_body)
                                
                        if e_success:
                            st.success(f"✅ {msg} & {e_msg}")
                        else:
                            st.warning(f"✅ {msg}, but emails were skipped: {e_msg}")
                            
                        st.rerun()
                    else:
                        st.error(f"❌ {msg}")
            
        st.divider()
        # Get all assignments
        all_assignments = pd.read_sql_query("""
        SELECT 
            assignments.id,
            assignments.title,
            assignments.deadline,
            subjects.name as subject,
            semesters.name as semester
        FROM assignments
        JOIN subjects ON assignments.subject_id = subjects.id
        JOIN semesters ON subjects.semester_id = semesters.id
        ORDER BY assignments.deadline ASC
        """, conn)
        
        if all_assignments.empty:
            st.info("No assignments created yet.")
        else:
            st.subheader("⏰ Assignment Deadlines Overview")
            
            # Categorize assignments
            overdue = []
            due_today = []
            due_soon = []
            upcoming = []
            
            for _, assignment in all_assignments.iterrows():
                days, status, color = get_deadline_status(assignment['deadline'])
                
                assignment_info = {
                    'title': assignment['title'],
                    'subject': assignment['subject'],
                    'semester': assignment['semester'],
                    'deadline': assignment['deadline'],
                    'days': days,
                    'status': status,
                    'color': color,
                    'id': assignment['id']
                }
                
                if status == "Overdue":
                    overdue.append(assignment_info)
                elif status == "Due Today":
                    due_today.append(assignment_info)
                elif status == "Due Soon" or status == "This Week":
                    due_soon.append(assignment_info)
                else:
                    upcoming.append(assignment_info)
            
            # Metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("🔴 Overdue", len(overdue))
            with col2:
                st.metric("🟠 Due Today", len(due_today))
            with col3:
                st.metric("🟡 Due This Week", len(due_soon))
            with col4:
                st.metric("🔵 Upcoming", len(upcoming))
            
            st.divider()
            
            # Show details
            if overdue:
                st.error("🔴 **OVERDUE ASSIGNMENTS**")
                for assign in overdue:
                    with st.expander("{} - {} ({})".format(assign['semester'], assign['subject'], assign['title'])):
                        st.write("**Deadline:** {}".format(assign['deadline']))
                        st.write("**Overdue by:** {} days".format(abs(assign['days'])))
                        
                        # Show submission stats
                        submissions = pd.read_sql_query("""
                        SELECT COUNT(*) as count FROM submissions
                        WHERE assignment_id=?
                        """, conn, params=(assign['id'],))
                        
                        st.metric("Submissions Received", submissions.iloc[0]['count'])
            
            if due_today:
                st.warning("🟠 **DUE TODAY**")
                for assign in due_today:
                    st.info("{} - {} - {}".format(assign['semester'], assign['subject'], assign['title']))
            
            if due_soon:
                st.info("🟡 **DUE THIS WEEK**")
                for assign in due_soon:
                    st.write("📌 {} - {} - {} ({} days left)".format(
                        assign['semester'],
                        assign['subject'],
                        assign['title'],
                        assign['days']
                    ))
            
            st.divider()
            
            # Submission statistics
            st.subheader("📈 Submission Statistics")
            
            for _, assignment in all_assignments.iterrows():
                # Count submissions
                total_submissions = pd.read_sql_query("""
                SELECT COUNT(*) as count FROM submissions
                WHERE assignment_id=?
                """, conn, params=(assignment['id'],)).iloc[0]['count']
                
                # Count total students in semester
                semester_id = pd.read_sql_query("""
                SELECT semester_id FROM subjects WHERE id=?
                """, conn, params=(assignment['subject'],))
                
                deadline_display = format_deadline_display(assignment['deadline'])
                
                with st.expander("{} - {} | {}".format(assignment['subject'], assignment['title'], deadline_display)):
                    col_a, col_b = st.columns(2)
                    
                    with col_a:
                        st.metric("Total Submissions", total_submissions)
                    
                    with col_b:
                        graded = pd.read_sql_query("""
                        SELECT COUNT(*) as count FROM submissions
                        WHERE assignment_id=? AND marks IS NOT NULL AND marks != ''
                        """, conn, params=(assignment['id'],)).iloc[0]['count']
                        
                        st.metric("Graded", graded)
    # SEMESTERS
    with tabs[1]:
        name = st.text_input("New Semester")

        if st.button("Add Semester"):
            if not name.strip():
                st.error("Semester name cannot be empty.")
            else:
                try:
                    c.execute("INSERT INTO semesters(name) VALUES(?)", (name.strip(),))
                    conn.commit()
                    st.success("✅ Semester Added")
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.warning("⚠️ Semester already exists.")

        st.dataframe(
            pd.read_sql_query("SELECT * FROM semesters ORDER BY name ASC", conn),
            use_container_width=True,
            hide_index=True
        )
        st.divider()
        st.subheader("Delete Semester")

        sems = pd.read_sql_query("SELECT * FROM semesters ORDER BY name ASC", conn) 
        if not sems.empty:
            semester_options={
                f"{row['name']} (ID:{row['id']})": row['id']
                for _, row in sems.iterrows()
            }

            selected_sem = st.selectbox(
                "select Semester to Delete",
                list(semester_options.keys()),
                key="delete_semester"
            )
            if st.button("Delete Selected Semester"):

                sem_id = semester_options[selected_sem]
                
                try:
                    deleted_files = 0
                    
                    # Step 1: Get all subjects in this semester
                    subject_ids = pd.read_sql_query(
                        "SELECT id FROM subjects WHERE semester_id=?",
                        conn,
                        params=(int(sem_id),)
                    )
                    
                    # Step 2: For each subject, delete all related files
                    for _, subject_row in subject_ids.iterrows():
                        
                        # Get all assignments for this subject
                        assignments = pd.read_sql_query(
                            "SELECT id, question_file FROM assignments WHERE subject_id=?",
                            conn,
                            params=(subject_row["id"],)
                        )
                        
                        # For each assignment
                        for _, assign_row in assignments.iterrows():
                            
                            # Delete all submission files
                            submissions = pd.read_sql_query(
                                "SELECT submission_file FROM submissions WHERE assignment_id=?",
                                conn,
                                params=(assign_row["id"],)
                            )
                            
                            for _, sub_row in submissions.iterrows():
                                if sub_row['submission_file'] and os.path.exists(sub_row['submission_file']):
                                    try:
                                        os.remove(sub_row['submission_file'])
                                        deleted_files += 1
                                    except:
                                        pass
                            
                            # Delete all submissions (database)
                            c.execute("DELETE FROM submissions WHERE assignment_id=?", (assign_row["id"],))
                            
                            # Delete assignment question file
                            if assign_row['question_file'] and os.path.exists(assign_row['question_file']):
                                try:
                                    os.remove(assign_row['question_file'])
                                    deleted_files += 1
                                except:
                                    pass
                        
                        # Delete all assignments for this subject
                        c.execute("DELETE FROM assignments WHERE subject_id=?", (subject_row["id"],))
                        
                        # Delete all study materials for this subject
                        materials = pd.read_sql_query(
                            "SELECT file_path FROM study_materials WHERE subject_id=?",
                            conn,
                            params=(subject_row["id"],)
                        )
                        
                        for _, mat_row in materials.iterrows():
                            if mat_row['file_path'] and os.path.exists(mat_row['file_path']):
                                try:
                                    os.remove(mat_row['file_path'])
                                    deleted_files += 1
                                except:
                                    pass
                        
                        c.execute("DELETE FROM study_materials WHERE subject_id=?", (subject_row["id"],))
                    
                    # Step 3: Delete all subjects
                    c.execute("DELETE FROM subjects WHERE semester_id=?", (sem_id,))
                    
                    # Step 4: Update students (set semester_id to NULL)
                    c.execute("UPDATE users SET semester_id=NULL WHERE semester_id=?", (sem_id,))
                    
                    # Step 5: Delete semester
                    c.execute("DELETE FROM semesters WHERE id=?", (sem_id,))
                    
                    conn.commit()
                    st.success("✅ Semester deleted! Removed {} files from disk.".format(deleted_files))
                    st.rerun()
                    
                except Exception as e:
                    st.error("Error deleting semester: {}".format(str(e)))
        # SUBJECTS
    with tabs[2]:  # Adjust index based on your setup
        
        st.title("📚 Subject Management")
        
        sems = pd.read_sql_query("SELECT * FROM semesters ORDER BY name ASC", conn)

        if sems.empty:
            st.warning("Please create a semester first.")
        else:
            # ========== ADD SUBJECT ==========
            st.subheader("➕ Add New Subject")
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                sem = st.selectbox("Select Semester", sems["name"], key="subject_semester")
                sem_id = int(sems[sems["name"] == sem]["id"].values[0])
            
            with col2:
                sub = st.text_input("Subject Name", key="subject_name", placeholder="e.g., Structural Analysis")
            
            if st.button("➕ Add Subject", use_container_width=True):
                if not sub.strip():
                    st.error("Subject name cannot be empty.")
                else:
                    try:
                        c.execute(
                            "INSERT INTO subjects(name,semester_id) VALUES(?,?)",
                            (sub.strip(), int(sem_id))
                        )
                        conn.commit()
                        st.success("✅ Subject '{}' added to {}".format(sub.strip(), sem))
                        st.rerun()
                    except Exception as e:
                        st.error("Error adding subject: {}".format(str(e)))
            
            st.divider()
            
            # ========== VIEW SUBJECTS ==========
            st.subheader("📋 Subjects for: {}".format(sem))
            
            subjects_for_sem = pd.read_sql_query(
                "SELECT * FROM subjects WHERE semester_id=? ORDER BY name ASC",
                conn,
                params=(int(sem_id),)
            )
            
            if subjects_for_sem.empty:
                st.info("No subjects found for this semester.")
            else:
                st.dataframe(
                    subjects_for_sem[['id', 'name']],
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "id": "Subject ID",
                        "name": "Subject Name"
                    }
                )
                
                st.info("📊 Total Subjects: **{}**".format(len(subjects_for_sem)))
            
            st.divider()
            
            # ========== DELETE SUBJECT ==========
            st.subheader("🗑️ Delete Subject")
            
            if not subjects_for_sem.empty:
                
                # Create options for deletion
                subject_options = {
                    "{} (ID: {})".format(row['name'], row['id']): row['id']
                    for _, row in subjects_for_sem.iterrows()
                }
                
                selected_subject = st.selectbox(
                    "Select Subject to Delete from {}".format(sem),
                    list(subject_options.keys()),
                    key="delete_subject_select"
                )
                
                col_warn1, col_warn2 = st.columns([2, 1])
                
                with col_warn1:
                    st.warning("⚠️ **Warning:** Deleting a subject will also delete:\n- All assignments under this subject\n- All submissions for those assignments")
                
                with col_warn2:
                    if st.button("🗑️ Confirm Delete Subject", type="primary", use_container_width=True):
                        
                        subject_id = subject_options[selected_subject]
                        
                        try:
                            # Get all assignment IDs for this subject
                            assignment_ids = pd.read_sql_query(
                                "SELECT id FROM assignments WHERE subject_id=?",
                                conn,
                                params=(int(subject_id),)
                            )
                            
                            # Delete submissions for each assignment
                            for _, row in assignment_ids.iterrows():
                                c.execute("DELETE FROM submissions WHERE assignment_id=?", (row["id"],))
                            
                            # Delete all assignments for this subject
                            c.execute("DELETE FROM assignments WHERE subject_id=?", (int(subject_id),))
                            
                            # Delete all study materials for this subject
                            materials = pd.read_sql_query(
                                "SELECT file_path FROM study_materials WHERE subject_id=?",
                                conn,
                                params=(int(subject_id),)
                            )
                            for _, mat in materials.iterrows():
                                if mat['file_path'] and os.path.exists(mat['file_path']):
                                    os.remove(mat['file_path'])
                            
                            c.execute("DELETE FROM study_materials WHERE subject_id=?", (int(subject_id),))
                            
                            # Finally, delete the subject
                            c.execute("DELETE FROM subjects WHERE id=?", (int(subject_id),))
                            
                            conn.commit()
                            st.success("✅ Subject deleted successfully!")
                            st.rerun()
                            
                        except Exception as e:
                            st.error("Error deleting subject: {}".format(str(e)))
            else:
                st.info("No subjects available to delete in this semester.")
            
            st.divider()
            
            # ========== ALL SUBJECTS DEBUG ==========
            with st.expander("🔍 View All Subjects (All Semesters)"):
                all_subjects_debug = pd.read_sql_query("""
                SELECT 
                    subjects.id as ID,
                    subjects.name as Subject,
                    semesters.name as Semester
                FROM subjects
                JOIN semesters ON subjects.semester_id = semesters.id
                ORDER BY semesters.name, subjects.name
                """, conn)
                
                if not all_subjects_debug.empty:
                    st.dataframe(all_subjects_debug, use_container_width=True, hide_index=True)
                else:
                    st.info("No subjects created yet.")
            # ================= DYNAMIC SCHEME CONFIGURATOR =================
            st.write("")
            with st.expander("⚙️ Advanced: Configure Subject Marking Schemes (Weightage Rules)"):
                all_subs = pd.read_sql_query("""
                    SELECT s.id, s.name, sem.name as semester 
                    FROM subjects s 
                    JOIN semesters sem ON s.semester_id = sem.id
                    ORDER BY sem.name, s.name
                """, conn)
                
                if all_subs.empty:
                    st.info("Please add subjects before configuring weightage distribution rules.")
                else:
                    sub_map = {f"{row['semester']} | {row['name']}": row['id'] for _, row in all_subs.iterrows()}
                    selected_target = st.selectbox("Choose Subject to Edit Rules", list(sub_map.keys()), key="scheme_sub_picker")
                    target_sub_id = sub_map[selected_target]
                    
                    # Load existing data from database if it exists, otherwise fall back to your classic standard values
                    exist_rule = pd.read_sql_query("SELECT * FROM subject_schemes WHERE subject_id=?", conn, params=(int(target_sub_id),))
                    
                    sc_theory = exist_rule.iloc[0]['theory_full_marks'] if not exist_rule.empty else 40.0
                    sc_prac = exist_rule.iloc[0]['prac_full_marks'] if not exist_rule.empty else 25.0
                    
                    cc1, cc2 = st.columns(2)
                    with cc1:
                        st.markdown("### 📝 Theory Weights")
                        f_theory = st.number_input("Theory Full Marks Allocation", min_value=0.0, max_value=100.0, value=float(sc_theory), key="sch_f_theory")
                        w_att = st.slider("Attendance Weight Ratio", 0.0, 1.0, 0.10, key="sch_w_att")
                        w_hw = st.slider("Homework/Assignment Weight Ratio", 0.0, 1.0, 0.25, key="sch_w_hw")
                        w_mid = st.slider("Mid-Term Assessment Weight Ratio", 0.0, 1.0, 0.25, key="sch_w_mid")
                        w_final = st.slider("Final Internal Exam Weight Ratio", 0.0, 1.0, 0.25, key="sch_w_final")
                        w_other = st.slider("Discipline/Other Continuous Weights", 0.0, 1.0, 0.15, key="sch_w_other")
                    with cc2:
                        st.markdown("### 🧪 Practical Weights")
                        f_prac = st.number_input("Practical Full Marks Allocation", min_value=0.0, max_value=100.0, value=float(sc_prac), key="sch_f_prac")
                    
                    # Validate that the coefficients sum to 1.0 total
                    total_ratio = w_att + w_hw + w_mid + w_final + w_other
                    if abs(total_ratio - 1.0) > 0.01:
                        st.warning(f"⚠️ Note: Theory distribution coefficients sum to {total_ratio:.2f}. For perfect scaling, ensure they sum precisely to 1.00.")
                    
                    if st.button("💾 Lock Weighting Schema Rules for Selected Subject", use_container_width=True, type="primary", key="save_scheme_btn"):
                        c.execute("""
                            INSERT INTO subject_schemes (
                                subject_id, theory_full_marks, prac_full_marks, t_weight_att, 
                                t_weight_hw, t_weight_other, t_weight_mid, t_weight_final
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            ON CONFLICT(subject_id) DO UPDATE SET
                                theory_full_marks=excluded.theory_full_marks,
                                prac_full_marks=excluded.prac_full_marks,
                                t_weight_att=excluded.t_weight_att,
                                t_weight_hw=excluded.t_weight_hw,
                                t_weight_other=excluded.t_weight_other,
                                t_weight_mid=excluded.t_weight_mid,
                               _final=excluded.t_weight_final
                        """, (int(target_sub_id), f_theory, f_prac, w_att, w_hw, w_other, w_mid, w_final))
                        conn.commit()
                        st.success(f"✅ Assessment mapping and report generation rules updated across all application engines for {selected_target}!")
                        st.rerun()

        # ASSIGNMENTS
    with tabs[3]:  # Adjust index based on your setup
        
        st.title("📝 Assignment Management")
        
        # ========== CREATE NEW ASSIGNMENT ==========
        st.subheader("➕ Create New Assignment")

        sems = pd.read_sql_query("SELECT * FROM semesters ORDER BY name ASC", conn)

        if sems.empty:
            st.warning("Please create a semester first.")
        else:
            col1, col2 = st.columns(2)
            
            with col1:
                sem_name = st.selectbox("Select Semester", sems["name"], key="assign_sem")
                sem_id = int(sems[sems["name"] == sem_name]["id"].values[0])

                subjects = pd.read_sql_query(
                    "SELECT * FROM subjects WHERE semester_id=?",
                    conn,
                    params=(sem_id,)
                )

                if subjects.empty:
                    st.warning("Please create a subject for this semester first.")
                    subject_selected = None
                else:
                    subject_options = {
                        row['name']: row['id']
                        for _, row in subjects.iterrows()
                    }

                    selected_subject = st.selectbox("Select Subject", list(subject_options.keys()))
                    sub_id = int(subject_options[selected_subject])
                    subject_selected = True
            
            with col2:
                title = st.text_input("Assignment Title", placeholder="e.g., Design of RCC Beam")
                deadline = st.date_input("Deadline")
                rubric_text = st.text_area("🎯 Marking Rubric / Model Answer", placeholder="Key steps, formulas, or point breakdowns...")
                
                file = st.file_uploader("📎 Upload Assignment Question PDF (Optional)", type=["pdf"])

            if st.button("➕ Create Assignment", use_container_width=True, type="primary"):

                if not subject_selected:
                    st.error("Please select a subject.")
                elif not title.strip():
                    st.error("Title cannot be empty.")
                else:
                    file_path = ""

                    if file:
                        # ✅ VALIDATE FILE
                        is_valid, validation_msg = validate_file_upload(file, ALLOWED_ASSIGNMENT_TYPES, MAX_FILE_SIZE_MB)
                        
                        if not is_valid:
                            st.error("❌ File Validation Failed: {}".format(validation_msg))
                        else:
                            timestamp = datetime.now(NST).strftime("%Y%m%d_%H%M%S")
                            file_path = "assignment_files/{}_{}.pdf".format(timestamp, file.name.replace(" ", "_"))
                            
                            # Safe file save operation
                            success, result = safe_file_operation(
                                lambda: open(file_path, "wb").write(file.getbuffer())
                            )
                            if success:
                                apply_watermark(file_path)
                            if not success:
                                st.error("❌ File Save Failed: {}".format(result))
                                file_path = ""
                            
                    try:
                        c.execute("""
                        INSERT INTO assignments(title,subject_id,deadline,question_file,rubric)
                        VALUES(?,?,?,?,?)
                        """, (title.strip(), int(sub_id), str(deadline), file_path, rubric_text.strip()))

                        conn.commit()
                        st.success("✅ Assignment '{}' created successfully!".format(title.strip()))
                        st.balloons()
                        st.rerun()

                    except Exception as e:
                        st.error("Database Error: {}".format(str(e)))
                        # Cleanup file if database insert failed
                        if file_path and os.path.exists(file_path):
                            try:
                                os.remove(file_path)
                            except:
                                pass

        st.divider()
        
        # ========== VIEW ASSIGNMENTS ==========
        st.subheader("📋 Existing Assignments")
        
        # Filter option
        view_sems = pd.read_sql_query("SELECT * FROM semesters ORDER BY name ASC", conn)
        
        if not view_sems.empty:
            view_filter = st.selectbox("Filter by Semester", ["All"] + view_sems["name"].tolist(), key="view_assign_filter")
            
            if view_filter == "All":
                all_assignments = pd.read_sql_query("""
                SELECT 
                    assignments.id as ID,
                    assignments.title as Title,
                    subjects.name as Subject,
                    semesters.name as Semester,
                    assignments.deadline as Deadline,
                    assignments.question_file as File
                FROM assignments
                JOIN subjects ON assignments.subject_id = subjects.id
                JOIN semesters ON subjects.semester_id = semesters.id
                ORDER BY assignments.deadline DESC
                """, conn)
            else:
                filter_sem_id = int(view_sems[view_sems["name"] == view_filter]["id"].values[0])
                all_assignments = pd.read_sql_query("""
                SELECT 
                    assignments.id as ID,
                    assignments.title as Title,
                    subjects.name as Subject,
                    semesters.name as Semester,
                    assignments.deadline as Deadline,
                    assignments.question_file as File
                FROM assignments
                JOIN subjects ON assignments.subject_id = subjects.id
                JOIN semesters ON subjects.semester_id = semesters.id
                WHERE semesters.id = ?
                ORDER BY assignments.deadline DESC
                """, conn, params=(filter_sem_id,))

            if all_assignments.empty:
                st.info("No assignments created yet.")
            else:
                # Show table without file path
                st.dataframe(
                    all_assignments[['ID', 'Semester', 'Subject', 'Title', 'Deadline']],
                    use_container_width=True,
                    hide_index=True
                )
                
                st.info("📊 Total Assignments: **{}**".format(len(all_assignments)))
                
                st.divider()
                
                # ========== ASSIGNMENT DETAILS WITH DELETE ==========
                st.subheader("📄 Assignment Details")
                
                for _, assignment in all_assignments.iterrows():
                    
                    # Get submission count
                    submission_count = pd.read_sql_query("""
                    SELECT COUNT(*) as count FROM submissions
                    WHERE assignment_id=?
                    """, conn, params=(assignment['ID'],)).iloc[0]['count']
                    
                    deadline_display = format_deadline_display(assignment['Deadline'])
                    
                    with st.expander("{} - {} - {} | {}".format(
                        assignment['Semester'],
                        assignment['Subject'],
                        assignment['Title'],
                        deadline_display
                    )):
                        
                        col_detail1, col_detail2 = st.columns([2, 1])
                        
                        with col_detail1:
                            st.write("**Semester:** {}".format(assignment['Semester']))
                            st.write("**Subject:** {}".format(assignment['Subject']))
                            st.write("**Title:** {}".format(assignment['Title']))
                            st.write("**Deadline:** {}".format(assignment['Deadline']))
                            st.metric("📊 Total Submissions", submission_count)
                        
                        with col_detail2:
                            # Download assignment file
                            if assignment['File'] and os.path.exists(assignment['File']):
                                with open(assignment['File'], "rb") as f:
                                    st.download_button(
                                        "📥 Download Question",
                                        f,
                                        file_name=os.path.basename(assignment['File']),
                                        key="download_assign_{}".format(assignment['ID']),
                                        use_container_width=True
                                    )
                            else:
                                st.info("No file uploaded")
                        
                        st.divider()
                        
                        # ========== EDIT ASSIGNMENT ==========
                        with st.expander("✏️ Edit Assignment Details"):
                            
                            col_edit1, col_edit2 = st.columns(2)
                            
                            with col_edit1:
                                new_title = st.text_input(
                                    "New Title",
                                    value=assignment['Title'],
                                    key="edit_title_{}".format(assignment['ID'])
                                )
                            
                            with col_edit2:
                                current_deadline = datetime.strptime(assignment['Deadline'], '%Y-%m-%d').date()
                                new_deadline = st.date_input(
                                    "New Deadline",
                                    value=current_deadline,
                                    key="edit_deadline_{}".format(assignment['ID'])
                                )
                            
                            if st.button("💾 Save Changes", key="save_edit_{}".format(assignment['ID']), type="primary"):
                                
                                if not new_title.strip():
                                    st.error("Title cannot be empty")
                                elif new_title == assignment['Title'] and str(new_deadline) == assignment['Deadline']:
                                    st.info("No changes made")
                                else:
                                    success, message = update_assignment(assignment['ID'], new_title, new_deadline)
                                    
                                    if success:
                                        st.success("✅ {}".format(message))
                                        st.rerun()
                                    else:
                                        st.error("❌ {}".format(message))
                        
                        # Delete button
                        col_del1, col_del2 = st.columns([2, 1])
                        
                        with col_del1:
                            st.warning("⚠️ **Delete Assignment:** This will remove all student submissions for this assignment.")
                        
                        with col_del2:
                            if st.button("🗑️ Delete Assignment", key="delete_assign_{}".format(assignment['ID']), type="primary", use_container_width=True):
                                
                                try:
                                    # Delete all submissions first
                                    submissions = pd.read_sql_query("""
                                    SELECT submission_file FROM submissions
                                    WHERE assignment_id=?
                                    """, conn, params=(assignment['ID'],))
                                    
                                    # Delete submission files
                                    for _, sub in submissions.iterrows():
                                        if sub['submission_file'] and os.path.exists(sub['submission_file']):
                                            os.remove(sub['submission_file'])
                                    
                                    # Delete submissions from database
                                    c.execute("DELETE FROM submissions WHERE assignment_id=?", (assignment['ID'],))
                                    
                                    # Delete assignment file
                                    if assignment['File'] and os.path.exists(assignment['File']):
                                        os.remove(assignment['File'])
                                    
                                    # Delete assignment from database
                                    c.execute("DELETE FROM assignments WHERE id=?", (assignment['ID'],))
                                    
                                    conn.commit()
                                    

                                    st.success("✅ Assignment '{}' deleted successfully!".format(assignment['Title']))
                                    st.rerun()
                                    
                                except Exception as e:
                                    st.error("Error deleting assignment: {}".format(str(e)))
            
        # ========== MANAGE STUDENT SUBMISSIONS ==========
        st.divider()
        st.subheader("🗑️ Delete a Student's Submission")
        st.info("Use this if a student uploaded the wrong file. This deletes their file and allows them to submit again.")

        # 1. Let admin pick the assignment
        all_assignments_for_del = pd.read_sql_query("SELECT id, title FROM assignments", conn)
        
        if not all_assignments_for_del.empty:
            assn_options = {row['title']: row['id'] for _, row in all_assignments_for_del.iterrows()}
            
            col_sel1, col_sel2 = st.columns(2)
            with col_sel1:
                assn_to_manage = st.selectbox("1. Select Assignment", list(assn_options.keys()), key="del_sub_assn")
            
            # 2. Find all submissions for that specific assignment
            subs_query = """
            SELECT s.id, s.submission_file, u.username, u.full_name 
            FROM submissions s
            JOIN users u ON s.student_id = u.id
            WHERE s.assignment_id = ?
            """
            submissions_df = pd.read_sql_query(subs_query, conn, params=(int(assn_options[assn_to_manage]),))
            
            with col_sel2:
                if not submissions_df.empty:
                    sub_options = {"{} ({})".format(row['full_name'], row['username']): (row['id'], row['submission_file']) for _, row in submissions_df.iterrows()}
                    student_to_delete = st.selectbox("2. Select Student's Submission", list(sub_options.keys()), key="del_sub_student")
                else:
                    st.info("No submissions yet.")
                    sub_options = {}
                
            # 3. The Delete Button
            if sub_options:
                if st.button("🚨 Delete Student's Submission", type="primary", use_container_width=True):
                    sub_id_to_del, file_to_del = sub_options[student_to_delete]
                    
                    try:
                        # A. Delete from database
                        c.execute("DELETE FROM submissions WHERE id=?", (int(sub_id_to_del),))
                        conn.commit()
                        
                        # B. Delete the physical PDF file from the folder
                        if file_to_del and os.path.exists(file_to_del):
                            os.remove(file_to_del)
                            
                        st.success("✅ Submission deleted! {} can now upload a new file.".format(student_to_delete.split(' ')[0]))
                        st.balloons()
                        st.rerun()
                    except Exception as e:
                        st.error("❌ Error deleting submission: {}".format(str(e)))
        else:
            st.info("No assignments created yet.")                         
    
    # SUBMISSIONS & AI
    with tabs[4]:

        st.subheader("Student Submissions & AI Grading")

        # filter by semester
        sems = pd.read_sql_query("SELECT * FROM semesters ORDER BY name ASC", conn)

        if not sems.empty:
            selected_sem = st.selectbox("Filter by Semester", ["All"] + sems["name"].tolist(), key="filter_sem")

            if selected_sem == "All":
                df = pd.read_sql_query("""
                SELECT
                    submissions.id,
                    users.username,
                    users.full_name,
                    semesters.name as semester,
                    subjects.name as subject,
                    assignments.title as assignment,
                    assignments.rubric,
                    submissions.submission_time,
                    submissions.submission_file,
                    submissions.marks,
                    submissions.ai_summary
                FROM submissions
                JOIN users ON submissions.student_id = users.id 
                JOIN assignments ON submissions.assignment_id = assignments.id
                JOIN subjects ON assignments.subject_id = subjects.id
                JOIN semesters ON subjects.semester_id = semesters.id
                ORDER BY submissions.submission_time DESC
                """, conn)
            else:
                sem_id = int(sems[sems["name"] == selected_sem]["id"].values[0])
                df = pd.read_sql_query("""
                SELECT
                    submissions.id, 
                    users.username,
                    users.full_name,
                    semesters.name as semester,
                    subjects.name as subject,
                    assignments.title as assignment,
                    submissions.submission_time,
                    submissions.submission_file,
                    submissions.marks,
                    submissions.ai_summary
                FROM submissions
                JOIN users ON submissions.student_id = users.id
                JOIN assignments ON submissions.assignment_id = assignments.id
                JOIN subjects ON assignments.subject_id = subjects.id
                JOIN semesters ON subjects.semester_id = semesters.id
                WHERE semesters.id = ?
                ORDER BY submissions.submission_time DESC
                """, conn, params=(sem_id,))
        else:
            df = pd.DataFrame()

        if df.empty:
            st.info("No submissions yet.")
        else:
            # Display summary
            st.dataframe(
                df[["semester", "subject", "assignment", "username", "full_name", "submission_time", "marks"]],
                use_container_width=True,
                hide_index=True
            )
            st.divider()
            st.subheader("AI Grading Tool")

            
            
            for _, row in df.iterrows():
                expander_title = "{} - {} ({})".format(row['username'], row['assignment'], row['subject'])
                
                with st.expander(expander_title):
                    col1, col2 = st.columns([2, 1])

                    with col1:
                        st.write("**Student:** {} ({})".format(row['full_name'], row['username']))
                        st.write("**Semester:** {}".format(row['semester']))
                        st.write("**Subject:** {}".format(row['subject']))
                        st.write("**Assignment:** {}".format(row['assignment']))
                        st.write("**Submitted:** {}".format(row['submission_time']))

                        if row['marks'] and str(row['marks']).strip():
                            st.metric("Current Marks", "{}/10".format(row['marks']))
                        else:
                            st.info("Not graded yet")

                    with col2:
                        if row["submission_file"] and os.path.exists(row["submission_file"]):
                            with open(row["submission_file"], "rb") as f:
                                st.download_button(
                                    "Download Submission", 
                                    f,
                                    file_name=os.path.basename(row["submission_file"]),
                                    key="dl_{}".format(row['id'])
                                )
                    
                    st.divider()

                    # AI Grading 
                    if row["submission_file"] and os.path.exists(row["submission_file"]):
                        col_a, col_b = st.columns(2)
                            
                        with col_a:
                            if st.button("AI Grade", key="grade_{}".format(row['id'])):
                                if not row['rubric'] or not str(row['rubric']).strip():
                                    st.warning("Please enter a rubric/model answer first")
                                else:
                                    with st.spinner("AI is grading..."):
                                        try:
                                            result = vision_grade(row["submission_file"], row["rubric"])
                                            with st.expander("**AI Response:**", expanded= True):
                                                st.write(result)

                                            #check if result contains error
                                            if result and "Error" not in str(result):
                                                marks = extract_marks(result)
                                                
                                                if marks is not None:
                                                    c.execute(
                                                        "UPDATE submissions SET marks=?, ai_summary=? WHERE id=?",
                                                        (marks, result, row["id"])
                                                    )
                                                    conn.commit()
                                                    st.success("Updated marks: {}/10".format(marks))
                                                    st.rerun()
                                                else:
                                                    st.warning("Could not extract marks from AI response.Please enter manually below")
                                                    st.info("Tip: Make sure AI response contains 'FINAL_MARKS: X/10'")
                                                    #still save the AI summary even if marks extraction failed
                                                    c. execute(
                                                        "UPDATE submissions SER ai_summary=? WHERE id=?",
                                                        (str(result), int(row["id"]))
                                                    )
                                                    conn.commit()
                                            else:
                                                st.error("AI returned an error. Check the response above.")
                                        except Exception as e:
                                            st.error("Error during AI grading: {}".format(str(e)))
                                            import traceback 
                                            st.code(traceback.format_exc())
                        
                        with col_b:
                            # Manual grade override
                            default_marks = 0
                            if row['marks'] and str(row['marks']).strip():
                                try:
                                    default_marks = int(row['marks'])
                                except:
                                    default_marks = 0
                            
                            manual_marks = st.number_input(
                                "Or enter marks manually",
                                min_value=0,
                                max_value=10,
                                value=default_marks,
                                key="manual_{}".format(row['id'])
                            )
                            if st.button("Save Manual Marks", key="save_{}".format(row['id'])):
                                c.execute(
                                    "UPDATE submissions SET marks=? WHERE id=?",
                                    (manual_marks, row["id"])
                                )
                                conn.commit()
                                st.success("Marks updated to {}/10".format(manual_marks))
                                st.rerun()
                    
                    # Show previous AI summary if exists
                    if row['ai_summary'] and str(row['ai_summary']).strip():
                        with st.expander("Previous AI Feedback"):
                            st.write(row['ai_summary'])
    st.write("DEBUG: Tab 5 is loading!")
    # ANALYTICS & GRADING HUB
    with tabs[5]:
        st.title("📊 Performance & Grading Hub")
        
        # 1. THE SWITCHBOARD: Toggle between your original charts and the new ledger
        view_mode = st.radio(
            "Select View Mode", 
            ["📈 Analytics Dashboard", "📅 Daily Roll Call", "📝 Internal Theory Ledger (40 Marks)", "🧪 Practical Ledger (25 Marks)"], 
            horizontal=True
        )
        st.divider()

        # ================= VIEW 1: RESTORED ORIGINAL ANALYTICS =================
        if view_mode == "📈 Analytics Dashboard":
            st.subheader("📈 Class Performance Trend")
            # Fetch average marks per assignment ordered chronologically by deadline
            trend_data = pd.read_sql_query("""
            SELECT
                assignments.title as Assignment,
                AVG(CAST(submissions.marks AS FLOAT)) as Average_Marks
            FROM submissions
            JOIN assignments ON submissions.assignment_id = assignments.id
            WHERE submissions.marks IS NOT NULL AND submissions.marks != ''
            GROUP BY assignments.id
            ORDER BY assignments.deadline ASC
            """, conn)

            if not trend_data.empty:
                trend_data.set_index('Assignment', inplace=True)
                st.area_chart(trend_data['Average_Marks'])
            else:
                st.info("Not enough graded submissions to generate a trend chart yet.")
            
            st.divider() 

            st.subheader("📊 Grade Statistics")
            
            sems = pd.read_sql_query("SELECT * FROM semesters ORDER BY name ASC", conn)
            
            if not sems.empty:
                selected_sem = st.selectbox("Select Semester for Stats", ["All"] + sems["name"].tolist(), key="analytics_sem")
                
                if selected_sem == "All":
                    df = pd.read_sql_query("""
                    SELECT 
                        semesters.name as Semester, subjects.name as Subject, assignments.title as Assignment,
                        users.full_name as Student_Name, users.username as Username,
                        submissions.submission_time as Submission_Date, assignments.deadline as Deadline,
                        submissions.marks as Marks, submissions.ai_summary as AI_Feedback
                    FROM submissions
                    JOIN assignments ON submissions.assignment_id=assignments.id
                    JOIN subjects ON assignments.subject_id = subjects.id
                    JOIN semesters ON subjects.semester_id = semesters.id
                    JOIN users ON submissions.student_id = users.id
                    WHERE submissions.marks IS NOT NULL AND submissions.marks != ''
                    ORDER BY semesters.name, subjects.name, assignments.title, users.full_name
                    """, conn)
                else:
                    sem_id = int(sems[sems["name"] == selected_sem]["id"].values[0])
                    df = pd.read_sql_query("""
                    SELECT 
                        semesters.name as Semester, subjects.name as Subject, assignments.title as Assignment,
                        users.full_name as Student_Name, users.username as Username,
                        submissions.submission_time as Submission_Date, assignments.deadline as Deadline,
                        submissions.marks as Marks, submissions.ai_summary as AI_Feedback
                    FROM submissions
                    JOIN assignments ON submissions.assignment_id=assignments.id
                    JOIN subjects ON assignments.subject_id = subjects.id
                    JOIN semesters ON subjects.semester_id = semesters.id
                    JOIN users ON submissions.student_id = users.id
                    WHERE semesters.id = ? AND submissions.marks IS NOT NULL AND submissions.marks != ''
                    ORDER BY subjects.name, assignments.title, users.full_name
                    """, conn, params=(sem_id,))

                if not df.empty:
                    df["marks"] = pd.to_numeric(df["Marks"], errors="coerce")
                    
                    st.subheader("📥 Download Grade Reports")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        csv_detailed = df.to_csv(index=False).encode('utf-8')
                        st.download_button("📄 Detailed Report", csv_detailed, f"Grades_Detailed_{selected_sem}.csv", 'text/csv', use_container_width=True)
                    
                    with col2:
                        df_summary = df[['Semester', 'Subject', 'Assignment', 'Student_Name', 'Username', 'Marks']]
                        csv_summary = df_summary.to_csv(index=False).encode('utf-8')
                        st.download_button("📊 Summary Report", csv_summary, f"Grades_Summary_{selected_sem}.csv", 'text/csv', use_container_width=True)
                    
                    with col3:
                        df_pivot = df.pivot_table(index=['Semester', 'Student_Name', 'Username', 'Subject'], columns='Assignment', values='marks', aggfunc='first').reset_index()
                        assignment_cols = [col for col in df_pivot.columns if col not in ['Semester', 'Student_Name', 'Username', 'Subject']]
                        df_pivot['Average'] = df_pivot[assignment_cols].mean(axis=1).round(2)
                        csv_pivot = df_pivot.to_csv(index=False).encode('utf-8')
                        st.download_button("📈 Student-wise Summary", csv_pivot, f"Grades_Student_{selected_sem}.csv", 'text/csv', use_container_width=True)
                    
                    st.divider()
                    st.subheader("📊 Average Marks by Assignment")
                    st.bar_chart(df.groupby("Assignment")["marks"].mean())
                    
                    st.divider()
                    st.subheader("📋 Detailed Grade Table")
                    st.dataframe(df[['Semester', 'Subject', 'Assignment', 'Student_Name', 'Username', 'Marks']], use_container_width=True, hide_index=True)
                else:
                    st.info("No graded submissions yet.")
        # ================= REFINED: DAILY ATTENDANCE PUNCHER WITH EXPORT =================
        elif view_mode == "📅 Daily Roll Call":
            st.subheader("📅 Daily Attendance Puncher")
            
            sems_att = pd.read_sql_query("SELECT * FROM semesters ORDER BY name ASC", conn)
            if sems_att.empty:
                st.warning("Please create a semester first.")
            else:
                c1, c2, c3 = st.columns(3)
                with c1:
                    sel_sem_name = st.selectbox("Select Semester", sems_att["name"], key="att_sem_sel")
                    sel_sem_id = int(sems_att[sems_att["name"] == sel_sem_name]["id"].values[0])
                with c2:
                    subjects_att = pd.read_sql_query("SELECT * FROM subjects WHERE semester_id=?", conn, params=(sel_sem_id,))
                    if subjects_att.empty:
                        st.error("No subjects found.")
                        sub_id = None
                    else:
                        sel_sub_name = st.selectbox("Select Subject", subjects_att["name"], key="att_sub_sel")
                        sub_id = int(subjects_att[subjects_att["name"] == sel_sub_name]["id"].values[0])
                with c3:
                    att_type = st.radio("Session Type", ["📝 Theory Class", "🧪 Practical Lab"], horizontal=True)

                if sub_id:
                    # Fetch student roster for this class
                    students_df = pd.read_sql_query("""
                        SELECT id as student_id, full_name as Name, username as Roll 
                        FROM users 
                        WHERE role='student' AND semester_id=? 
                        ORDER BY username ASC
                    """, conn, params=(sel_sem_id,))

                    if students_df.empty:
                        st.info("No students registered in this semester yet.")
                    else:
                        st.write(f"Marking attendance for: **{datetime.now(NST).strftime('%B %d, %Y')}**")
                        
                        # Create a display data editor where only the "Present" checkbox column is editable
                        students_df["Present"] = True  # Default to present for quick logging
                        
                        edited_att_df = st.data_editor(
                            students_df,
                            column_config={
                                "student_id": None,
                                "Roll": st.column_config.TextColumn("Roll No.", disabled=True),
                                "Name": st.column_config.TextColumn("Student Name", disabled=True),
                                "Present": st.column_config.CheckboxColumn("Attendance Status", default=True)
                            },
                            use_container_width=True,
                            hide_index=True,
                            key="daily_attendance_grid"
                        )

                        # ================= EXCEL/CSV HISTORY EXPORTER =================
                        st.divider()
                        st.markdown("### 📥 Export Attendance History")
                        
                        export_query = """
                            SELECT u.username as [Roll No.], u.full_name as [Student Name],
                                   IFNULL(m.t_att_present, 0) as [Theory Present], IFNULL(m.t_att_total, 0) as [Theory Total],
                                   IFNULL(m.p_att_present, 0) as [Practical Present], IFNULL(m.p_att_total, 0) as [Practical Total]
                            FROM users u
                            LEFT JOIN student_marks m ON u.id = m.student_id AND m.subject_id = ?
                            WHERE u.role = 'student' AND u.semester_id = ?
                            ORDER BY u.username ASC
                        """
                        export_df = pd.read_sql_query(export_query, conn, params=(sub_id, sel_sem_id))
                        
                        if not export_df.empty:
                            file_timestamp = datetime.now(NST).strftime("%Y%m%d")
                            clean_filename = f"Attendance_{sel_sub_name.replace(' ', '_')}_{file_timestamp}.csv"
                            csv_buffer = export_df.to_csv(index=False).encode('utf-8')
                            
                            st.download_button(
                                label="📥 Download Current Attendance Sheet (Excel/CSV Compatible)",
                                data=csv_buffer,
                                file_name=clean_filename,
                                mime="text/csv",
                                use_container_width=True
                            )
                        # ===================================================================

                        st.write("") # Spacer

                        if st.button("🚀 Submit Today's Attendance Record", use_container_width=True, type="primary"):
                            for _, r in edited_att_df.iterrows():
                                s_id = int(r['student_id'])
                                
                                # 🛡️ Safe-eval the checkbox: Handles cases where SQLite returns raw bytes or booleans
                                val_present = r['Present']
                                if isinstance(val_present, bytes):
                                    is_present = 1 if b'\x01' in val_present else 0
                                else:
                                    is_present = 1 if bool(val_present) else 0
                                
                                # 1. Fetch current historical numbers from student_marks table
                                current_record = pd.read_sql_query(
                                    "SELECT t_att_present, t_att_total, p_att_present, p_att_total FROM student_marks WHERE student_id=? AND subject_id=?",
                                    conn, params=(s_id, sub_id)
                                )
                                
                                # 🛠️ Inner helper function to intercept and sanitize byte-string formats safely
                                def get_safe_int(df, column):
                                    if df.empty or pd.isna(df.iloc[0][column]):
                                        return 0
                                    val = df.iloc[0][column]
                                    if isinstance(val, bytes):
                                        return 1 if b'\x01' in val else 0
                                    return int(float(val))

                                # 2. Increment based on class type selection
                                if att_type == "📝 Theory Class":
                                    prev_present = get_safe_int(current_record, 't_att_present')
                                    prev_total = get_safe_int(current_record, 't_att_total')
                                    
                                    new_present = prev_present + is_present
                                    new_total = prev_total + 1
                                    
                                    c.execute("""
                                        INSERT INTO student_marks (student_id, subject_id, t_att_present, t_att_total) 
                                        VALUES (?, ?, ?, ?)
                                        ON CONFLICT(student_id, subject_id) DO UPDATE SET 
                                            t_att_present = ?, t_att_total = ?
                                    """, (s_id, sub_id, new_present, new_total, new_present, new_total))
                                    
                                else:  # Practical Class
                                    prev_present = get_safe_int(current_record, 'p_att_present')
                                    prev_total = get_safe_int(current_record, 'p_att_total')
                                    
                                    new_present = prev_present + is_present
                                    new_total = prev_total + 1
                                    
                                    c.execute("""
                                        INSERT INTO student_marks (student_id, subject_id, p_att_present, p_att_total) 
                                        VALUES (?, ?, ?, ?)
                                        ON CONFLICT(student_id, subject_id) DO UPDATE SET 
                                            p_att_present = ?, p_att_total = ?
                                    """, (s_id, sub_id, new_present, new_total, new_present, new_total))
                                    
                            conn.commit()
                            st.success(f"✅ Attendance successfully compiled and added to cumulative ledgers!")
                            st.balloons()
                            st.rerun()

        # ================= VIEW 2: INTERNAL THEORY LEDGER =================
        elif view_mode == "📝 Internal Theory Ledger (40 Marks)":
            sems_grading = pd.read_sql_query("SELECT * FROM semesters ORDER BY name ASC", conn)
            if sems_grading.empty:
                st.warning("Please create a semester first.")
            else:
                col_sel1, col_sel2 = st.columns(2)
                with col_sel1:
                    sel_sem_name = st.selectbox("Semester", sems_grading["name"], key="grad_sem_sel_t")
                    sel_sem_id = int(sems_grading[sems_grading["name"] == sel_sem_name]["id"].values[0])
                with col_sel2:
                    subjects_grading = pd.read_sql_query("SELECT * FROM subjects WHERE semester_id=?", conn, params=(sel_sem_id,))
                    if subjects_grading.empty:
                        st.error("No subjects found.")
                    else:
                        sel_sub_name = st.selectbox("Subject", subjects_grading["name"], key="grad_sub_sel_t")
                        sel_sub_id = int(subjects_grading[subjects_grading["name"] == sel_sub_name]["id"].values[0])

                        # Hydraulics Scheme
                        hyd_scheme = {'theory_full_marks': 40, 't_weight_att': 0.10, 't_weight_hw': 0.25, 't_weight_other': 0.15, 't_weight_mid': 0.25, 't_weight_final': 0.25}

                        query = """
                            SELECT u.id as student_id, u.full_name as Name, u.username as Roll,
                            IFNULL(m.t_att_present, 0) as t_att_present,
                            IFNULL(m.t_att_total, 34) as t_att_total,
                            IFNULL(m.t_hw_raw, 0) as t_hw_raw,
                            IFNULL(m.t_mid_raw, 0) as t_mid_raw,
                            IFNULL(m.t_final_raw, 0) as t_final_raw,
                            IFNULL(m.t_other_raw, 0) as t_other_raw,
                            IFNULL(m.t_grace, 0) as t_grace
                            
                            FROM users u LEFT JOIN student_marks m ON u.id = m.student_id AND m.subject_id = ?
                            WHERE u.role = 'student' AND u.semester_id = ?
                        """
                        df_t = pd.read_sql_query(query, conn, params=(sel_sub_id, sel_sem_id))
                        edited_t = st.data_editor(df_t, column_config={"student_id": None, "Grace": st.column_config.NumberColumn(max_value=5)}, use_container_width=True, hide_index=True, key="theory_editor")

                        if st.button("💾 Synchronize Theory Marks", use_container_width=True, type="primary"):
                            for _, r in edited_t.iterrows():
                                c.execute("""
                                          INSERT INTO student_marks (
                                          student_id, subject_id, t_att_present, t_att_total,
                                          t_hw_raw, t_mid_raw, t_final_raw, t_other_raw, t_grace
                                          ) VALUES (?,?,?,?,?,?,?,?,?)
                                          ON CONFLICT(student_id, subject_id) DO UPDATE SET
                                            t_att_present=excluded.t_att_present,
                                            t_att_total=excluded.t_att_total,
                                            t_hw_raw=excluded.t_hw_raw,
                                            t_mid_raw=excluded.t_mid_raw,
                                            t_final_raw=excluded.t_final_raw,
                                            t_other_raw=excluded.t_other_raw,
                                            t_grace=excluded.t_grace
                                """, (
                                    int(r['student_id']),
                                    int(sel_sub_id),
                                    int(r['t_att_present']),
                                    int(r['t_att_total']),
                                    float(r['t_hw_raw']),
                                    float(r['t_mid_raw']),
                                    float(r['t_final_raw']),
                                    float(r['t_other_raw']),
                                    float(r['t_grace'])
                                ))
                            conn.commit()
                            st.success("✅ Theory marks successfully synchronized and locked.")
                            st.rerun()


                        st.divider(); st.subheader("🎯 Theory Totals")
                        res_t = [{"Name": r['Name'], "Total (/40)": calculate_internal_theory(r.to_dict(), sub_id, conn)[0], "Eligibility": "✅ Eligible" if calculate_internal_theory(r.to_dict(), sub_id, conn)[1] else "❌ Ineligible"} for _, r in edited_t.iterrows()]
                        st.table(res_t)

        # ================= VIEW 3: PRACTICAL LEDGER =================
        elif view_mode == "🧪 Practical Ledger (25 Marks)":
            sems_grading = pd.read_sql_query("SELECT * FROM semesters ORDER BY name ASC", conn)
            if sems_grading.empty:
                st.warning("Please create a semester first.")
            else:
                col_sel1, col_sel2 = st.columns(2)
                with col_sel1:
                    sel_sem_name = st.selectbox("Semester", sems_grading["name"], key="grad_sem_sel_p")
                    sel_sem_id = int(sems_grading[sems_grading["name"] == sel_sem_name]["id"].values[0])
                with col_sel2:
                    subjects_grading = pd.read_sql_query("SELECT * FROM subjects WHERE semester_id=?", conn, params=(sel_sem_id,))
                    if subjects_grading.empty:
                        st.error("No subjects found.")
                    else:
                        sel_sub_name = st.selectbox("Subject", subjects_grading["name"], key="grad_sub_sel_p")
                        sel_sub_id = int(subjects_grading[subjects_grading["name"] == sel_sub_name]["id"].values[0])

                        # Practical Scheme
                        hyd_scheme = {'prac_full_marks': 25, 'p_weight_att': 0.20, 'p_weight_perf': 0.20, 'p_weight_report': 0.20, 'p_weight_test': 0.20, 'p_weight_viva': 0.20}

                        query_p = """
                            SELECT u.id as student_id, u.full_name as Name, u.username as Roll,
                            IFNULL(m.p_att_present, 0) as p_att_present,
                            IFNULL(m.p_att_total, 12) as p_att_total,
                            IFNULL(m.p_perf_raw, 0) as p_perf_raw, 
                            IFNULL(m.p_report_raw, 0) as p_report_raw,
                            IFNULL(m.p_test_raw, 0) as p_test_raw, 
                            IFNULL(m.p_viva_raw, 0) as p_viva_raw
                            FROM users u 
                            LEFT JOIN student_marks m ON u.id = m.student_id AND m.subject_id = ?
                            WHERE u.role = 'student' AND u.semester_id = ?
                        """
                        df_p = pd.read_sql_query(query_p, conn, params=(sel_sub_id, sel_sem_id))
                        edited_p = st.data_editor(df_p, column_config={"student_id": None}, use_container_width=True, hide_index=True, key="p_editor")

                        if st.button("💾 Synchronize Practical Marks", use_container_width=True, type="primary"):
                            for _, r in edited_p.iterrows():
                                c.execute("INSERT INTO student_marks (student_id, subject_id, p_att_present, p_att_total, p_perf_raw, p_report_raw, p_test_raw, p_viva_raw) VALUES (?,?,?,?,?,?,?,?) ON CONFLICT(student_id, subject_id) DO UPDATE SET p_att_present=excluded.p_att_present, p_att_total=excluded.p_att_total, p_perf_raw=excluded.p_perf_raw, p_report_raw=excluded.p_report_raw, p_test_raw=excluded.p_test_raw, p_viva_raw=excluded.p_viva_raw", (int(r['student_id']), int(sel_sub_id), int(r['p_att_present']), int(r['p_att_total']), float(r['p_perf_raw']), float(r['p_report_raw']), float(r['p_test_raw']), float(r['p_viva_raw'])))
                            conn.commit(); st.success("Practical Saved."); st.rerun()

                        st.divider(); st.subheader("🧪 Practical Totals")
                        res_p = [{"Name": r['Name'], "Total (/25)": calculate_internal_practical(r.to_dict(), sub_id, conn)[0], "Eligibility": "✅ Eligible" if calculate_internal_practical(r.to_dict(), sub_id, conn)[1] else "❌ Ineligible"} for _, r in edited_p.iterrows()]
                        st.table(res_p)
       
            # ================= MANAGE STUDENTS (TABS[6]) =================
    with tabs[6]:
        st.subheader("⚠️ Emergency Fix for Existing Students")
        if st.button("🔧 Fix ALL Students with NULL semester"):
            default_sem = pd.read_sql_query("SELECT id FROM semesters ORDER BY id ASC LIMIT 1", conn)
            if not default_sem.empty:
                default_sem_id = int(default_sem.iloc[0]['id'])
                c.execute("UPDATE users SET semester_id = ? WHERE role = 'student' AND semester_id IS NULL", (default_sem_id,))
                conn.commit()
                st.success("✅ Fixed {} students - assigned to semester_id {}".format(c.rowcount, default_sem_id))
                st.rerun()
            else:
                st.error("No semesters available to assign")
    
        st.divider()
    
        st.subheader("Add Student Manually")
        col1, col2 = st.columns(2)

        with col1:
            student_name = st.text_input("Full Name", key="student_name")
            username = st.text_input("Username", key="student_username")
            email_input = st.text_input("Email Address", key="student_email")
            password = st.text_input("Password", type="password", key="student_password")

        with col2:
            sems = pd.read_sql_query("SELECT * FROM semesters ORDER BY name ASC", conn)
            if sems.empty:
                st.warning("Please create semesters first.")
            else:
                semester_name = st.selectbox("Assign Semester", sems["name"], key="student_semester")
                semester_id = int(sems[sems["name"] == semester_name]["id"].values[0])
                st.info("Will assign semester_id: {}".format(semester_id))

                if st.button("Create Student"):
                    if not username or not password or not student_name:
                        st.error("All fields except email are required.")
                    else:
                        try:
                            c.execute("""
                                INSERT INTO users(full_name, username, password, role, semester_id, email)
                                VALUES(?, ?, ?, ?, ?, ?)
                            """, (
                                student_name.strip(),
                                username.strip(),
                                hash_password(password.strip()),
                                "student",
                                semester_id,
                                email_input.strip() if email_input else None
                            ))
                            conn.commit()
                            st.success("✅ Student '{}' created successfully!".format(username))
                            st.rerun()
                        except sqlite3.IntegrityError:
                            st.error("Username already exists.")
                        except Exception as e:
                            st.error("Error: {}".format(str(e)))

        st.divider()

        st.subheader("Bulk Upload Students via CSV")
        st.info("CSV format: name,username,password,semester,email")
        csv_file = st.file_uploader("Upload CSV", type=["csv"], key="student_csv")

        if csv_file:
            df_csv = pd.read_csv(csv_file)
            df_csv.columns = df_csv.columns.str.strip().str.lower()
            required_cols = {"name", "username", "password", "semester", "email"}

            if not required_cols.issubset(df_csv.columns):
                st.error("CSV missing columns. Ensure it has: name, username, password, semester, email")
            else:
                st.write("🔍 Data Preview:", df_csv.head())
                if st.button("🚀 Process & Register Students"):
                    sems_list = pd.read_sql_query("SELECT * FROM semesters", conn)
                    success_count, error_count = 0, 0

                    for _, row in df_csv.iterrows():
                        try:
                            clean_name = str(row["name"]).strip()
                            clean_user = str(row["username"]).strip()
                            clean_sem = str(row["semester"]).strip()
                            clean_email = str(row["email"]).strip() if not pd.isna(row["email"]) else None
                            raw_pw = str(row["password"]).replace('.0', '').strip()
                        
                            sem_match = sems_list[sems_list["name"] == clean_sem]
                            if not sem_match.empty:
                                sem_id = int(sem_match["id"].values[0])
                                c.execute("""
                                    INSERT INTO users(full_name, username, password, role, semester_id, email)
                                    VALUES(?,?,?,?,?,?)
                                """, (clean_name, clean_user, hash_password(raw_pw), "student", sem_id, clean_email))
                                success_count += 1
                            else:
                                error_count += 1
                        except:
                            error_count += 1
                
                    conn.commit()
                    st.success("✅ {} students uploaded! ❌ {} failed.".format(success_count, error_count))
                    st.rerun()

        st.divider()

        st.subheader("📋 Registered Student List")
        all_sems_list = pd.read_sql_query("SELECT * FROM semesters ORDER BY name ASC", conn)
        list_filter = st.selectbox("View Students by Semester", ["All"] + all_sems_list["name"].tolist(), key="view_filter")

        if list_filter == "All":
            query = """
                SELECT users.id as ID, users.full_name as Name, users.username as Username, 
                       users.email as Email, COALESCE(semesters.name, 'No Semester') as Semester
                FROM users 
                LEFT JOIN semesters ON users.semester_id = semesters.id 
                WHERE users.role='student' 
                ORDER BY semesters.name ASC, users.full_name ASC
            """
            students_df = pd.read_sql_query(query, conn)
        else:
            query = """
                SELECT users.id as ID, users.full_name as Name, users.username as Username, 
                       users.email as Email, semesters.name as Semester
                FROM users 
                JOIN semesters ON users.semester_id = semesters.id 
                WHERE users.role='student' AND semesters.name = ?
                ORDER BY users.full_name ASC
            """
            students_df = pd.read_sql_query(query, conn, params=(list_filter,))

        if not students_df.empty:
            st.dataframe(students_df[['Name', 'Username', 'Email', 'Semester']], use_container_width=True, hide_index=True)
            st.info(f"📊 Total Students: **{len(students_df)}**")
        
            csv_data = students_df[['Name', 'Username', 'Email', 'Semester']].to_csv(index=False).encode('utf-8')
            st.download_button(f"📥 Download {list_filter} List (CSV)", csv_data, f"Students_{list_filter}.csv", "text/csv", use_container_width=True)
        else:
            st.info("No students found.")

        st.divider()

        st.subheader("🗑️ Delete Student")
        if not students_df.empty:
            student_options = {f"{row['Semester']} | {row['Username']} | {row['Name']}": row['ID'] for _, row in students_df.iterrows()}
            selected_to_delete = st.selectbox("Select Student to Remove", list(student_options.keys()))
        
            col_d1, col_d2 = st.columns([1, 3])
            with col_d1:
                if st.button("🗑️ Confirm Delete", type="primary", use_container_width=True):
                    s_id = student_options[selected_to_delete]
                    c.execute("DELETE FROM submissions WHERE student_id=?", (int(s_id),))
                    c.execute("DELETE FROM users WHERE id=?", (int(s_id),))
                    conn.commit()
                    st.success("Student removed.")
                    st.rerun()
            with col_d2:
                st.warning("⚠️ Deleting will remove all submissions for this student.")

        st.divider()

        st.subheader("🔧 Update Semester Assignment")
        all_students = pd.read_sql_query("SELECT id, username, full_name FROM users WHERE role='student' ORDER BY username ASC", conn)
        if not all_students.empty:
            student_map = {f"{row['username']} ({row['full_name']})": row['id'] for _, row in all_students.iterrows()}
            c_up1, c_up2 = st.columns(2)
            with c_up1:
                target_student = st.selectbox("Select Student", list(student_map.keys()), key="up_stud")
            with c_up2:
                new_sem_list = pd.read_sql_query("SELECT id, name FROM semesters ORDER BY name ASC", conn)
                target_sem = st.selectbox("New Semester", new_sem_list["name"], key="up_sem")
        
            if st.button("💾 Update Assignment", use_container_width=True):
                new_id = int(new_sem_list[new_sem_list["name"] == target_sem]["id"].values[0])
                c.execute("UPDATE users SET semester_id=? WHERE id=?", (new_id, student_map[target_student]))
                conn.commit()
                st.success("Assignment updated!")
                st.rerun()

        st.divider()

        st.subheader("🔑 Emergency Password Reset")
        if not all_students.empty:
            reset_map = {f"{row['username']} ({row['full_name']})": row['id'] for _, row in all_students.iterrows()}
            c_res1, c_res2 = st.columns(2)
            with c_res1:
                reset_student = st.selectbox("Select Student", list(reset_map.keys()), key="res_stud")
            with c_res2:
                new_pw = st.text_input("New Temporary Password", type="password")
            
            if st.button("🚨 Force Reset Password", type="primary", use_container_width=True):
                if len(new_pw) < 6:
                    st.error("Password too short.")
                else:
                    c.execute("UPDATE users SET password=? WHERE id=?", (hash_password(new_pw), reset_map[reset_student]))
                    conn.commit()
                    st.success(f"Password reset for {reset_student}!")
                    st.balloons()
    # STUDY MATERIALS
    with tabs[7]:
        
        st.title("📚 Study Materials Management")
        
        # ========== UPLOAD NEW MATERIAL ==========
        st.subheader("📤 Upload New Study Material")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Select Semester
            sems_material = pd.read_sql_query("SELECT * FROM semesters ORDER BY name ASC", conn)
            
            if sems_material.empty:
                st.warning("Please create semesters first.")
            else:
                material_semester = st.selectbox("Select Semester", sems_material["name"], key="material_semester")
                material_sem_id = int(sems_material[sems_material["name"] == material_semester]["id"].values[0])
                
                # Get subjects for selected semester
                subjects_material = pd.read_sql_query(
                    "SELECT * FROM subjects WHERE semester_id=?",
                    conn,
                    params=(material_sem_id,)
                )
                
                if subjects_material.empty:
                    st.warning("No subjects found for this semester. Please create subjects first.")
                    material_subject_id = None
                else:
                    material_subject = st.selectbox(
                        "Select Subject", 
                        subjects_material["name"], 
                        key="material_subject"
                    )
                    material_subject_id = int(subjects_material[subjects_material["name"] == material_subject]["id"].values[0])
        
        with col2:
            material_title = st.text_input("Material Title", placeholder="e.g., Chapter 3 - Structural Analysis")
            material_description = st.text_area("Description (Optional)", placeholder="Brief description of the material...")
        
        # File Upload
        uploaded_file = st.file_uploader(
            "Upload Study Material (PDF, DOCX, PPTX, ZIP)",
            type=["pdf", "docx", "pptx", "zip", "jpg", "png"],
            key="study_material_upload"
        )
        
        if st.button("📤 Upload Material", type="primary", use_container_width=True):
            
            if not material_title.strip():
                st.error("⚠️ Please enter a title for the material.")
            elif not uploaded_file:
                st.error("⚠️ Please select a file to upload.")
            elif material_subject_id is None:
                st.error("⚠️ Please select a subject.")
            else:
                try:
                    # Save file
                    timestamp = datetime.now(NST).strftime("%Y%m%d_%H%M%S")
                    file_extension = uploaded_file.name.split(".")[-1]
                    file_path = "study_materials/{}_{}.{}".format(
                        timestamp,
                        material_title.replace(" ", "_"),
                        file_extension
                    )
                    
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    if file_extension.lower() == "pdf":
                        apply_watermark(file_path)
                    
                    # Save to database
                    c.execute("""
                    INSERT INTO study_materials(
                        title, 
                        subject_id, 
                        semester_id, 
                        file_path, 
                        description, 
                        upload_date, 
                        uploaded_by
                    )
                    VALUES(?, ?, ?, ?, ?, ?, ?)
                    """, (
                        material_title.strip(),
                        int(material_subject_id),
                        int(material_sem_id),
                        file_path,
                        material_description.strip(),
                        str(datetime.now(NST)),
                        int(st.session_state.user_id)
                    ))
                    
                    conn.commit()
                    with st.spinner("Notifying students..."):
                        email_subject = f"📚 New Study Material: {material_title.strip()}"
                        email_body = f"Hello,\n\nNew study material '{material_title.strip()}' has been uploaded for {material_subject}.\n\nPlease log into The N-Streamlines to download it."
                        e_success, e_msg = send_email_notification(material_sem_id, email_subject, email_body)
                    # ----------------------------

                    st.success("✅ Study material uploaded successfully!")
                    st.balloons()
                    st.rerun()
                    
                except Exception as e:
                    st.error("Error uploading material: {}".format(str(e)))
        
        st.divider()
        
        # ========== VIEW/MANAGE MATERIALS ==========
        st.subheader("📋 Uploaded Study Materials")
        
        # Filter by semester
        filter_sems = pd.read_sql_query("SELECT * FROM semesters ORDER BY name ASC", conn)
        
        if not filter_sems.empty:
            filter_semester = st.selectbox(
                "Filter by Semester", 
                ["All"] + filter_sems["name"].tolist(), 
                key="filter_materials_sem"
            )
            
            # Query materials
            if filter_semester == "All":
                materials_df = pd.read_sql_query("""
                SELECT 
                    study_materials.id,
                    study_materials.title,
                    subjects.name as subject,
                    semesters.name as semester,
                    study_materials.description,
                    study_materials.file_path,
                    study_materials.upload_date
                FROM study_materials
                JOIN subjects ON study_materials.subject_id = subjects.id
                JOIN semesters ON study_materials.semester_id = semesters.id
                ORDER BY study_materials.upload_date DESC
                """, conn)
            else:
                filter_sem_id = int(filter_sems[filter_sems["name"] == filter_semester]["id"].values[0])
                materials_df = pd.read_sql_query("""
                SELECT 
                    study_materials.id,
                    study_materials.title,
                    subjects.name as subject,
                    semesters.name as semester,
                    study_materials.description,
                    study_materials.file_path,
                    study_materials.upload_date
                FROM study_materials
                JOIN subjects ON study_materials.subject_id = subjects.id
                JOIN semesters ON study_materials.semester_id = semesters.id
                WHERE study_materials.semester_id = ?
                ORDER BY study_materials.upload_date DESC
                """, conn, params=(filter_sem_id,))
            
            if materials_df.empty:
                st.info("📭 No study materials uploaded yet.")
            else:
                st.dataframe(
                    materials_df[["semester", "subject", "title", "upload_date"]],
                    use_container_width=True,
                    hide_index=True
                )
                
                st.info("📊 Total Materials: **{}**".format(len(materials_df)))
                
                st.divider()
                
                # Individual material cards with download and delete
                st.subheader("📚 Material Details")
                
                for _, material in materials_df.iterrows():
                    with st.expander("📄 {} - {}".format(material['subject'], material['title'])):
                        
                        col_a, col_b = st.columns([3, 1])
                        
                        with col_a:
                            st.write("**Semester:** {}".format(material['semester']))
                            st.write("**Subject:** {}".format(material['subject']))
                            st.write("**Title:** {}".format(material['title']))
                            st.write("**Uploaded:** {}".format(material['upload_date']))
                            if material['description']:
                                st.write("**Description:** {}".format(material['description']))
                        
                        with col_b:
                            # Download button
                            if material['file_path'] and os.path.exists(material['file_path']):
                                with open(material['file_path'], "rb") as f:
                                    st.download_button(
                                        "📥 Download",
                                        f,
                                        file_name=os.path.basename(material['file_path']),
                                        key="download_material_{}".format(material['id']),
                                        use_container_width=True
                                    )
                            
                            # Delete button
                            if st.button("🗑️ Delete", key="delete_material_{}".format(material['id']), use_container_width=True):
                                try:
                                    # Delete file
                                    if os.path.exists(material['file_path']):
                                        os.remove(material['file_path'])
                                    
                                    # Delete from database
                                    c.execute("DELETE FROM study_materials WHERE id=?", (material['id'],))
                                    conn.commit()
                                    
                                    st.success("✅ Material deleted!")
                                    st.rerun()
                                except Exception as e:
                                    st.error("Error deleting: {}".format(str(e)))
        # STORAGE MANAGEMENT
    with tabs[8]:
        
        st.title("💾 Storage & File Management")
        st.markdown("---")
        st.markdown("""
        <div style='background-color: #f0f8ff; padding: 15px; border-radius: 10px; border-left: 4px solid #004b87;'>
            <h4 style='color: #004b87; margin-top: 0;'>🌊 The N-Streamlines Storage Monitor</h4>
            <p style='color: #555; margin-bottom: 0;'>Keep your platform clean and optimized</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # Get storage stats
        stats = get_storage_stats()
        
        # ========== STORAGE USAGE OVERVIEW ==========
        st.subheader("📊 Current Storage Usage")
        
        if stats:
            cols = st.columns(len(stats))
            
            total_size = 0
            total_files = 0
            
            for idx, (label, data) in enumerate(stats.items()):
                with cols[idx]:
                    st.metric(
                        label,
                        "{} MB".format(data['size_mb']),
                        "{} files".format(data['file_count'])
                    )
                    total_size += data['size_mb']
                    total_files += data['file_count']
            
            st.divider()
            
            col_total1, col_total2, col_total3 = st.columns(3)
            
            with col_total1:
                st.metric("📦 Total Platform Storage", "{} MB".format(round(total_size, 2)))
            
            with col_total2:
                st.metric("📄 Total Files", total_files)
            
            with col_total3:
                # Estimate GitHub limit (1GB = 1024 MB)
                percent_used = (total_size / 1024) * 100
                st.metric("GitHub Repo Usage", "{}%".format(round(percent_used, 1)))
            
            # Warning if approaching limit
            if percent_used > 80:
                st.error("⚠️ **Critical:** Approaching GitHub 1GB storage limit! Run cleanup immediately.")
            elif percent_used > 50:
                st.warning("⚠️ **Warning:** Using over 50% of recommended storage. Consider cleanup.")
        
        else:
            st.info("No storage data available yet.")
        
        st.divider()
        
        # ========== ORPHANED FILE CLEANUP ==========
        st.subheader("🧹 Automatic File Cleanup")
        
        st.markdown("""
        <div style='background-color: #fff4e6; padding: 12px; border-radius: 8px; border-left: 3px solid #ff9800;'>
            <p style='margin: 0; color: #e65100;'>
                <strong>⚠️ What are orphaned files?</strong><br>
                Files that exist on disk but are no longer referenced in the database 
                (e.g., from deleted assignments, students, or semesters).
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("")
        
        col_cleanup1, col_cleanup2 = st.columns([1, 2])
        
        with col_cleanup1:
            if st.button("🧹 Scan & Clean Orphaned Files", type="primary", use_container_width=True):
                
                with st.spinner("🔍 Scanning for orphaned files..."):
                    deleted, space_freed = cleanup_orphaned_files()
                
                if deleted > 0:
                    st.success("✅ **Cleanup Complete!**")
                    st.write("- **Files Deleted:** {}".format(deleted))
                    st.write("- **Space Freed:** {} MB".format(space_freed))
                    st.balloons()
                    st.rerun()
                else:
                    st.info("✨ **Platform is clean!** No orphaned files found.")
        
        with col_cleanup2:
            st.info("""
            **Safe Operation:**
            - Only removes files NOT in database
            - Does NOT delete active assignments/submissions
            - Recommended: Run monthly
            """)
        
        st.divider()
        
        # ========== FILE BROWSER ==========
        st.subheader("📁 File Browser & Inspector")
        
        folder = st.selectbox("Select Folder to Inspect", [
            "assignment_files",
            "submission_files", 
            "study_materials",
            "data"
        ])
        
        if os.path.exists(folder):
            files = []
            for filename in os.listdir(folder):
                file_path = os.path.join(folder, filename)
                if os.path.isfile(file_path):
                    try:
                        size_mb = round(os.path.getsize(file_path) / (1024 * 1024), 2)
                        # Get file modification time
                        mod_time = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M')
                        
                        files.append({
                            'Filename': filename,
                            'Size (MB)': size_mb,
                            'Modified': mod_time,
                            'Path': file_path
                        })
                    except:
                        continue
            
            if files:
                df_files = pd.DataFrame(files)
                # Sort by size (largest first)
                df_files = df_files.sort_values('Size (MB)', ascending=False)
                
                st.dataframe(
                    df_files[['Filename', 'Size (MB)', 'Modified']], 
                    use_container_width=True, 
                    hide_index=True
                )
                
                col_info1, col_info2 = st.columns(2)
                
                with col_info1:
                    st.info("📊 **Total Files:** {}".format(len(files)))
                
                with col_info2:
                    total_folder_size = sum([f['Size (MB)'] for f in files])
                    st.info("💾 **Folder Size:** {} MB".format(round(total_folder_size, 2)))
                
                # Show largest files
                if len(files) > 5:
                    st.write("**🔝 Top 5 Largest Files:**")
                    top_5 = df_files.head(5)[['Filename', 'Size (MB)']]
                    st.dataframe(top_5, use_container_width=True, hide_index=True)
            
            else:
                st.info("📭 No files in this folder")
        else:
            st.warning("⚠️ Folder does not exist yet")
        
        st.divider()
        
        # ========== QUICK STATS ==========
        st.subheader("📈 Platform Statistics")
        
        col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
        
        with col_stat1:
            semester_count = pd.read_sql_query("SELECT COUNT(*) as count FROM semesters", conn).iloc[0]['count']
            st.metric("🎓 Semesters", semester_count)
        
        with col_stat2:
            student_count = pd.read_sql_query("SELECT COUNT(*) as count FROM users WHERE role='student'", conn).iloc[0]['count']
            st.metric("👥 Students", student_count)
        
        with col_stat3:
            assignment_count = pd.read_sql_query("SELECT COUNT(*) as count FROM assignments", conn).iloc[0]['count']
            st.metric("📝 Assignments", assignment_count)
        
        with col_stat4:
            submission_count = pd.read_sql_query("SELECT COUNT(*) as count FROM submissions", conn).iloc[0]['count']
            st.metric("📤 Submissions", submission_count)
            st.divider()
        
        # ========== DATABASE BACKUP & RESTORE ==========
        st.subheader("💾 Database Backup & Restore")
        
        st.warning("⚠️ **Important:** After restoring a backup, you must refresh the page to reconnect to the database.")
        
        col_backup1, col_backup2 = st.columns(2)
        
        with col_backup1:
            st.markdown("**📦 Create New Backup**")
            st.info("Creates a timestamped backup of the current database. Last 10 backups are kept automatically.")
            
            if st.button("📦 Create Backup Now", use_container_width=True, type="primary"):
                with st.spinner("Creating backup..."):
                    success, message = create_database_backup()
                
                if success:
                    st.success("✅ {}".format(message))
                    st.balloons()
                else:
                    st.error("❌ {}".format(message))
        
        with col_backup2:
            st.markdown("**🔄 Restore from Backup**")
            
            backups = get_backup_list()
            
            if backups:
                # Display backups in a nice format
                backup_options = {
                    "{} ({} KB)".format(b['date'], b['size_kb']): b['path']
                    for b in backups
                }
                
                selected_backup_display = st.selectbox(
                    "Select backup to restore",
                    list(backup_options.keys()),
                    key="restore_backup_select"
                )
                
                if selected_backup_display:
                    selected_backup_path = backup_options[selected_backup_display]
                    
                    # Two-step confirmation
                    if st.button("⚠️ Restore Database", use_container_width=True):
                        st.error("🚨 **DANGER ZONE** 🚨")
                        st.write("This will replace the current database!")
                        
                        col_confirm1, col_confirm2 = st.columns(2)
                        
                        with col_confirm1:
                            if st.button("✅ YES, RESTORE", type="primary", use_container_width=True, key="confirm_restore_yes"):
                                with st.spinner("Restoring database..."):
                                    success, message = restore_database_from_backup(selected_backup_path)
                                
                                if success:
                                    st.success("✅ {}".format(message))
                                    st.info("🔄 Please REFRESH the page now (Ctrl+R or Cmd+R)")
                                else:
                                    st.error("❌ {}".format(message))
                        
                        with col_confirm2:
                            if st.button("❌ Cancel", use_container_width=True, key="confirm_restore_no"):
                                st.info("Restore cancelled")
            else:
                st.info("📭 No backups available yet. Create your first backup!")
        
        st.divider()
        
        # Show backup history
        if backups:
            with st.expander("📜 Backup History"):
                backup_df = pd.DataFrame(backups)
                st.dataframe(
                    backup_df[['filename', 'date', 'size_kb']],
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        'filename': 'Backup File',
                        'date': 'Created On',
                        'size_kb': 'Size (KB)'
                    }
                )
    # STUDENT PROFILES
    with tabs[9]:
        
        st.title("👤 Student Profile Viewer")
        
        # Select student
        all_students = pd.read_sql_query("""
        SELECT users.id, users.username, users.full_name, semesters.name as semester
        FROM users
        LEFT JOIN semesters ON users.semester_id = semesters.id
        WHERE users.role='student'
        ORDER BY users.username ASC
        """, conn)
        
        if all_students.empty:
            st.info("No students registered yet.")
        else:
            # Search or select
            col_profile1, col_profile2 = st.columns([2, 1])
            
            with col_profile1:
                search_profile = st.text_input(
                    "🔍 Search student by name or username",
                    key="search_profile"
                )
            
            with col_profile2:
                if search_profile:
                    filtered = all_students[
                        all_students['username'].str.contains(search_profile, case=False) |
                        all_students['full_name'].str.contains(search_profile, case=False)
                    ]
                else:
                    filtered = all_students
            
            if filtered.empty:
                st.warning("No students found")
            else:
                student_options = {
                    "{} ({}) - {}".format(row['username'], row['full_name'], row['semester']): row['id']
                    for _, row in filtered.iterrows()
                }
                
                selected = st.selectbox("Select Student", list(student_options.keys()))
                
                if selected:
                    student_id = student_options[selected]
                    profile = get_student_profile(student_id)
                    
                    if profile:
                        st.divider()
                        
                        # Header
                        st.markdown("""
                        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                    padding: 20px; border-radius: 10px; color: white;'>
                            <h2 style='margin:0;'>{}</h2>
                            <p style='margin:5px 0 0 0;'>@{} | {}</p>
                        </div>
                        """.format(
                            profile['info']['full_name'],
                            profile['info']['username'],
                            profile['info']['semester']
                        ), unsafe_allow_html=True)
                        st.divider()
                        st.subheader("📊 Personal Growth & Performance")
                        
                        submissions_df = profile['submissions']

                        # Filter only the assignments that have actually been graded by the AI
                        graded_df = submissions_df[submissions_df['marks'].notna() & (submissions_df['marks'] != '')].copy()

                        if not graded_df.empty:
                            # Safely convert marks to numbers
                            graded_df['Marks'] = pd.to_numeric(graded_df['marks'], errors='coerce')
                            # Sort by deadline to show chronological growth over the semester
                            graded_df = graded_df.sort_values(by='deadline')
                            # Create a clean chart data table
                            chart_data = graded_df[['assignment', 'Marks']].set_index('assignment')
                            # Display a line chart showing their progress
                            st.line_chart(chart_data)
                        else:
                            st.info("Waiting for more graded assignments to generate a growth chart.")
                        
                        st.write("")
                        
                        # Statistics
                        col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
                        
                        with col_stat1:
                            st.metric("📤 Total Submissions", profile['stats']['total_submissions'])
                        
                        with col_stat2:
                            st.metric("✅ Graded", profile['stats']['total_graded'])
                        
                        with col_stat3:
                            st.metric("📊 Average Score", "{}/10".format(profile['stats']['average']))
                        
                        with col_stat4:
                            st.metric("🏆 Best Score", "{}/10".format(profile['stats']['highest']))
                        
                        st.divider()
                        
                        # Submissions
                        st.subheader("📋 Submission History")
                        
                        if profile['submissions'].empty:
                            st.info("No submissions yet")
                        else:
                            # Add status column
                            def get_status(row):
                                if row['marks'] and str(row['marks']).strip():
                                    return "✅ Graded ({}/10)".format(row['marks'])
                                else:
                                    return "⏳ Pending"
                            
                            display_df = profile['submissions'].copy()
                            display_df['Status'] = display_df.apply(get_status, axis=1)
                            
                            st.dataframe(
                                display_df[['subject', 'assignment', 'deadline', 'submission_time', 'Status']],
                                use_container_width=True,
                                hide_index=True
                            )
                            
                            # Performance chart
                            graded = display_df[display_df['marks'].notna() & (display_df['marks'] != '')]
                            
                            if not graded.empty:
                                st.divider()
                                st.subheader("📈 Performance Over Time")
                                
                                graded['marks_numeric'] = pd.to_numeric(graded['marks'], errors='coerce')
                                graded_sorted = graded.sort_values('submission_time')
                                
                                st.line_chart(
                                    graded_sorted.set_index('assignment')['marks_numeric']
                                )
# ==========================================================
# ===================== STUDENT =============================
# ==========================================================

elif role == "student":

    tabs = st.tabs(["Assignments","Study Materials", "My Results", "Profile and Settings"])

        # ================= ASSIGNMENTS =================
    # ================= ASSIGNMENTS =================
    with tabs[0]:
        st.title("📝 My Assignments")

        # 1. First, get student's semester info
        student_info = pd.read_sql_query(
            "SELECT semester_id, username FROM users WHERE id=?",
            conn,
            params=(int(st.session_state.user_id),)
        )

        if student_info.empty:
            st.error("Student record not found.")
            st.stop()

        sem_id_raw = student_info.iloc[0]["semester_id"]

        if sem_id_raw is None or str(sem_id_raw).strip() == "":
            st.warning("You are not assigned to a semester. Please Contact your Lecturer")
            st.stop()

        # 2. Define sem_id clearly as an integer
        sem_id = int(sem_id_raw)

        # 3. NOW load announcements using that sem_id
        announcements = get_announcements_for_semester(sem_id)
        
        if not announcements.empty:
            st.subheader("📢 Announcements")
            for _, ann in announcements.iterrows():
                # Color based on priority
                if ann['priority'] == 'Urgent':
                    color = '#ff4444'
                    icon = '🚨'
                elif ann['priority'] == 'Important':
                    color = '#ff9800'
                    icon = '⚠️'
                else:
                    color = '#004b87'
                    icon = '📢'
                
                st.markdown("""
                <div style='background-color: #f8f9fa; padding: 15px; border-radius: 8px; 
                            border-left: 6px solid {}; margin-bottom: 10px;'>
                    <h4 style='margin:0; color: {};'>{} {}</h4>
                    <p style='color: #333333; margin: 10px 0; font-size: 1.1em;'>{}</p>
                    <small style='color: #666666;'>Posted by {} on {}</small>
                </div>
                """.format(
                    color, 
                    color,
                    icon,
                    ann['title'],
                    ann['message'],
                    ann['author'],
                    ann['created_at'][:16]
                ), unsafe_allow_html=True)
            
            st.divider()

        # 4. Continue with the rest of your Assignment logic...
        # (Deadline reminders, assignment list, etc.)

        st.title("📝 My Assignments")

        # Get student's semester
        student_info = pd.read_sql_query(
            "SELECT semester_id, username FROM users WHERE id=?",
            conn,
            params=(int(st.session_state.user_id),)
        )

        if student_info.empty:
            st.error("Student record not found.")
            st.stop()

        sem_id_raw = student_info.iloc[0]["semester_id"]

        if sem_id_raw is None or str(sem_id_raw).strip() == "":
            st.warning("You are not assigned to a semester. Please Contact your Lecturer")
            st.stop()

        sem_id = int(sem_id_raw)

        # Get semester name
        semester_info = pd.read_sql_query(
            "SELECT name FROM semesters WHERE id=?",
            conn,
            params=(sem_id,)
        )
        
        if not semester_info.empty:
            st.info("📚 Semester: **{}**".format(semester_info.iloc[0]['name']))
        
        # ========== DEADLINE REMINDER DASHBOARD ==========
        st.subheader("⏰ Deadline Reminders")
        
        # Get all assignments for student's semester
        all_assignments = pd.read_sql_query("""
        SELECT 
            assignments.id,
            assignments.title,
            assignments.deadline,
            subjects.name as subject
        FROM assignments
        JOIN subjects ON assignments.subject_id = subjects.id
        WHERE subjects.semester_id=?
        ORDER BY assignments.deadline ASC
        """, conn, params=(sem_id,))
        
        if not all_assignments.empty:
            # Check submission status
            overdue = []
            due_today = []
            due_soon = []
            upcoming = []
            completed = []
            
            for _, assignment in all_assignments.iterrows():
                # Check if submitted
                submission = pd.read_sql_query("""
                SELECT id FROM submissions
                WHERE assignment_id=? AND student_id=?
                """, conn, params=(int(assignment['id']), int(st.session_state.user_id)))
                
                days, status, color = get_deadline_status(assignment['deadline'])
                
                assignment_info = {
                    'id': assignment['id'],
                    'title': assignment['title'],
                    'subject': assignment['subject'],
                    'deadline': assignment['deadline'],
                    'days': days,
                    'status': status,
                    'color': color
                }
                
                if not submission.empty:
                    completed.append(assignment_info)
                elif status == "Overdue":
                    overdue.append(assignment_info)
                elif status == "Due Today":
                    due_today.append(assignment_info)
                elif status == "Due Soon":
                    due_soon.append(assignment_info)
                else:
                    upcoming.append(assignment_info)
            
            # Display metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("🔴 Overdue", len(overdue))
            with col2:
                st.metric("🟠 Due Today", len(due_today))
            with col3:
                st.metric("🟡 Due Soon", len(due_soon))
            with col4:
                st.metric("✅ Completed", len(completed))
            
            st.divider()
            
            # Show overdue assignments (if any)
            if overdue:
                st.error("🔴 **OVERDUE ASSIGNMENTS - Cannot submit!!**")
                for assign in overdue:
                    st.warning("⚠️ **{}** - {} (Overdue by {} days)".format(
                        assign['subject'],
                        assign['title'],
                        abs(assign['days'])
                    ))
            
            # Show due today (if any)
            if due_today:
                st.warning("🟠 **DUE TODAY - Last Chance!**")
                for assign in due_today:
                    st.info("⏰ **{}** - {}".format(assign['subject'], assign['title']))
            
            # Show due soon (if any)
            if due_soon:
                st.info("🟡 **DUE SOON - Complete These First!**")
                for assign in due_soon:
                    st.write("📌 **{}** - {} ({} days left)".format(
                        assign['subject'],
                        assign['title'],
                        assign['days']
                    ))
            
            st.divider()
        
        # ========== ASSIGNMENT LIST WITH STATUS ==========
        st.subheader("📋 All Assignments")
        
        # Get assignments for student's semester
        assignments = pd.read_sql_query("""
        SELECT assignments.*, subjects.name as subject
        FROM assignments
        JOIN subjects ON assignments.subject_id = subjects.id
        WHERE subjects.semester_id=?
        ORDER BY assignments.deadline ASC
        """, conn, params=(sem_id,))

        if assignments.empty:
            st.info("📭 No assignments available for your semester.")
        else:
            for index, row in assignments.iterrows():
                
                # Check submission status
                existing_submission = pd.read_sql_query("""
                SELECT * FROM submissions
                WHERE assignment_id=? AND student_id=?
                """, conn, params=(int(row["id"]), int(st.session_state.user_id)))
                
                # Get deadline status
                deadline_display = format_deadline_display(row['deadline'])
                
                # Create expander title with status
                if not existing_submission.empty:
                    expander_title = "✅ {} - {} | {}".format(
                        row['subject'],
                        row['title'],
                        deadline_display
                    )
                else:
                    expander_title = "{} - {} | {}".format(
                        row['subject'],
                        row['title'],
                        deadline_display
                    )
                
                with st.expander(expander_title):

                    # 1. DOWNLOAD ASSIGNMENT FILE
                    if row["question_file"] and os.path.exists(row["question_file"]):
                        with open(row["question_file"], "rb") as f:
                            st.download_button(
                                "📥 Download Assignment Question",
                                f,
                                file_name=os.path.basename(row["question_file"]),
                                key="download_q_{}".format(row['id'])
                            )
                    else:
                        st.info("No assignment file attached by lecturer.")

                    st.divider()

                    # 2. DEADLINE CALCULATIONS (NEW)
                    try:
                        # Convert stored deadline string to date object
                        deadline_date = datetime.strptime(str(row['deadline']), '%Y-%m-%d').date()
                        current_date = datetime.now(NST).date()
                        is_late = current_date > deadline_date
                    except:
                        is_late = False

                    # 3. SUBMISSION STATUS LOGIC
                    if not existing_submission.empty:
                        # Case A: Already submitted
                        st.success("✅ You have already submitted this assignment.")

                        submission_time = existing_submission.iloc[0]["submission_time"]
                        st.write("**Submitted on:** {}".format(submission_time))

                        # Show marks if graded
                        marks = existing_submission.iloc[0]["marks"]
                        if marks and str(marks).strip():
                            st.metric("🎯 Marks Awarded", str(marks) + "/10")
                        else:
                            st.info("⏳ Not graded yet")

                        # Allow download of submitted file
                        submitted_file = existing_submission.iloc[0]["submission_file"]
                        if submitted_file and os.path.exists(submitted_file):
                            with open(submitted_file, "rb") as f:
                                st.download_button(
                                    "📥 Download My Submission",
                                    f,
                                    file_name=os.path.basename(submitted_file),
                                    key="download_sub_{}".format(row['id'])
                                )

                    elif is_late:
                        # Case B: Not submitted and deadline passed (LOCKDOWN)
                        st.error("🔒 **Deadline Locked:** This assignment closed on {}.".format(row['deadline']))
                        st.info("Late submissions are not accepted through the portal. Please contact Er. Nirajan Katuwal.")
                    
                    else:
                        # Case C: Not submitted and deadline is still open
                        days_left, _, _ = get_deadline_status(row['deadline'])
                        if days_left == 0:
                            st.warning("⚠️ **Final Call:** This assignment is due today!")
                        elif days_left is not None and days_left <= 2:
                            st.info("🟡 Only {} days left to submit!".format(days_left))

                                                # UPLOAD NEW SUBMISSION
                        uploaded = st.file_uploader(
                            "📤 Upload Your Answer PDF",
                            type=["pdf"],
                            key="upload_{}".format(row['id'])
                        )

                        if st.button("Submit Assignment", key="submit_{}".format(row['id']), type="primary"):

                            if not uploaded:
                                st.warning("⚠️ Please upload a PDF file before submitting.")
                            else:
                                timestamp = datetime.now(NST).strftime("%Y%m%d_%H%M%S")
                                file_path = "submission_files/" + str(st.session_state.username) + "_" + str(row['id']) + "_" + timestamp + ".pdf"

                                with open(file_path, "wb") as f:
                                    f.write(uploaded.getbuffer())

                                c.execute("""
                                INSERT INTO submissions(
                                    assignment_id,
                                    student_id,
                                    submission_time,
                                    submission_file,
                                    marks,
                                    ai_summary
                                )
                                VALUES(?,?,?,?,?,?)
                                """, (
                                    int(row["id"]),
                                    int(st.session_state.user_id),
                                    str(datetime.now(NST)),
                                    file_path,
                                    "",
                                    ""
                                ))

                                conn.commit()
                                
                                # Check if submitted on time
                                if days >= 0:
                                    st.success("✅ Assignment submitted successfully on time!")
                                else:
                                    st.warning("⚠️ Assignment submitted {} days late.".format(abs(days)))
                                
                                st.balloons()
                                st.rerun()

        # ================= STUDY MATERIALS =================
    with tabs[1]:
        
        st.title("📚 Study Materials")
        
        # Get student's semester
        student_info = pd.read_sql_query(
            "SELECT semester_id FROM users WHERE id=?",
            conn,
            params=(int(st.session_state.user_id),)
        )
        
        if student_info.empty or student_info.iloc[0]["semester_id"] is None:
            st.warning("⚠️ You are not assigned to a semester. Please contact your lecturer.")
        else:
            sem_id = int(student_info.iloc[0]["semester_id"])
            
            # Get semester name
            semester_info = pd.read_sql_query(
                "SELECT name FROM semesters WHERE id=?",
                conn,
                params=(sem_id,)
            )
            
            if not semester_info.empty:
                st.info("📚 Study Materials for: **{}**".format(semester_info.iloc[0]['name']))
            
            # Get all materials for student's semester
            materials = pd.read_sql_query("""
            SELECT 
                study_materials.id,
                study_materials.title,
                subjects.name as subject,
                study_materials.description,
                study_materials.file_path,
                study_materials.upload_date
            FROM study_materials
            JOIN subjects ON study_materials.subject_id = subjects.id
            WHERE study_materials.semester_id = ?
            ORDER BY subjects.name ASC, study_materials.upload_date DESC
            """, conn, params=(sem_id,))
            
            if materials.empty:
                st.info("📭 No study materials available yet.")
            else:
                # Group by subject
                subjects_list = materials['subject'].unique()
                
                for subject in subjects_list:
                    st.subheader("📖 {}".format(subject))
                    
                    subject_materials = materials[materials['subject'] == subject]
                    
                    for _, material in subject_materials.iterrows():
                        with st.expander("📄 {}".format(material['title'])):
                            
                            col1, col2 = st.columns([3, 1])
                            
                            with col1:
                                st.write("**Subject:** {}".format(material['subject']))
                                st.write("**Uploaded:** {}".format(material['upload_date']))
                                if material['description']:
                                    st.write("**Description:**")
                                    st.info(material['description'])
                            
                            with col2:
                                # Download button
                                if material['file_path'] and os.path.exists(material['file_path']):
                                    with open(material['file_path'], "rb") as f:
                                        st.download_button(
                                            "📥 Download",
                                            f,
                                            file_name=os.path.basename(material['file_path']),
                                            key="student_download_{}".format(material['id']),
                                            use_container_width=True,
                                            type="primary"
                                        )
                                else:
                                    st.error("File not found")
                    
                    st.divider()
    # ================= STUDENT RESULTS (ENHANCED ACCOUNTABILITY) =================
    with tabs[2]:
        st.header("📝 My Official Internal Performance")
        
        # 1. Core Data Retrieval
        student_id = int(st.session_state.user_id)
        # Use the sem_id already defined in your student section
        
        # Define the Hydraulics weightages for calculations
        hyd_scheme = {
            'theory_full_marks': 40, 'prac_full_marks': 25,
            't_weight_att': 0.10, 't_weight_hw': 0.25, 't_weight_other': 0.15, 
            't_weight_mid': 0.25, 't_weight_final': 0.25,
            'p_weight_att': 0.20, 'p_weight_perf': 0.20, 'p_weight_report': 0.20, 
            'p_weight_test': 0.20, 'p_weight_viva': 0.20
        }

        # 2. Display Official Internal Summary
        st.subheader("📊 Official Internal Totals")
        subjects = pd.read_sql_query("SELECT id, name FROM subjects WHERE semester_id=?", conn, params=(sem_id,))
        
        for _, sub in subjects.iterrows():
            with st.expander(f"📘 {sub['name']} - Official Standing"):
                # Fetch official internal marks
                m = pd.read_sql_query("SELECT * FROM student_marks WHERE student_id=? AND subject_id=?", 
                                     conn, params=(student_id, sub['id']))
                
                if m.empty:
                    st.info("The lecturer has not finalized official internal totals for this subject yet.")
                else:
                    row = m.iloc[0].to_dict()
                    t_total, t_eligible = calculate_internal_theory(row, sub['id'],conn)
                    p_total, p_eligible = calculate_internal_practical(row, sub['id'],conn)
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        st.metric("Theory Internal", f"{t_total}/40")
                        if t_eligible: st.success("✅ Eligible (Theory)")
                        else: st.error("❌ Ineligible (Att < 70%)")
                    with c2:
                        st.metric("Practical Internal", f"{p_total}/25")
                        if p_eligible: st.success("✅ Eligible (Lab)")
                        else: st.error("❌ Ineligible (Lab Att < 70%)")

        st.divider()

        # 3. Individual Assignment Breakdown (Your Original Accountability Logic)
        st.subheader("📑 Individual Assignment Breakdown")
        query_assignments = """
        SELECT s.name as Subject, a.title as Assignment, a.deadline as Deadline, 
               sub.marks as Marks, sub.submission_time as Submitted_On
        FROM assignments a
        INNER JOIN subjects s ON a.subject_id = s.id
        LEFT JOIN submissions sub ON a.id = sub.assignment_id AND sub.student_id = ?
        WHERE s.semester_id = ?
        ORDER BY a.deadline DESC
        """
        results_df = pd.read_sql_query(query_assignments, conn, params=(student_id, sem_id))

        if not results_df.empty:
            display_data = []
            for _, row in results_df.iterrows():
                deadline_date = datetime.strptime(str(row['Deadline']), '%Y-%m-%d').date()
                current_date = datetime.now(NST).date()
                
                raw_marks = row['Marks']
                has_marks = raw_marks is not None and str(raw_marks).strip() != ""
                
                if row['Submitted_On'] is not None:
                    status = "✅ Graded" if has_marks else "⏳ Pending"
                    score = f"{raw_marks}/10" if has_marks else "N/A"
                elif current_date > deadline_date:
                    status = "❌ MISSED"
                    score = "0/10"
                else:
                    status = "📖 Open"
                    score = "Pending"

                display_data.append({
                    "Subject": row['Subject'], "Assignment": row['Assignment'],
                    "Deadline": row['Deadline'], "Status": status, "Marks": score
                })
            
            st.dataframe(pd.DataFrame(display_data), use_container_width=True, hide_index=True)
    # ================= PROFILE & SETTINGS =================
    with tabs[3]:
        st.title("⚙️ Profile & Settings")
        
        # --- NEW EMAIL UPDATE SECTION ---
        st.subheader("📧 Update Email Address")
        st.info("Please provide your email address to receive important platform s and assignment deadlines.")
        
        # Get current email to display
        current_user_info = pd.read_sql_query("SELECT email FROM users WHERE id=?", conn, params=(int(st.session_state.user_id),))
        current_email = current_user_info.iloc[0]['email'] if not pd.isna(current_user_info.iloc[0]['email']) else ""
        
        with st.form("update_email_form"):
            new_email = st.text_input("Email Address", value=current_email, placeholder="student@example.com")
            submit_email = st.form_submit_button("Save Email")
            
            if submit_email:
                if not new_email or "@" not in new_email:
                    st.error("⚠️ Please enter a valid email address.")
                else:
                    try:
                        c.execute("UPDATE users SET email=? WHERE id=?", (new_email.strip(), int(st.session_state.user_id)))
                        conn.commit()
                        st.success("✅ Email updated successfully! You will now receive platform notifications.")
                    except Exception as e:
                        st.error(f"Database error: {str(e)}")
        
        st.divider()
        # --------------------------------
        
        


        st.subheader("🔒 Change Password")
        st.info("Your password is encrypted and cannot be seen by anyone, including the platform administrator.")
        
        # Using a form groups the inputs together neatly
        with st.form("change_password_form"):
            current_pw = st.text_input("Current Password", type="password")
            new_pw = st.text_input("New Password", type="password")
            confirm_pw = st.text_input("Confirm New Password", type="password")
            
            submit_pw = st.form_submit_button("Update Password")
            
            if submit_pw:
                if not current_pw or not new_pw or not confirm_pw:
                    st.error("⚠️ Please fill in all password fields.")
                elif new_pw != confirm_pw:
                    st.error("❌ The new passwords do not match. Please try again.")
                elif len(new_pw) < 6:
                    st.error("⚠️ For your security, the new password must be at least 6 characters long.")
                else:
                    # 1. Fetch the user's current hashed password from the database
                    user_data = pd.read_sql_query(
                        "SELECT password FROM users WHERE id=?", 
                        conn, 
                        params=(int(st.session_state.user_id),)
                    )
                    
                    if not user_data.empty:
                        hashed_db_pw = user_data.iloc[0]["password"]
                        
                        # 2. Verify their current password is correct
                        if check_password(current_pw, hashed_db_pw):
                            
                            # 3. Hash the new password and update the database
                            new_hashed_pw = hash_password(new_pw)
                            
                            try:
                                c.execute(
                                    "UPDATE users SET password=? WHERE id=?", 
                                    (new_hashed_pw, int(st.session_state.user_id))
                                )
                                conn.commit()
                                st.success("✅ Password updated successfully! Please remember your new password.")
                            except Exception as e:
                                st.error(f"Database error: {str(e)}")
                        else:
                            st.error("❌ The current password you entered is incorrect.")
                    else:
                        st.error("User record not found.")
