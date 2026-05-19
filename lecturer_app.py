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

# ========== MINIMALIST MODE-ADAPTIVE PROFESSIONAL UI SKIN ==========
st.markdown("""
<style>
    /* 1. Reset Main Canvas back to native flexible templates */
    .stApp {
        background-color: transparent !important;
        background-image: none !important;
    }

    /* 2. Target the specific header block with an adaptive blue neon glow that reads on both modes */
    .neon-blue-title {
        color: #0088FF !important; /* Vivid brand blue for text structure */
        text-shadow: 0 0 4px rgba(0, 136, 255, 0.6), 
                     0 0 12px rgba(0, 136, 255, 0.4) !important;
        font-weight: 800 !important;
        letter-spacing: 1.5px;
        text-align: center;
        margin-bottom: 0px !important;
    }

    /* 3. Clean Standard UI Institutional Cards for Platform Branding */
    .brand-card-dark {
        text-align: center; 
        padding: 20px; 
        background-color: rgba(128, 128, 128, 0.05); 
        border: 1px solid rgba(128, 128, 128, 0.2); 
        border-radius: 8px; 
        border-top: 4px solid #0088FF; 
        margin-top: 15px;
    }
    .brand-inner-box {
        background-color: rgba(128, 128, 128, 0.03); 
        padding: 10px; 
        border-radius: 6px;
        border: 1px solid rgba(128, 128, 128, 0.1);
    }
    
    .brand-card-dark h4, .brand-card-dark p, .brand-card-dark strong {
        color: inherit !important;
    }

    /* 4. Force high text contrast for progress bar titles on BOTH Light & Dark canvas layers */
    .caption-white {
        color: inherit !important;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        margin-bottom: 6px;
    }

    /* Ensure secondary paragraphs and small metric tracking figures obey flexible theme variables */
    div[data-testid="stMarkdownContainer"] p, 
    div[data-testid="stText"] p,
    .element-container p,
    [data-testid="stMetricLabel"] div,
    [data-testid="stMetricValue"] div {
        color: inherit !important;
    }

    /* 🎨 RE-COLOR THE STREAMLIT PROGRESS BARS TO ROYAL BLUE */
    div[data-testid="stProgress"] > div > div > div > div {
        background-color: #0055FF !important; /* Premium Royal Blue Fill */
    }
    
    /* Adaptive track background color channel */
    div[data-testid="stProgress"] > div > div {
        background-color: rgba(128, 128, 128, 0.2) !important;
    }
</style>
""", unsafe_allow_html=True)

# ================= TIMEZONE CONFIG =================
NST = timezone(timedelta(hours=5, minutes=45))
# ================= CONFIG =================

st.set_page_config(
    page_title="The N-streamlines",
    page_icon="🌊",
    layout="wide"
)



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

# ================= GLOBAL SESSION STATE FALLBACKS =================
if "g_univ" not in st.session_state: st.session_state["g_univ"] = "Tribhuvan University"
if "g_inst_body" not in st.session_state: st.session_state["g_inst_body"] = "Institute of Engineering"
if "g_college" not in st.session_state: st.session_state["g_college"] = "Himalaya College of Engineering"
if "g_dept" not in st.session_state: st.session_state["g_dept"] = "Civil"
if "g_prog" not in st.session_state: st.session_state["g_prog"] = "BE Civil"
if "g_batch" not in st.session_state: st.session_state["g_batch"] = "2080"
if "g_yp" not in st.session_state: st.session_state["g_yp"] = "III/I"
if "g_exam_title" not in st.session_state: st.session_state["g_exam_title"] = "Internal Assessment Examination 2082 Chaitra"
if "g_teacher" not in st.session_state: st.session_state["g_teacher"] = "Er. Nirajan Katuwal"
if "g_hod" not in st.session_state: st.session_state["g_hod"] = "MD Abrar Alam"
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
def score_to_words(score_num):
    """
    Utility function to automatically convert numeric marks integers 
    into standard academic textbook word formatting for university ledgers.
    """
    try:
        val = int(round(float(score_num)))
    except (ValueError, TypeError):
        return "Zero"
        
    words_map = {
        0: "Zero", 1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five",
        6: "Six", 7: "Seven", 8: "Eight", 9: "Nine", 10: "Ten",
        11: "Eleven", 12: "Twelve", 13: "Thirteen", 14: "Fourteen", 15: "Fifteen",
        16: "Sixteen", 17: "Seventeen", 18: "Eighteen", 19: "Nineteen", 20: "Twenty",
        21: "Twenty One", 22: "Twenty Two", 23: "Twenty Three", 24: "Twenty Four", 25: "Twenty Five",
        26: "Twenty Six", 27: "Twenty Seven", 28: "Twenty Eight", 29: "Twenty Nine", 30: "Thirty",
        31: "Thirty One", 32: "Thirty Two", 33: "Thirty Three", 34: "Thirty Four", 35: "Thirty Five",
        36: "Thirty Six", 37: "Thirty Seven", 38: "Thirty Eight", 39: "Thirty Nine", 40: "Forty"
    }
    return words_map.get(val, str(val))
#=======ELIGIBILITY CRITERIA=============================
def check_ioe_eligibility(t_pct, p_pct, t_score, p_score):
    """
    Evaluates Theory and Practical board exam eligibility independently.
    Returns: (theory_status, practical_status)
    """
    # Evaluate Theory Component independently
    if t_pct < 70.0:
        theory_status = "❌ NQ (Theory Attendance < 70%)"
    elif float(t_score or 0) < 16.0:
        theory_status = "❌ NQ (Theory Score < 16)"
    else:
        theory_status = "✅ Eligible"
        
    # Evaluate Practical Component independently
    if p_pct < 70.0:
        practical_status = "❌ NQ (Practical Attendance < 70%)"
    elif float(p_score or 0) < 10.0:
        practical_status = "❌ NQ (Practical Score < 10)"
    else:
        practical_status = "✅ Eligible"
        
    return theory_status, practical_status
# ================= DATABASE SAFE MIGRATION TUNNEL =================
# 1. Ensure email column exists
try:
    c.execute("ALTER TABLE users ADD COLUMN email TEXT")
    conn.commit()
except:
    pass 

# 2. Ensure section column exists
try:
    c.execute("ALTER TABLE users ADD COLUMN section TEXT DEFAULT 'A'")
    conn.commit()
except:
    pass 

# 3. 🚨 ADD THIS EXACTLY HERE TO FIX THE CRASH:
try:
    c.execute("ALTER TABLE users ADD COLUMN lab_group TEXT DEFAULT 'Group 1'")
    conn.commit()
except:
    pass

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
# ===================================================================
# ➕ MIGRATION TUNNEL: ADD DYNAMIC RAW CEILINGS TO SUBJECT SCHEMES
# ===================================================================
try:
    c.execute("ALTER TABLE subject_schemes ADD COLUMN t_max_raw_hw REAL DEFAULT 50.0")
    c.execute("ALTER TABLE subject_schemes ADD COLUMN t_max_raw_mid REAL DEFAULT 40.0")
    c.execute("ALTER TABLE subject_schemes ADD COLUMN t_max_raw_final REAL DEFAULT 40.0")
    c.execute("ALTER TABLE subject_schemes ADD COLUMN t_max_raw_other REAL DEFAULT 100.0")
    conn.commit()
except Exception:
    pass
# ===================================================================
# ===================================================================
# ➕ MIGRATION TUNNEL: ADD DYNAMIC RAW CEILINGS TO PRACTICAL SCHEMES
# ===================================================================
try:
    c.execute("ALTER TABLE subject_schemes ADD COLUMN p_max_raw_perf REAL DEFAULT 100.0")
    c.execute("ALTER TABLE subject_schemes ADD COLUMN p_max_raw_report REAL DEFAULT 100.0")
    c.execute("ALTER TABLE subject_schemes ADD COLUMN p_max_raw_test REAL DEFAULT 100.0")
    c.execute("ALTER TABLE subject_schemes ADD COLUMN p_max_raw_viva REAL DEFAULT 100.0")
    conn.commit()
except Exception:
    pass
# ===================================================================
try:
    c.execute("ALTER TABLE subjects ADD COLUMN code TEXT DEFAULT 'CIV-ENGINEERING'")
    conn.commit()
except:
    pass

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

# ===================================================================
# ➕ NEW: SAAS PROTOTYPE DB REGISTRY (ADDED HERE)
# ===================================================================
c.execute("""
CREATE TABLE IF NOT EXISTS system_settings (
    key TEXT PRIMARY KEY,
    value TEXT
)
""")

c.execute("""
INSERT OR IGNORE INTO system_settings (key, value) 
VALUES ('organization_name', 'Himalaya College of Engineering')
""")

c.execute("""
CREATE TABLE IF NOT EXISTS saas_assessments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id INTEGER,
    assessment_name TEXT,  
    max_marks REAL,        
    weightage REAL,        
    UNIQUE(subject_id, assessment_name)
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS saas_student_marks (
    student_id INTEGER,
    assessment_id INTEGER,
    marks_obtained REAL,
    weighted_score REAL,
    PRIMARY KEY (student_id, assessment_id)
)
""")
conn.commit()
# ===================================================================
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
# 1. Create System Settings Table for SaaS Branding
c.execute("""
CREATE TABLE IF NOT EXISTS system_settings (
    key TEXT PRIMARY KEY,
    value TEXT
)
""")

# Insert a default college name if the table is completely empty
c.execute("""
INSERT OR IGNORE INTO system_settings (key, value) 
VALUES ('organization_name', 'My Engineering College')
""")

# 2. Create the Upgraded Assessments & Marks Management Tables
c.execute("""
CREATE TABLE IF NOT EXISTS saas_assessments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id INTEGER,
    assessment_name TEXT,  -- 'Mid-Term Exam' or 'Final Exam'
    max_marks REAL,        -- Dynamic: e.g., 50, 80, 100
    weightage REAL,        -- Dynamic: e.g., 30, 70
    UNIQUE(subject_id, assessment_name)
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS saas_student_marks (
    student_id INTEGER,
    assessment_id INTEGER,
    marks_obtained REAL,
    weighted_score REAL,
    PRIMARY KEY (student_id, assessment_id)
)
""")
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
# ================= LOGIN FLOW GATE =================

if not st.session_state.get("logged_in", False):

    st.markdown("""
        <div style='text-align: center; padding-bottom: 20px;'>
            <h1 class='neon-blue-title' style='font-size: 3em;'>🌊 THE N-STREAMLINES</h1>
            <p style='color: #555; font-size: 1.2em; font-weight: 500; margin-top: 5px;'>
                Developed by Nirajan Katuwal
            </p>
        </div>
        """, unsafe_allow_html=True)
    #-------------------------------------------
    with st.container(border=True):
        user_input = st.text_input("Username").strip()
        pw_input = st.text_input("Password", type="password").strip()

        if st.button("Enter the Flow", use_container_width=True, type="primary"):
            if not user_input or not pw_input:
                st.warning("Please enter both your Username and Password.")
            else:
                res = pd.read_sql_query(
                    "SELECT * FROM users WHERE username=?",
                    conn,
                    params=(user_input,)
                )

                if not res.empty and check_password(pw_input, res.iloc[0]["password"]):
                    st.session_state.logged_in = True
                    st.session_state.user_id = res.iloc[0]["id"]
                    st.session_state.role = res.iloc[0]["role"]
                    st.session_state.username = res.iloc[0]["username"]
                    st.session_state.semester_id = res.iloc[0]["semester_id"]
                    st.session_state.full_name = res.iloc[0]["full_name"]
                    st.session_state.show_splash = True
                    st.rerun()
                else:
                    st.error("❌ Invalid Username or Password. Please check for typos and try again.")
    
    # 🛑 Hard stop here for unauthenticated visitors so down-stream code like Line 757 never executes!
    st.stop()

# ================= AUTHENTICATED DASHBOARD CODE SECURE ZONE =================
# Line 757 will safely execute down here because the script only reaches this point after a successful login!

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
    # 3. Global Developer Branding (Pushed to the bottom - Formatted for Nordic Twilight)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    st.markdown("""
        <div class="brand-card-dark">
            <h4 style='color: #03B5AA; margin-top: 0; margin-bottom: 5px; font-size: 1.1em;'>🌊 The N-Streamlines</h4>
            <p style='font-size: 0.88em; color: #A2A7B5; margin-bottom: 12px; line-height: 1.4;'>
                Advanced Hydro-Informatics &<br>Learning Management
            </p>
            <div class="brand-inner-box">
                <p style='font-size: 0.85em; color: #E2E4E9; margin-bottom: 0;'>
                    Developed & Architected by<br>
                    <strong style='color: #03B5AA;'>Er. Nirajan Katuwal</strong>
                </p>
            </div>
            <p style='font-size: 0.75em; color: #636875; margin-top: 12px; margin-bottom: 0;'>
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
    Unified Institutional Marking Engine:
    Normalizes continuous term assessments using custom database raw ceilings,
    integrates dynamic cumulative assignment scoring (max 50) scaled linearly,
    and enforces a strict 70% attendance gate threshold for structural grace points.
    """
    import pandas as pd
    
    # 1. Fetch weight scheme and raw testing ceilings from the database
    scheme_df = pd.read_sql_query(
        "SELECT * FROM subject_schemes WHERE subject_id = ?", 
        db_conn, 
        params=(int(subject_id),)
    )
    
    # Absolute institutional fallbacks if configuration record is missing
    if scheme_df.empty:
        scheme = {
            'theory_full_marks': 40.0,
            't_weight_att': 0.10, 't_weight_hw': 0.25, 't_weight_mid': 0.25, 't_weight_final': 0.25, 't_weight_other': 0.15,
            't_max_raw_hw': 50.0, 't_max_raw_mid': 40.0, 't_max_raw_final': 40.0, 't_max_raw_other': 100.0
        }
    else:
        scheme = scheme_df.iloc[0].to_dict()

    # 2. Attendance Component Math (Standard 10% weight allocation)
    att_ratio = row['t_att_present'] / row['t_att_total'] if row['t_att_total'] > 0 else 0
    att_score = att_ratio * (scheme['theory_full_marks'] * scheme['t_weight_att'])
    
    # 3. 🧠 CUMULATIVE ASSIGNMENT CALCULATOR (INCREMENTAL GROWTH TRACKING)
    q_all_assigns = "SELECT id FROM assignments WHERE subject_id = ?"
    all_assign_df = pd.read_sql_query(q_all_assigns, db_conn, params=(int(subject_id),))
    total_assignments_count = len(all_assign_df)
    
    # Explicitly calculate denominator based on assignment count (e.g., 5 assignments * 10 = 50.0)
    max_cumulative_raw_ceiling = total_assignments_count * 10.0 if total_assignments_count > 0 else 50.0
        
    # 🛡️ BULLETPROOF MULTI-TENANT STUDENT ID EXTRACTOR
    target_student_id = None
    
    # Check if the active execution context is passing a database ledger row series/dict
    if isinstance(row, dict) or (hasattr(row, 'keys') and callable(getattr(row, 'keys'))):
        if 'id' in row and row['id'] is not None and str(row['id']).strip() != "":
            target_student_id = int(row['id'])
        elif 'student_id' in row and row['student_id'] is not None and str(row['student_id']).strip() != "":
            target_student_id = int(row['student_id'])
            
    # If row extraction yields nothing, inspect global Streamlit Session Memory Core
    if target_student_id is None:
        import streamlit as st
        possible_keys = ['user_id', 'student_id', 'uid', 'username_id', 'id']
        for k in possible_keys:
            if k in st.session_state and st.session_state[k] is not None and str(st.session_state[k]).strip() != "":
                try:
                    target_student_id = int(st.session_state[k])
                    break
                except:
                    pass
                    
    # Fallback absolute emergency safety lock to prevent 0-index calculation drops
    if target_student_id is None:
        target_student_id = 0

    # Query the live database to accumulate the active student's exact earned assignment marks
    q_student_marks = """
    SELECT NULLIF(marks, '') as marks FROM submissions 
    WHERE assignment_id IN (SELECT id FROM assignments WHERE subject_id = ?) AND student_id = ?
    """
    marks_df = pd.read_sql_query(q_student_marks, db_conn, params=(int(subject_id), target_student_id))
    cumulative_raw_earned = 0.0
    if not marks_df.empty:
        for _, marks_row in marks_df.iterrows():
            m_val = marks_row['marks']
            if m_val is not None and str(m_val).strip() != "":
                try: 
                    cumulative_raw_earned += float(m_val)
                except ValueError: 
                    pass

    # ✅ TRULY DYNAMIC REPLACEMENT: Respects the Advanced Configuration Tab settings directly
    cfg_max_hw = float(scheme.get('t_max_raw_hw', 50.0)) if (scheme.get('t_max_raw_hw') and float(scheme.get('t_max_raw_hw')) > 0) else 50.0
    
    # Calculate assignment score dynamically using your Advanced configuration setting denominator
    hw_score = (float(cumulative_raw_earned) / cfg_max_hw) * 10.0
    
    # 4. 🎛️ UNIVERSAL EXAM/TEST NORMALIZATION MATHEMATICS
    # Scale Mid-Term Exam using its dynamic testing ceiling denominator
    raw_max_mid = scheme.get('t_max_raw_mid', 40.0)
    mid_score = (row['t_mid_raw'] / raw_max_mid) * (scheme['theory_full_marks'] * scheme['t_weight_mid'])
    
    # Scale Final Term Exam using its dynamic testing ceiling denominator
    raw_max_final = scheme.get('t_max_raw_final', 40.0)
    final_score = (row['t_final_raw'] / raw_max_final) * (scheme['theory_full_marks'] * scheme['t_weight_final'])
    
    # Scale Continuous Tutorial/Other assessments using its dynamic testing ceiling denominator
    raw_max_other = scheme.get('t_max_raw_other', 100.0)
    other_score = (row['t_other_raw'] / raw_max_other) * (scheme['theory_full_marks'] * scheme['t_weight_other'])
    
    # Aggregate compiled internal credits tally out of 40 marks
    raw_total = att_score + hw_score + mid_score + final_score + other_score
    
    # 5. Enforce 70% Attendance Gate Check for Grace Marks Allocation
    final_total = raw_total
    is_eligible_grace = att_ratio >= 0.70
    
    if is_eligible_grace and row['t_grace'] > 0:
        final_total += min(row['t_grace'], 5) 
        
    return round(final_total, 2), is_eligible_grace
def calculate_internal_practical(row, subject_id, db_conn):
    """
    Dynamically reads both syllabus weightages and the lecturer's custom 
    raw testing ceilings to perfectly normalize any continuous laboratory data 
    down to the official 25-mark practical internal ledger envelope.
    """
    # 1. Fetch weight scheme and raw ceilings from database
    scheme_df = pd.read_sql_query(
        "SELECT * FROM subject_schemes WHERE subject_id = ?", 
        db_conn, 
        params=(int(subject_id),)
    )
    
    # Absolute fallbacks if configuration record is missing
    if scheme_df.empty:
        scheme = {
            'prac_full_marks': 25.0,
            'p_weight_att': 0.20, 'p_weight_perf': 0.20, 'p_weight_report': 0.20, 'p_weight_test': 0.20, 'p_weight_viva': 0.20,
            'p_max_raw_perf': 100.0, 'p_max_raw_report': 100.0, 'p_max_raw_test': 100.0, 'p_max_raw_viva': 100.0
        }
    else:
        scheme = scheme_df.iloc[0].to_dict()

    full_p = scheme['prac_full_marks']
    
    # 2. Lab Attendance Component Math (20% standard weight)
    att_ratio = row['p_att_present'] / row['p_att_total'] if row['p_att_total'] > 0 else 0
    att_score = att_ratio * (full_p * scheme['p_weight_att'])
    
    # 3. 🧠 UNIVERSAL LABORATORY NORMALIZATION MATHEMATICS
    # Scale Lab Performance using its dynamic denominator
    raw_max_perf = scheme.get('p_max_raw_perf', 100.0)
    perf_score = (row['p_perf_raw'] / raw_max_perf) * (full_p * scheme['p_weight_perf'])
    
    # Scale Lab Reports using its dynamic denominator
    raw_max_report = scheme.get('p_max_raw_report', 100.0)
    report_score = (row['p_report_raw'] / raw_max_report) * (full_p * scheme['p_weight_report'])
    
    # Scale Practical Exam Test using its dynamic denominator
    raw_max_test = scheme.get('p_max_raw_test', 100.0)
    test_score = (row['p_test_raw'] / raw_max_test) * (full_p * scheme['p_weight_test'])
    
    # Scale Viva Voce using its dynamic denominator
    raw_max_viva = scheme.get('p_max_raw_viva', 100.0)
    viva_score = (row['p_viva_raw'] / raw_max_viva) * (full_p * scheme['p_weight_viva'])
    
    # Aggregate compiled internal practical credits tally
    raw_total = att_score + perf_score + report_score + test_score + viva_score
    is_eligible = att_ratio >= 0.70
    
    return round(raw_total, 2), is_eligible
  
# ==========================================================
# ===================== LECTURER ============================
# ==========================================================

if role == "lecturer":
    # Ensure this is right under the line: if role == "lecturer":
    
    # ===================================================================
    # 🏫 GLOBAL INSTITUTIONAL PROFILE CONFIGURATION CARD (INPUT ONCE)
    # ===================================================================
    with st.expander("🏫 Global Institutional & Print Settings Registry", expanded=False):
        st.markdown("##### ⚙️ Configure Document Header Credentials (Input Once, Fills All Exports)")
        
        # --- Row 1: Core Institutional Details (UPDATED TO SEPARATE BATCH & YEAR/PART) ---
        c_inst1, c_inst2, c_inst3 = st.columns(3)
        with c_inst1:
            st.text_input("University Title", value=st.session_state["g_univ"], key="g_univ")
            st.text_input("College / Institute Name", value=st.session_state["g_college"], key="g_college")
        with c_inst2:
            st.text_input("Institute Body", value=st.session_state["g_inst_body"], key="g_inst_body")
            st.text_input("Department Handle", value=st.session_state["g_dept"], key="g_dept")
        with c_inst3:
            st.text_input("Programme / Level Title", value=st.session_state["g_prog"], key="g_prog")
            
            # Splitting Batch and Year/Part safely into their own side-by-side inputs
            sub_col1, sub_col2 = st.columns(2)
            with sub_col1:
                st.text_input("Enrollment Batch", value=st.session_state["g_batch"], key="g_batch")
            with sub_col2:
                st.text_input("Current Year/Part", value=st.session_state["g_yp"], key="g_yp")
            
        st.divider()
        
        # --- Row 2: Examination Sheet Credentials ---
        c_exam1, c_exam2, c_exam3 = st.columns(3)
        with c_exam1:
            st.text_input("Examination Header Title", value=st.session_state["g_exam_title"], key="g_exam_title")
            st.text_input("Subject Name Override", value="Engineering Hydrology", key="g_sub_name")
        with c_exam2:
            st.text_input("Subject Code No.", value="ENCE 306", key="g_sub_code")
            st.selectbox("Evaluation Nature Mode", ["Theory", "Practical"], key="g_exam_nature")
        with c_exam3:
            st.number_input("Header Full Marks Ceiling", value=25, key="g_f_marks")
            st.number_input("Header Pass Marks Ceiling", value=10, key="g_p_marks")

        st.divider()

        # --- Row 3: Signing Authorities & Teacher Tracks ---
        c_auth1, c_auth2 = st.columns(2)
        with c_auth1:
            st.text_input("Name of Examiner / Subject Teacher", value=st.session_state["g_teacher"], key="g_teacher")
        with c_auth2:
            st.text_input("Name of Head of Department (HoD)", value=st.session_state["g_hod"], key="g_hod")

    st.write("") # Clean spacing barrier before tab widgets load
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
                
                # ⏱️ Handle Soft Window Evaluation directly in the overview tracking log
                deadline_date = datetime.strptime(str(assignment['deadline']), '%Y-%m-%d').date()
                current_date = datetime.now(NST).date()
                
                today_dt = datetime.now(NST)
                deadline_dt = datetime.combine(deadline_date, datetime.min.time()).replace(tzinfo=NST)
                hours_late = (today_dt - deadline_dt).total_seconds() / 3600.0 if current_date > deadline_date else 0.0

                assignment_info = {
                    'title': assignment['title'],
                    'subject': assignment['subject'],
                    'semester': assignment['semester'],
                    'deadline': assignment['deadline'],
                    'days': days,
                    'status': status,
                    'color': color,
                    'id': assignment['id'],
                    'hours_late': hours_late
                }
                
                # 🧠 RE-ALIGNED MATRIX CLASSIFICATION GATES
                if current_date > deadline_date and hours_late > 48.0:
                    # Only assign to hard Overdue block if it crosses the full 48-hour threshold
                    overdue.append(assignment_info)
                elif status == "Due Today":
                    due_today.append(assignment_info)
                elif (current_date > deadline_date and hours_late <= 48.0) or status == "Due Soon" or status == "This Week":
                    # Keep active grace window entries sitting inside the yellow "Due This Week" tracker panel
                    due_soon.append(assignment_info)
                else:
                    upcoming.append(assignment_info)
            
            # Metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("🔴 Completely Expired (>48h)", len(overdue))
            with col2:
                st.metric("🟠 Due Today", len(due_today))
            with col3:
                st.metric("🟡 In Grace Window / Due Soon", len(due_soon))
            with col4:
                st.metric("🔵 Upcoming", len(upcoming))
            
            st.divider()
            
            # Show details
            if overdue:
                st.error("🔴 **COMPLETELY EXPIRED ASSIGNMENTS (PORTAL LOCKED)**")
                for assign in overdue:
                    with st.expander(f"🔒 {assign['semester']} - {assign['subject']} ({assign['title']})"):
                        st.write(f"**Deadline Was:** {assign['deadline']}")
                        st.write(f"**Locked For:** {int(assign['hours_late'] - 48)} hours past the final grace threshold")
                        
                        submissions = pd.read_sql_query("""
                        SELECT COUNT(*) as count FROM submissions WHERE assignment_id=?
                        """, conn, params=(assign['id'],))
                        st.metric("Final Submissions Count Locked In", submissions.iloc[0]['count'])
            
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
            # ===================================================================
            # ⚙️ ENTERPRISE-GRADE SCHEME CONFIGURATOR PANEL
            # ===================================================================
            st.write("")
            with st.expander("⚙️ Advanced: Configure Subject Marking Schemes (Dynamic Raw Ceilings)"):
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
                    
                    # Read existing settings out of database storage file
                    exist_rule = pd.read_sql_query("SELECT * FROM subject_schemes WHERE subject_id=?", conn, params=(int(target_sub_id),))
                    
                    sc_theory = exist_rule.iloc[0]['theory_full_marks'] if not exist_rule.empty else 40.0
                    sc_prac = exist_rule.iloc[0]['prac_full_marks'] if not exist_rule.empty else 25.0
                    
                    # Read existing raw ceiling setups if present, fallback to defaults if blank
                    ex_max_hw = exist_rule.iloc[0]['t_max_raw_hw'] if (not exist_rule.empty and 't_max_raw_hw' in exist_rule.columns) else 50.0
                    ex_max_mid = exist_rule.iloc[0]['t_max_raw_mid'] if (not exist_rule.empty and 't_max_raw_mid' in exist_rule.columns) else 40.0
                    ex_max_final = exist_rule.iloc[0]['t_max_raw_final'] if (not exist_rule.empty and 't_max_raw_final' in exist_rule.columns) else 40.0
                    ex_max_other = exist_rule.iloc[0]['t_max_raw_other'] if (not exist_rule.empty and 't_max_raw_other' in exist_rule.columns) else 100.0

                    cc1, cc2 = st.columns(2)
                    with cc1:
                        st.markdown("### 📝 Theory Weights & Ceilings")
                        f_theory = st.number_input("Theory Overall Syllabus Ceiling Full Marks", min_value=0.0, max_value=100.0, value=float(sc_theory), key="sch_f_theory")
                        
                        st.markdown("---")
                        w_att = st.slider("Attendance Weight Fraction", 0.0, 1.0, 0.10, key="sch_w_att")
                        
                        st.markdown("##### ✏️ Assignments Configuration")
                        w_hw = st.slider("Homework / Assignment Weight Fraction", 0.0, 1.0, 0.25, key="sch_w_hw")
                        m_raw_hw = st.number_input("Your Total Raw Assignment Testing Limit (Denom):", min_value=1.0, value=float(ex_max_hw), key="sch_m_raw_hw")
                        
                        st.markdown("##### ⏱️ Mid-Term Exam Configuration")
                        w_mid = st.slider("Mid-Term Assessment Weight Fraction", 0.0, 1.0, 0.25, key="sch_w_mid")
                        m_raw_mid = st.number_input("Your Total Raw Mid-Term Test Max Limit (Denom):", min_value=1.0, value=float(ex_max_mid), key="sch_m_raw_mid")
                        
                        st.markdown("##### 🎯 Final Term Exam Configuration")
                        w_final = st.slider("Final Internal Exam Weight Fraction", 0.0, 1.0, 0.25, key="sch_w_final")
                        m_raw_final = st.number_input("Your Total Raw Final Term Test Max Limit (Denom):", min_value=1.0, value=float(ex_max_final), key="sch_m_raw_final")
                        
                        st.markdown("##### 👥 Continuous Tutorial Evaluation")
                        w_other = st.slider("Discipline/Other Continuous Weight Fraction", 0.0, 1.0, 0.15, key="sch_w_other")
                        m_raw_other = st.number_input("Your Continuous Assessment Max Scale Limit (Denom):", min_value=1.0, value=float(ex_max_other), key="sch_m_raw_other")
                        
                    with cc2:
                        st.markdown("### 🧪 Practical Blueprint Settings")
                        f_prac = st.number_input("Practical Overall Syllabus Ceiling Full Marks", min_value=0.0, max_value=100.0, value=float(sc_prac), key="sch_f_prac")
                        
                        # Read existing raw practical ceiling setups if present, fallback to defaults if blank
                        ex_max_perf = exist_rule.iloc[0]['p_max_raw_perf'] if (not exist_rule.empty and 'p_max_raw_perf' in exist_rule.columns) else 100.0
                        ex_max_report = exist_rule.iloc[0]['p_max_raw_report'] if (not exist_rule.empty and 'p_max_raw_report' in exist_rule.columns) else 100.0
                        ex_max_test = exist_rule.iloc[0]['p_max_raw_test'] if (not exist_rule.empty and 'p_max_raw_test' in exist_rule.columns) else 100.0
                        ex_max_viva = exist_rule.iloc[0]['p_max_raw_viva'] if (not exist_rule.empty and 'p_max_raw_viva' in exist_rule.columns) else 100.0

                        st.markdown("---")
                        p_att = st.slider("Lab Attendance Weight Fraction", 0.0, 1.0, 0.20, key="sch_p_att")
                        
                        st.markdown("##### 🔬 Lab Performance Configuration")
                        p_perf = st.slider("Lab Performance Weight Fraction", 0.0, 1.0, 0.20, key="sch_p_perf")
                        m_raw_perf = st.number_input("Your Max Raw Lab Performance Score Ceiling:", min_value=1.0, value=float(ex_max_perf), key="sch_m_raw_perf")
                        
                        st.markdown("##### 📁 Lab Reports Configuration")
                        p_report = st.slider("Lab Reports/Records Weight Fraction", 0.0, 1.0, 0.20, key="sch_p_report")
                        m_raw_report = st.number_input("Your Max Raw Lab Reports Cumulative Tally Ceiling:", min_value=1.0, value=float(ex_max_report), key="sch_m_raw_report")
                        
                        st.markdown("##### 📝 Practical Test Configuration")
                        p_test = st.slider("Practical Exam Test Weight Fraction", 0.0, 1.0, 0.20, key="sch_p_test")
                        m_raw_test = st.number_input("Your Max Raw Practical Exam Test Paper Ceiling:", min_value=1.0, value=float(ex_max_test), key="sch_m_raw_test")
                        
                        st.markdown("##### 🗣️ Viva Voce Configuration")
                        p_viva = st.slider("Viva Voce Assessment Weight Fraction", 0.0, 1.0, 0.20, key="sch_p_viva")
                        m_raw_viva = st.number_input("Your Max Raw Viva Voce Interview Panel Ceiling:", min_value=1.0, value=float(ex_max_viva), key="sch_m_raw_viva")
                    
                    # Safety Tally Check
                    total_ratio = w_att + w_hw + w_mid + w_final + w_other
                    if abs(total_ratio - 1.0) > 0.01:
                        st.warning(f"⚠️ Warning: Distribution fractions sum to {total_ratio:.2f}. For perfect normalization scaling, make sure they balance to exactly 1.00.")
                    
                    # Practical Tally Check
                    total_p_ratio = p_att + p_perf + p_report + p_test + p_viva
                    if abs(total_p_ratio - 1.0) > 0.01:
                        st.warning(f"⚠️ Warning: Practical distribution fractions sum to {total_p_ratio:.2f}. Ensure they balance to exactly 1.00.")

                    if st.button("💾 Lock Dynamic Assessment Schema Parameters", use_container_width=True, type="primary", key="save_scheme_btn"):
                        c.execute("""
                            INSERT INTO subject_schemes (
                                subject_id, theory_full_marks, prac_full_marks, t_weight_att, 
                                t_weight_hw, t_weight_other, t_weight_mid, t_weight_final,
                                t_max_raw_hw, t_max_raw_mid, t_max_raw_final, t_max_raw_other,
                                p_weight_att, p_weight_perf, p_weight_report, p_weight_test, p_weight_viva,
                                p_max_raw_perf, p_max_raw_report, p_max_raw_test, p_max_raw_viva
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            ON CONFLICT(subject_id) DO UPDATE SET
                                theory_full_marks=excluded.theory_full_marks,
                                prac_full_marks=excluded.prac_full_marks,
                                t_weight_att=excluded.t_weight_att,
                                t_weight_hw=excluded.t_weight_hw,
                                t_weight_other=excluded.t_weight_other,
                                t_weight_mid=excluded.t_weight_mid,
                                t_weight_final=excluded.t_weight_final,
                                t_max_raw_hw=excluded.t_max_raw_hw,
                                t_max_raw_mid=excluded.t_max_raw_mid,
                                t_max_raw_final=excluded.t_max_raw_final,
                                t_max_raw_other=excluded.t_max_raw_other,
                                p_weight_att=excluded.p_weight_att,
                                p_weight_perf=excluded.p_weight_perf,
                                p_weight_report=excluded.p_weight_report,
                                p_weight_test=excluded.p_weight_test,
                                p_weight_viva=excluded.p_weight_viva,
                                p_max_raw_perf=excluded.p_max_raw_perf,
                                p_max_raw_report=excluded.p_max_raw_report,
                                p_max_raw_test=excluded.p_max_raw_test,
                                p_max_raw_viva=excluded.p_max_raw_viva
                        """, (
                            int(target_sub_id), f_theory, f_prac, w_att, w_hw, w_other, w_mid, w_final, m_raw_hw, m_raw_mid, m_raw_final, m_raw_other,
                            p_att, p_perf, p_report, p_test, p_viva, m_raw_perf, m_raw_report, m_raw_test, m_raw_viva
                        ))
                        conn.commit()
                        st.success(f"✅ Rules locked! Normalization matrix denominators synced successfully for {selected_target}!")
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
                            
                            with col_edit1:
                                new_title = st.text_input(
                                    "New Title",
                                    value=assignment['Title'],
                                    key="form_v2_title_{}".format(assignment['ID'])
                                )
                                
                                # ➕ Fetch the existing rubric from database to pre-populate the input area
                                existing_rubric_q = pd.read_sql_query("SELECT rubric FROM assignments WHERE id = ?", conn, params=(int(assignment['ID']),))
                                current_rubric_val = existing_rubric_q.iloc[0]['rubric'] if not existing_rubric_q.empty and existing_rubric_q.iloc[0]['rubric'] is not None else ""
                                
                                new_rubric = st.text_area(
                                    "New Marking Rubric / Model Answer",
                                    value=current_rubric_val,
                                    key="form_v2_rubric_{}".format(assignment['ID']),
                                    height=100
                                )
                            
                            with col_edit2:
                                current_deadline = datetime.strptime(assignment['Deadline'], '%Y-%m-%d').date()
                                new_deadline = st.date_input(
                                    "New Deadline",
                                    value=current_deadline,
                                    key="form_v2_deadline_{}".format(assignment['ID'])
                                )
                            
                            if st.button("💾 Save Changes", key="form_v2_save_{}".format(assignment['ID']), type="primary"):
                                if not new_title.strip():
                                    st.error("Title cannot be empty")
                                elif new_title == assignment['Title'] and str(new_deadline) == assignment['Deadline'] and new_rubric.strip() == current_rubric_val:
                                    st.info("No changes made")
                                else:
                                    # ✅ Cleanly providing all 4 matching arguments with safely namespaced keys
                                    success, message = update_assignment(assignment['ID'], new_title, new_deadline, new_rubric)
                                    
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
    
    # ================= SUBMISSIONS & AI (TABS[4] - FIXED VARIABLE MAPPING) =================
    with tabs[4]:
        st.subheader("📥 Centralized Submission & Assessment Desk")
        st.write("Select a specific course metric assignment below to audit, grade, or execute automated AI evaluations row-by-row.")

        # Pull available semesters to construct dynamic UI selectors
        sems = pd.read_sql_query("SELECT * FROM semesters ORDER BY name ASC", conn)

        if sems.empty:
            st.info("No active courses or semesters registered in the platform yet.")
        else:
            col1, col2, col3 = st.columns(3)
            with col1:
                # ✅ FIX: Use the existing user selections to safely map out the true operational ID
                selected_sem_name = st.selectbox("Filter by Semester", sems["name"].tolist(), key="sem_eval_filter_v4")
                active_semester_id = int(sems[sems["name"] == selected_sem_name]["id"].values[0])
            
            # 1️⃣ Core Filter Clusters linked cleanly to active_semester_id
            subjects_df = pd.read_sql_query("SELECT id, name, code FROM subjects WHERE semester_id = ?", conn, params=(int(active_semester_id),))

            if subjects_df.empty:
                st.warning("⚠️ No active subjects found for this semester. Please configure subjects in Tab 2 first.")
            else:
                with col1:
                    # Move subject picker directly into its column lane cleanly
                    subject_options = {f"{row['code']} - {row['name'].upper()}": row['id'] for _, row in subjects_df.iterrows()}
                    selected_sub_label = st.selectbox("Select Target Course", list(subject_options.keys()), key="sub_eval_filter_v4")
                    selected_sub_id = subject_options[selected_sub_label]
                
                # Dynamically pull assignments linked only to the selected subject
                asg_df = pd.read_sql_query("SELECT id, title, rubric FROM assignments WHERE subject_id = ?", conn, params=(int(selected_sub_id),))
                
                if asg_df.empty:
                    st.warning("⚠️ No assignments have been created or published for this subject track yet.")
                else:
                    with col2:
                        asg_options = {row['title']: (row['id'], row['rubric']) for _, row in asg_df.iterrows()}
                        selected_asg_title = st.selectbox("Select Assignment Module", list(asg_options.keys()), key="asg_eval_filter_v4")
                        selected_asg_id, selected_rubric = asg_options[selected_asg_title]
                    with col3:
                        status_filter = st.selectbox("Grading Lifecycle Status", ["All Submissions", "⏳ Pending Evaluation Only", "🟢 Evaluated Only"], key="status_eval_filter_v4")

                    st.divider()

                    # 2️⃣ Direct Vertical SQL Join Query for all 73 Students (Continues seamlessly below)
                    # 2️⃣ Direct Vertical SQL Join Query for all 73 Students (Aligned with submission_file and submission_time)
                query_submissions = """
                    SELECT 
                        s.id as student_id,
                        s.username as roll_no, 
                        s.full_name as student_name, 
                        s.section,
                        sub.id as submission_id,
                        sub.submission_file as file_path, 
                        sub.submission_time as submitted_at, 
                        sub.marks,
                        sub.ai_summary
                    FROM users s
                    LEFT JOIN submissions sub ON s.id = sub.student_id AND sub.assignment_id = ?
                    WHERE s.role = 'student' AND s.semester_id = ?
                    ORDER BY s.username ASC
                """
                submissions_df = pd.read_sql_query(query_submissions, conn, params=(int(selected_asg_id), int(active_semester_id)))

                # 3️⃣ Apply Pandas Status Filter constraints
                if status_filter == "⏳ Pending Evaluation Only":
                    display_df = submissions_df[submissions_df['marks'].isna() | (submissions_df['marks'] == '') | (submissions_df['marks'].astype(str).str.lower() == 'none')]
                elif status_filter == "🟢 Evaluated Only":
                    display_df = submissions_df[submissions_df['marks'].notna() & (submissions_df['marks'] != '') & (submissions_df['marks'].astype(str).str.lower() != 'none')]
                else:
                    display_df = submissions_df

                # 4️⃣ Render scannable vertical list data frame matrix
                if display_df.empty:
                    st.info("✨ No submission entries match your selected filter criteria.")
                else:
                    st.markdown(f"#### 📊 Showing **{len(display_df)}** Student Records for *{selected_asg_title}*")
                    
                    list_rows = []
                    for _, row in display_df.iterrows():
                        m_val = row['marks']
                        mark_status = f"🟢 {m_val} / 10.0" if (m_val is not None and str(m_val).strip() != "" and str(m_val).strip().lower() != "none") else "⏳ Pending"
                        
                        # ✅ FIXED PLACEMENT: Define the boolean logic BEFORE opening the list row dictionary object
                        is_valid_path = pd.notna(row['file_path']) and str(row['file_path']).strip() != "" and str(row['file_path']).strip().lower() != "none"
                        
                        list_rows.append({
                            "Roll Number": row['roll_no'],
                            "Student Name": row['student_name'].upper(),
                            "Section": f"Sec {row['section']}",
                            "Submitted Document": os.path.basename(str(row['file_path'])) if is_valid_path else "❌ No Submission",
                            "Assigned Score": mark_status,
                            "Timestamp": row['submitted_at'] if (pd.notna(row['submitted_at']) and str(row['submitted_at']).strip() != "") else "—"
                        })
                    
                    st.dataframe(pd.DataFrame(list_rows), use_container_width=True, hide_index=True)
                    

                    # ===================================================================
                    # 🚀 NEW FEATURE: BATCH AI GRADING ENGINE (ALL 73 STUDENTS AT ONCE)
                    # ===================================================================
                    st.markdown("### 🚀 Batch AI Assessment Operations")
                    st.write("Clicking the batch engine below will automatically scan through all students who have uploaded files but do not have a recorded grade yet, running a consecutive professor-rubric evaluation pass.")
                    
                    # Count un-evaluated submissions
                    pending_batch_count = len(display_df[display_df['file_path'].notna() & (display_df['file_path'] != '') & (display_df['marks'].isna() | (display_df['marks'] == ''))])
                    
                    if st.button(f"🤖 Run Batch AI Grading ({pending_batch_count} Files Pending)", key="run_batch_ai_grading_btn", type="secondary", disabled=(pending_batch_count == 0)):
                        if not selected_rubric or not str(selected_rubric).strip():
                            st.warning("⚠️ Please provide a dynamic evaluation marking rubric model answer first in Tab 3.")
                        else:
                            batch_success_count = 0
                            progress_bar = st.progress(0.0)
                            status_text = st.empty()
                            
                            # Filter down to the rows that can be evaluated automatically
                            batch_eligible_df = display_df[display_df['file_path'].notna() & (display_df['file_path'] != '') & (display_df['marks'].isna() | (display_df['marks'] == ''))]
                            
                            for idx, batch_row in enumerate(batch_eligible_df.iterrows()):
                                brow = batch_row[1]
                                status_text.text(f"Processing student file {idx+1}/{pending_batch_count}: {brow['student_name'].upper()}")
                                
                                try:
                                    result = vision_grade(brow["file_path"], selected_rubric)
                                    if result and "Error" not in str(result):
                                        extracted_m = extract_marks(result)
                                        final_score = float(extracted_m) if extracted_m is not None else 0.0
                                        
                                        # Deduct dynamic penalties for late entries inside batch loops
                                        sub_time_str = str(brow['submitted_at'])
                                        if "[LATE-10%]" in sub_time_str:
                                            final_score = final_score * 0.9
                                        elif "[LATE-50%]" in sub_time_str:
                                            final_score = final_score * 0.5
                                            
                                        cursor = conn.cursor()
                                        cursor.execute("UPDATE submissions SET marks = ?, ai_summary = ? WHERE id = ?", (round(final_score, 2), result, int(brow['submission_id'])))
                                        conn.commit()
                                        batch_success_count += 1
                                except Exception as e:
                                    pass # Skip corrupted file objects gracefully
                                    
                                progress_bar.progress((idx + 1) / pending_batch_count)
                            
                            status_text.empty()
                            progress_bar.empty()
                            st.success(f"🎉 Batch evaluation complete! Successfully graded {batch_success_count} student assignments automatically.")
                            st.rerun()

                    # ===================================================================
                    # 📝 INDIVIDUAL STUDENT WORKSPACE (RESTORED MANUAL & AI DESK)
                    # ===================================================================
                    st.markdown("---")
                    st.markdown("### 📝 Individual Quick Evaluation Workspace")
                    
                    # Create dictionary mapping for dropdown selectors
                    eligible_students = {f"{r['roll_no']} - {r['student_name'].upper()} [Sec {r['section']}]": r for _, r in display_df.iterrows()}
                    selected_student_key = st.selectbox("Select Target Student to Grade or View Feedback Logs:", list(eligible_students.keys()), key="student_eval_picker_v5")
                    
                    if selected_student_key:
                        target_row = eligible_students[selected_student_key]
                        
                        pane1, pane2 = st.columns([1, 1])
                        with pane1:
                            st.markdown(f"#### 👤 {target_row['student_name'].upper()}")
                            st.caption(f"Roll Reference: {target_row['roll_no']} | Section: {target_row['section']}")
                            
                            # ✅ FIXED: Safe type checking ensures pandas NaN float drops out cleanly before hitting os.path.exists
                            is_file_path_valid = pd.notna(target_row['file_path']) and str(target_row['file_path']).strip() != "" and str(target_row['file_path']).strip().lower() != "none"
                            
                            # Document Download Handler
                            if is_file_path_valid and os.path.exists(str(target_row['file_path'])):
                                st.success("📄 Submission file is valid and online.")
                                with open(target_row['file_path'], "rb") as f:
                                    st.download_button(
                                        "📥 Open & Download Student Answer Sheet",
                                        f,
                                        file_name=os.path.basename(target_row['file_path']),
                                        key=f"dl_vertical_btn_{target_row['student_id']}",
                                        use_container_width=True
                                    )
                            else:
                                st.error("⚠️ No uploaded PDF assignment document found for this student.")

                            st.write("")
                            st.markdown("##### ✏️ Manual Score Input / Override")
                            
                            # Match current marks cleanly to handle defaults
                            current_mark_raw = ""
                            if target_row['marks'] is not None and str(target_row['marks']).strip() != "" and str(target_row['marks']).lower() != 'none':
                                try:
                                    current_mark_raw = float(target_row['marks'])
                                except ValueError:
                                    current_mark_raw = 0.0
                                    
                            manual_marks = st.number_input(
                                "Assign Final Mark (Scale 0.0 - 10.0)",
                                min_value=0.0,
                                max_value=10.0,
                                value=float(current_mark_raw) if isinstance(current_mark_raw, float) else 0.0,
                                step=0.5,
                                key=f"v_num_mark_in_{target_row['student_id']}"
                            )
                            
                            if st.button("💾 Save Verified Grade", key=f"v_save_btn_{target_row['student_id']}", use_container_width=True, type="primary"):
                                final_score = float(manual_marks)
                                penalty_msg = ""
                                
                                # Process submission logs context to apply penalty tags dynamically if present
                                sub_time_str = str(target_row['submitted_at'])
                                if "[LATE-10%]" in sub_time_str:
                                    final_score = final_score * 0.9
                                    penalty_msg = " (-10% Late Penalty Applied)"
                                elif "[LATE-50%]" in sub_time_str:
                                    final_score = final_score * 0.5
                                    penalty_msg = " (-50% Late Penalty Applied)"
                                    
                                cursor = conn.cursor()
                                if target_row['submission_id'] is not None and pd.notna(target_row['submission_id']):
                                    cursor.execute("UPDATE submissions SET marks = ? WHERE id = ?", (round(final_score, 2), int(target_row['submission_id'])))
                                else:
                                    on_time_tag = datetime.now(NST).strftime("%Y-%m-%d %H:%M:%S")
                                    cursor.execute(
                                        "INSERT INTO submissions (assignment_id, student_id, submission_time, submission_file, marks, ai_summary) VALUES (?, ?, ?, '', ?, '')",
                                        (int(selected_asg_id), int(target_row['student_id']), on_time_tag, round(final_score, 2))
                                    )
                                conn.commit()
                                st.success(f"Successfully recorded score of {final_score:.1f}/10.0{penalty_msg} for {target_row['student_name'].upper()}!")
                                st.rerun()

                        with pane2:
                            st.markdown("##### 🤖 Single AI Co-Pilot Grading Engine")
                            
                            if st.button("🚀 Run Single AI Evaluation", key=f"v_single_ai_btn_{target_row['student_id']}", use_container_width=True, disabled=not target_row['file_path']):
                                if not selected_rubric or not str(selected_rubric).strip():
                                    st.warning("⚠️ Please fill in the assignment marking rubric answer key template inside Tab 3.")
                                else:
                                    with st.spinner("Executing LLM computer vision scoring analysis pass..."):
                                        result = vision_grade(target_row["file_path"], selected_rubric)
                                        if result and "Error" not in str(result):
                                            extracted_m = extract_marks(result)
                                            final_ai_score = float(extracted_m) if extracted_m is not None else 0.0
                                            
                                            sub_time_str = str(target_row['submitted_at'])
                                            if "[LATE-10%]" in sub_time_str:
                                                final_ai_score = final_ai_score * 0.9
                                            elif "[LATE-50%]" in sub_time_str:
                                                final_ai_score = final_ai_score * 0.5
                                                
                                            cursor = conn.cursor()
                                            cursor.execute("UPDATE submissions SET marks = ?, ai_summary = ? WHERE id = ?", (round(final_ai_score, 2), result, int(target_row['submission_id'])))
                                            conn.commit()
                                            st.success(f"AI Analysis successfully stored: {final_ai_score:.1f}/10.0")
                                            st.rerun()
                                        else:
                                            st.error(f"AI Engine Tracing Failure: {result}")
                            
                            st.write("")
                            st.markdown("##### 📜 Active Feedback Logs & Analysis Records")
                            if target_row['ai_summary'] and str(target_row['ai_summary']).strip().lower() != 'none':
                                st.info(target_row['ai_summary'])
                            else:
                                st.caption("No historical feedback notes or AI breakdown descriptions logged for this record.")
   # ANALYTICS & GRADING HUB
    with tabs[5]:
        st.title("📊 Performance & Grading Hub")
        
        # 1. THE SWITCHBOARD: Upgraded to support your SaaS prototype option
        view_mode = st.radio(
            "Select View Mode", 
            [
                "📈 Analytics Dashboard", 
                "📅 Daily Roll Call", 
                "📝 Internal Theory Ledger (40 Marks)", 
                "🧪 Practical Ledger (25 Marks)",
                
            ], 
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
        # ================= REFINED: DYNAMIC LAB GROUP ATTENDANCE PUNCHER =================
        elif view_mode == "📅 Daily Roll Call":
            st.subheader("📅 Daily Attendance Puncher")
            
            sems_att = pd.read_sql_query("SELECT * FROM semesters ORDER BY name ASC", conn)
            if sems_att.empty:
                st.warning("Please create a semester first.")
            else:
                c1, c2, c3, c4 = st.columns(4)
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
                    sel_section = st.selectbox("Select Section", ["A", "B"], key="att_section_sel")
                with c4:
                    att_type = st.radio("Session Type", ["📝 Theory Class", "🧪 Practical Lab"], horizontal=True)

                # ➕ Dynamic conditional filter option row for Lab Groups
                target_lab_group = "All"
                if att_type == "🧪 Practical Lab":
                    st.divider()
                    target_lab_group = st.selectbox(
                        "🔬 Which Lab Rotation Group is performing today?", 
                        ["Group 1", "Group 2", "Group 3", "Group 4"],
                        key="att_lab_group_filter"
                    )

                if sub_id:
                    # Construct the filtering parameters dynamically based on rotation rules
                    query_params = [sel_sem_id, sel_section]
                    group_clause = ""
                    
                    if att_type == "🧪 Practical Lab":
                        group_clause = "AND lab_group = ?"
                        query_params.append(target_lab_group)

                    # Fetch ONLY the active students scheduled for this specific lab row slot!
                    students_df = pd.read_sql_query(f"""
                        SELECT id as student_id, full_name as Name, username as Roll 
                        FROM users 
                        WHERE role='student' AND semester_id=? AND section=? {group_clause}
                        ORDER BY username ASC
                    """, conn, params=query_params)

                    if students_df.empty:
                        st.info(f"No students found registered under Section {sel_section} {f'[{target_lab_group}]' if att_type == '🧪 Practical Lab' else ''}.")
                    else:
                        header_label = f"Section {sel_section}" if att_type == "📝 Theory Class" else f"Section {sel_section} [{target_lab_group}]"
                        st.write(f"Marking attendance for **{header_label}** on: **{datetime.now(NST).strftime('%B %d, %Y')}**")
                        
                        students_df["Present"] = True  
                        
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

                        # ===================================================================
                        # 🖨️ OFFICIAL CONTINUOUS ATTENDANCE LOG COMPILER ENGINE
                        # ===================================================================
                        st.divider()
                        st.markdown("### 🖨️ Official Institutional Attendance Document Generator")
                        st.info("💡 Click the compilation button below to generate a standardized print-ready attendance log roster formatted with incremental sequence counts and recurring page titles.")

                        if st.button("📄 Compile Standardized Attendance Sheet Ledger", use_container_width=True, type="primary", key="print_attendance_ledger_btn"):
                            # SAFE STRING OVERRIDE: Matches 'Theory' or 'Practical' cleanly regardless of icons/emojis
                            session_label = "Theory" if "Theory" in att_type else "Practical"
                            
                            # Fetch historical calendar date tracking logs chronologically
                            log_data = pd.read_sql_query("""
                                SELECT u.username as [Roll No.], u.full_name as [Student Name], l.log_date, l.status
                                FROM attendance_logs l
                                JOIN users u ON l.student_id = u.id
                                WHERE l.subject_id = ? 
                                  AND l.session_type = ? 
                                  AND u.section = ?
                                ORDER BY l.log_date ASC, u.username ASC
                            """, conn, params=(sub_id, session_label, sel_section))

                            if log_data.empty:
                                st.warning("⚠️ No historical attendance tracking records discovered for this subject selection. Please log a daily roll call session first.")
                            else:
                                # Extract distinct sorted dates to construct dynamic column matrix grids
                                unique_dates = sorted(log_data['log_date'].unique())
                                students_list = pd.read_sql_query("""
                                    SELECT username as [Roll No.], full_name as [Student Name]
                                    FROM users WHERE role='student' AND semester_id=? AND section=?
                                    ORDER BY username ASC
                                """, conn, params=(sel_sem_id, sel_section))

                                
                                # ===================================================================
                                # 🖨️ RE-ALIGNED OFFICIAL ATTENDANCE SHEET REGISTER LEDGER
                                # ===================================================================
                                current_date_str = datetime.now(NST).strftime("%Y-%m-%d")
                                
                                att_html = f"""
                                <script>
                                    function downloadAttendanceExcel() {{
                                        var table = document.getElementById("attendance_master_print_table");
                                        var html = table.outerHTML;
                                        var url = 'data:application/vnd.ms-excel,' + encodeURIComponent(html);
                                        var a = document.createElement('a');
                                        a.href = url;
                                        a.download = '{sel_sub_name.replace(" ", "_")}_Attendance_Register.xls';
                                        a.click();
                                    }}
                                </script>
                                <style>
                                    @page {{
                                        size: landscape;
                                        margin: 10mm 10mm 10mm 10mm;
                                    }}
                                    @media print {{
                                        div[data-testid="stSidebar"], button, header, .stAppDeployButton, .no-print {{ display: none !important; }}
                                        body, .main .block-container {{ padding: 0 !important; margin: 0 !important; background: #fff !important; }}
                                        .repeat-header {{ display: table-header-group !important; }}
                                        .attendance-row {{ page-break-inside: avoid !important; break-inside: avoid !important; }}
                                    }}
                                    .download-btn {{
                                        background-color: #10B981; color: white; padding: 8px 16px; 
                                        border: none; border-radius: 4px; font-weight: bold; cursor: pointer;
                                        font-size: 12px; margin-bottom: 15px; float: right; font-family: Arial, sans-serif;
                                    }}
                                    .print-table {{
                                        width: 100%; border-collapse: collapse; font-family: Arial, sans-serif; color: #111111;
                                        margin: 0 auto;
                                    }}
                                    .print-table th, .print-table td {{
                                        border: 1px solid #000000 !important; padding: 6px 4px; text-align: center; font-size: 11px;
                                    }}
                                    .text-left {{ text-align: left !important; }}
                                    .absent-text {{ color: #dc2626 !important; font-weight: bold; background-color: #ffe4e6 !important; }}
                                    
                                    /* 🎨 MASTER METADATA SUB-TABLE GRID RE-ALIGNMENT */
                                    .meta-info-table {{
                                        width: 100%;
                                        border-collapse: collapse !important;
                                        margin-top: 5px;
                                    }}
                                    .meta-info-table td {{
                                        border: none !important; 
                                        padding: 3px 0px !important; /* Zero padding pulls metadata completely left to mirror column margins */
                                        font-size: 12px !important;
                                        font-weight: bold !important;
                                        text-align: left !important;
                                        line-height: 1.5;
                                        color: #111111 !important;
                                    }}
                                </style>
                                
                                <div style="background-color: #ffffff; padding: 5px; color: #111111;">
                                    <button class="download-btn no-print" onclick="downloadAttendanceExcel()">📥 Download Excel Spreadsheet</button>
                                    <button class="download-btn no-print" style="background-color: #3b82f6; margin-right: 10px;" onclick="window.print()">🖨️ Print / Save PDF</button>
                                    <div style="clear: both;"></div>

                                    <table class="print-table" id="attendance_master_print_table">
                                        <thead class="repeat-header">
                                            <tr>
                                                <th colspan="{len(unique_dates) + 5}" style="background-color: #ffffff; border: none !important; padding-bottom: 12px;">
                                                    <div style="text-align: center; font-weight: bold; line-height: 1.3; margin-bottom: 10px;">
                                                        <div style="font-size: 16px; text-transform: uppercase; letter-spacing: 0.5px;">{st.session_state.g_univ}</div>
                                                        <div style="font-size: 13px;">{st.session_state.g_inst_body}</div>
                                                        <div style="font-size: 14px; font-weight: bold;">{st.session_state.g_college}</div>
                                                        <div style="font-size: 13px; font-weight: bold; margin-top: 3px; color: #222;">Student Attendance Sheet Register</div>
                                                    </div>
                                                    
                                                    <table class="meta-info-table">
                                                        <tr>
                                                            <td style="width: 38.5%;">Subject: {sel_sub_name.upper()}</td>
                                                            <td style="width: 33.5%;">Department/Batch: {st.session_state.g_dept} | Batch: {st.session_state.g_batch}</td>
                                                            <td style="width: 28%; text-align: right !important;">Section: {sel_section}</td>
                                                        </tr>
                                                        <tr>
                                                            <td>Subject Teacher: {st.session_state.g_teacher}</td>
                                                            <td>Year/Part: {st.session_state.g_yp}</td>
                                                            <td style="text-align: right !important;">Nature: {session_label} Session</td>
                                                        </tr>
                                                    </table>
                                                </th>
                                            </tr>
                                            <tr style="background-color: #fafafa; font-weight: bold;">
                                                <th style="width: 4%;">S.N.</th>
                                                <th style="width: 14%;">CRN</th>
                                                <th style="text-align: left; padding-left: 8px; width: 26%;">Student Name</th>
                                """
                                for d in unique_dates:
                                    formatted_month_day = d[5:].replace("-", "/")
                                    att_html += f'<th style="font-size: 9px; padding: 4px 2px; width: 3.5%;">{formatted_month_day}</th>'
                                    
                                att_html += """
                                                <th style="width: 8%;">Total Attd.</th>
                                                <th style="width: 8%;">Score %</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                """
                                
                                # Compute student timeline arrays using sequence counters (1, 2, 3...)
                                for s_idx, s_row in students_list.iterrows():
                                    roll_no = s_row['Roll No.']
                                    s_name = s_row['Student Name']
                                    
                                    att_html += f"""
                                            <tr class="attendance-row">
                                                <td>{s_idx + 1}</td>
                                                <td style="font-family: monospace;">{roll_no}</td>
                                                <td class="text-left" style="font-weight: bold; padding-left: 8px;">{s_name.upper()}</td>
                                    """
                                    
                                    presence_counter = 0
                                    total_logged_days = len(unique_dates)
                                    
                                    for d in unique_dates:
                                        match_state = log_data[(log_data['Roll No.'] == roll_no) & (log_data['log_date'] == d)]
                                        
                                        if match_state.empty:
                                            att_html += '<td>-</td>'
                                        else:
                                            status = match_state.iloc[0]['status']
                                            if status == "Present":
                                                presence_counter += 1
                                                att_html += f'<td>{presence_counter}</td>'
                                            else:
                                                att_html += '<td class="absent-text">A</td>'
                                                
                                    pct_calc = (presence_counter / total_logged_days * 100) if total_logged_days > 0 else 0.0
                                    
                                    att_html += f"""
                                                <td style="font-weight: bold; background-color: #fafafa;">{presence_counter} / {total_logged_days}</td>
                                                <td style="font-weight: bold; background-color: #fafafa;">{pct_calc:.1f}%</td>
                                            </tr>
                                    """
                                    
                                att_html += f"""
                                        </tbody>
                                    </table>
                                    
                                    <table style="width: 100%; margin-top: 40px; font-size: 11px; font-weight: bold; font-family: Arial, sans-serif; border-collapse: collapse;">
                                        <tr>
                                            <td style="width: 50%; text-align: left; border: none !important; padding: 0px;">
                                                This Attendance sheet must be submitted to department.<br><br>
                                                Issued Date: {current_date_str}
                                            </td>
                                            <td style="width: 50%; text-align: right; border: none !important; padding: 0px; vertical-align: bottom;">
                                                ...........................................................<br>
                                                Certified Subject Teacher Signature
                                            </td>
                                        </tr>
                                    </table>
                                </div>
                                """
                                
                                import streamlit.components.v1 as components
                                calc_height = 450 + (len(students_list) * 38)
                                components.html(att_html, height=max(calc_height, 700), scrolling=True)

                        st.write("") # Spacer
                        st.write("") # Spacer
                        
                        # Freedom to pick any date (Defaults to today, but lets you backdate easily)
                        chosen_date = st.date_input(
                            "📅 Select Class/Lab Date for this Roll Call:", 
                            value=datetime.now(NST).date(),
                            key="attendance_calendar_picker"
                        )
                        
                        target_date_str = chosen_date.strftime("%Y-%m-%d")

                        if st.button(f"🚀 Submit & Log Attendance for {target_date_str}", use_container_width=True, type="primary"):
                            
                                
                            # ===================================================================
                            # 🛡️ CRITICAL RUNTIME FIX: DEFINED EXPLICITLY INSIDE THE EXECUTION PATH
                            # ===================================================================
                            session_label = "Theory" if att_type == "📝 Theory Class" else "Practical"
                            
                            for _, r in edited_att_df.iterrows():
                                s_id = int(r['student_id'])
                                
                                val_present = r['Present']
                                if isinstance(val_present, bytes):
                                    is_present = 1 if b'\x01' in val_present else 0
                                else:
                                    is_present = 1 if bool(val_present) else 0
                                    
                                status_str = "Present" if is_present else "Absent"
                                
                                # A. Write entry into logs
                                c.execute("""
                                    INSERT INTO attendance_logs (student_id, subject_id, log_date, session_type, status)
                                    VALUES (?, ?, ?, ?, ?)
                                    ON CONFLICT(student_id, subject_id, log_date, session_type) 
                                    DO UPDATE SET status = excluded.status
                                """, (s_id, sub_id, target_date_str, session_label, status_str))
                                
                                # B. Calculate aggregate sum totals to feed the grading ledger perfectly
                                if session_label == "Theory":
                                    p_count = c.execute("SELECT COUNT(*) FROM attendance_logs WHERE student_id=? AND subject_id=? AND session_type='Theory' AND status='Present'", (s_id, sub_id)).fetchone()[0]
                                    t_count = c.execute("SELECT COUNT(*) FROM attendance_logs WHERE student_id=? AND subject_id=? AND session_type='Theory'", (s_id, sub_id)).fetchone()[0]
                                    
                                    c.execute("""
                                        INSERT INTO student_marks (student_id, subject_id, t_att_present, t_att_total)
                                        VALUES (?, ?, ?, ?)
                                        ON CONFLICT(student_id, subject_id) DO UPDATE SET
                                            t_att_present = excluded.t_att_present,
                                            t_att_total = excluded.t_att_total
                                    """, (s_id, sub_id, p_count, t_count))
                                else: # Practical
                                    p_count = c.execute("SELECT COUNT(*) FROM attendance_logs WHERE student_id=? AND subject_id=? AND session_type='Practical' AND status='Present'", (s_id, sub_id)).fetchone()[0]
                                    t_count = c.execute("SELECT COUNT(*) FROM attendance_logs WHERE student_id=? AND subject_id=? AND session_type='Practical'", (s_id, sub_id)).fetchone()[0]
                                    
                                    c.execute("""
                                        INSERT INTO student_marks (student_id, subject_id, p_att_present, p_att_total)
                                        VALUES (?, ?, ?, ?)
                                        ON CONFLICT(student_id, subject_id) DO UPDATE SET
                                            p_att_present = excluded.p_att_present,
                                            p_att_total = excluded.p_att_total
                                    """, (s_id, sub_id, p_count, t_count))
                                    
                            conn.commit()
                            st.success(f"✅ Attendance for {target_date_str} logged! Cumulative grading metrics recalculated successfully.")
                            st.balloons()
                            st.rerun()
                            st.write("")
                        if st.button(f"🗑️ Clear & Reset All Logs for {target_date_str}", use_container_width=True, type="secondary", key="clear_accidental_day_btn"):
                            # 28 spaces (7 tabs) at the front of ALL these lines
                            session_label = "Theory" if "Theory" in att_type else "Practical"
                            
                            # 1. Fetch targeted student IDs for the active section cleanly
                            target_students = pd.read_sql_query(
                                "SELECT id FROM users WHERE role='student' AND section=?", 
                                conn, params=(sel_section,)
                            )
                            
                            if not target_students.empty:
                                student_ids = target_students['id'].tolist()
                                placeholders = ",".join("?" for _ in student_ids)
                                
                                # 2. Purge only the logs for this specific day, section, and subject
                                c.execute(f"DELETE FROM attendance_logs WHERE subject_id = ? AND session_type = ? AND log_date = ? AND student_id IN ({placeholders})", [sub_id, session_label, target_date_str] + student_ids)
                                
                                # 3. Dynamic Re-tally Engine Loop: Fix summary totals for the marks ledger
                                for s_id in student_ids:
                                    if session_label == "Theory":
                                        p_count = c.execute("SELECT COUNT(*) FROM attendance_logs WHERE student_id=? AND subject_id=? AND session_type='Theory' AND status='Present'", (s_id, sub_id)).fetchone()[0]
                                        t_count = c.execute("SELECT COUNT(*) FROM attendance_logs WHERE student_id=? AND subject_id=? AND session_type='Theory'", (s_id, sub_id)).fetchone()[0]
                                        
                                        c.execute("""
                                            INSERT INTO student_marks (student_id, subject_id, t_att_present, t_att_total)
                                            VALUES (?, ?, ?, ?)
                                            ON CONFLICT(student_id, subject_id) DO UPDATE SET
                                                t_att_present = excluded.t_att_present,
                                                t_att_total = excluded.t_att_total
                                        """, (s_id, sub_id, p_count, t_count))
                                    else:
                                        p_count = c.execute("SELECT COUNT(*) FROM attendance_logs WHERE student_id=? AND subject_id=? AND session_type='Practical' AND status='Present'", (s_id, sub_id)).fetchone()[0]
                                        t_count = c.execute("SELECT COUNT(*) FROM attendance_logs WHERE student_id=? AND subject_id=? AND session_type='Practical'", (s_id, sub_id)).fetchone()[0]
                                        
                                        c.execute("""
                                            INSERT INTO student_marks (student_id, subject_id, p_att_present, p_att_total)
                                            VALUES (?, ?, ?, ?)
                                            ON CONFLICT(student_id, subject_id) DO UPDATE SET
                                                p_att_present = excluded.p_att_present,
                                                p_att_total = excluded.p_att_total
                                        """, (s_id, sub_id, p_count, t_count))
                                
                                conn.commit()
                                st.success(f"💥 Cleaned up! All logs for {target_date_str} (Section {sel_section}) have been erased, and marks are fixed.")
                                time.sleep(1.2)
                                st.rerun()
                            else:
                                st.error("❌ No students found in this active section to clear.")
                        
                        # ===================================================================
       # ================= Free-Standing Full Width Theory Ledger =================
        elif view_mode == "📝 Internal Theory Ledger (40 Marks)":
            st.markdown("## 📝 Internal Theory Assessment Ledger (40 Marks)")
            
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
                        sel_sub_id = None
                    else:
                        sel_sub_name = st.selectbox("Subject", subjects_grading["name"], key="grad_sub_sel_t")
                        sel_sub_id = int(subjects_grading[subjects_grading["name"] == sel_sub_name]["id"].values[0])

                if sel_sub_id:
                    st.divider()
                    st.markdown("### 📊 Step 1: Input Raw Continuous Scores")
                    
                    # 🛡️ Safe Extraction of Teacher's Custom Max Denominators
                    active_cfg = pd.read_sql_query("SELECT * FROM subject_schemes WHERE subject_id = ?", conn, params=(int(sel_sub_id),))
                    cfg_max_hw = float(active_cfg.iloc[0]['t_max_raw_hw']) if (not active_cfg.empty and 't_max_raw_hw' in active_cfg.columns and pd.notna(active_cfg.iloc[0]['t_max_raw_hw'])) else 50.0
                    cfg_max_mid = float(active_cfg.iloc[0]['t_max_raw_mid']) if (not active_cfg.empty and 't_max_raw_mid' in active_cfg.columns and pd.notna(active_cfg.iloc[0]['t_max_raw_mid'])) else 40.0
                    cfg_max_final = float(active_cfg.iloc[0]['t_max_raw_final']) if (not active_cfg.empty and 't_max_raw_final' in active_cfg.columns and pd.notna(active_cfg.iloc[0]['t_max_raw_final'])) else 40.0
                    cfg_max_other = float(active_cfg.iloc[0]['t_max_raw_other']) if (not active_cfg.empty and 't_max_raw_other' in active_cfg.columns and pd.notna(active_cfg.iloc[0]['t_max_raw_other'])) else 100.0

                    query = """
                        SELECT u.id as student_id, u.username as Roll, u.full_name as Name,
                        IFNULL(m.t_att_present, 0) as t_att_present,
                        IFNULL(m.t_att_total, 34) as t_att_total,
                        IFNULL(m.t_hw_raw, 0.0) as t_hw_raw,
                        IFNULL(m.t_mid_raw, 0.0) as t_mid_raw,
                        IFNULL(m.t_final_raw, 0.0) as t_final_raw,
                        IFNULL(m.t_other_raw, 0.0) as t_other_raw,
                        IFNULL(m.t_grace, 0.0) as t_grace
                        FROM users u LEFT JOIN student_marks m ON u.id = m.student_id AND m.subject_id = ?
                        WHERE u.role = 'student' AND u.semester_id = ?
                        ORDER BY u.username ASC
                    """
                    df_t = pd.read_sql_query(query, conn, params=(sel_sub_id, sel_sem_id))
                    
                    edited_t = st.data_editor(
                        df_t, 
                        column_config={
                            "student_id": None, 
                            "Roll": st.column_config.TextColumn("Roll No.", disabled=True),
                            "Name": st.column_config.TextColumn("Student Name", disabled=True),
                            "t_att_present": st.column_config.NumberColumn("Attended", min_value=0, step=1),
                            "t_att_total": st.column_config.NumberColumn("Total Classes", min_value=1, step=1),
                            "t_hw_raw": st.column_config.NumberColumn(f"Assignments (Max {cfg_max_hw:.0f})", min_value=0.0, max_value=cfg_max_hw, step=0.5),
                            "t_mid_raw": st.column_config.NumberColumn(f"Mid-Term (Max {cfg_max_mid:.0f})", min_value=0.0, max_value=cfg_max_mid, step=0.5),
                            "t_final_raw": st.column_config.NumberColumn(f"Final Term (Max {cfg_max_final:.0f})", min_value=0.0, max_value=cfg_max_final, step=0.5),
                            "t_other_raw": st.column_config.NumberColumn(f"Tutorials/Other (Max {cfg_max_other:.0f})", min_value=0.0, max_value=cfg_max_other, step=1.0),
                            "t_grace": st.column_config.NumberColumn("Grace (Max 5)", min_value=0.0, max_value=5.0, step=0.5)
                        }, 
                        use_container_width=True, 
                        hide_index=True, 
                        key="theory_editor_v6_force"
                    )

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
                                int(r['student_id']), int(sel_sub_id),
                                int(r['t_att_present']), int(r['t_att_total']),
                                float(r['t_hw_raw']), float(r['t_mid_raw']),
                                float(r['t_final_raw']), float(r['t_other_raw']), float(r['t_grace'])
                            ))
                        conn.commit()
                        st.success("✅ Theory raw marks successfully synchronized and recalculated.")
                        st.rerun()

                    # 🌟 THE RESTORED PROCESSED THEORY TOTALS MATRIX VIEW
                    st.write("")
                    st.divider()
                    st.subheader("🎯 Step 2: Processed Theory Totals (Out of 40)")
                    
                    res_t = []
                    for _, r in edited_t.iterrows():
                        s_meta = r.to_dict()
                        
                        # 🧠 1. Fetch live accumulated assignment scores from submissions for this specific student
                        q_stud_marks_hub = """
                        SELECT NULLIF(marks, '') as marks FROM submissions 
                        WHERE assignment_id IN (SELECT id FROM assignments WHERE subject_id = ?) AND student_id = ?
                        """
                        m_df_hub = pd.read_sql_query(q_stud_marks_hub, conn, params=(int(sel_sub_id), int(s_meta['student_id'])))
                        live_cum_earned_hub = 0.0
                        if not m_df_hub.empty:
                            for _, m_row_hub in m_df_hub.iterrows():
                                if m_row_hub['marks'] is not None and str(m_row_hub['marks']).strip() != "":
                                    try: 
                                        live_cum_earned_hub += float(m_row_hub['marks'])
                                    except ValueError: 
                                        pass

                        # 📦 2. Pull denominators cleanly from schema, using your advanced configuration parameters
                        cfg_max_hw = float(active_cfg.iloc[0]['t_max_raw_hw']) if (not active_cfg.empty and 't_max_raw_hw' in active_cfg.columns and pd.notna(active_cfg.iloc[0]['t_max_raw_hw'])) else 50.0
                        cfg_max_mid = float(active_cfg.iloc[0]['t_max_raw_mid']) if (not active_cfg.empty and 't_max_raw_mid' in active_cfg.columns and pd.notna(active_cfg.iloc[0]['t_max_raw_mid'])) else 40.0
                        cfg_max_final = float(active_cfg.iloc[0]['t_max_raw_final']) if (not active_cfg.empty and 't_max_raw_final' in active_cfg.columns and pd.notna(active_cfg.iloc[0]['t_max_raw_final'])) else 40.0
                        cfg_max_other = float(active_cfg.iloc[0]['t_max_raw_other']) if (not active_cfg.empty and 't_max_raw_other' in active_cfg.columns and pd.notna(active_cfg.iloc[0]['t_max_raw_other'])) else 100.0

                        # 🧮 3. Pure Explicit Normalization Calculations
                        r_att = (s_meta['t_att_present'] / s_meta['t_att_total']) * 4.0 if s_meta['t_att_total'] > 0 else 0.0
                        
                        # Use your precise assignment conversion rule directly in the view loop
                        r_hw = (live_cum_earned_hub / cfg_max_hw) * 10.0
                        
                        r_mid = (s_meta['t_mid_raw'] / cfg_max_mid) * 10.0 if cfg_max_mid > 0 else 0.0
                        r_final = (s_meta['t_final_raw'] / cfg_max_final) * 10.0 if cfg_max_final > 0 else 0.0
                        r_ot = (s_meta['t_other_raw'] / cfg_max_other) * 6.0 if cfg_max_other > 0 else 0.0

                        # Sum up all assessment weight heads out of exactly 40 marks max
                        t_score_calc = r_att + r_hw + r_mid + r_final + r_ot
                        
                        # Add structural grace points securely if thresholds match
                        t_pct_val = (s_meta['t_att_present'] / s_meta['t_att_total'] * 100) if s_meta['t_att_total'] > 0 else 0.0
                        is_elig = t_pct_val >= 70.0
                        
                        if is_elig and s_meta['t_grace'] > 0:
                            t_score_calc += min(s_meta['t_grace'], 5.0)

                        t_standing = "✅ Eligible" if (is_elig and t_score_calc >= 16.0) else "❌ NQ"

                        res_t.append({
                            "Roll No.": s_meta['Roll'],
                            "Student Name": s_meta['Name'].upper(),
                            "Total Score (/40)": f"{t_score_calc:.2f}",
                            "Theory Exam Standing": t_standing
                        })
                    
                    st.dataframe(pd.DataFrame(res_t), use_container_width=True, hide_index=True,key="theory_totals_preview_v6")
               # === REMOVED CLUTTERING LOCAL INPUT FIELDS - READS FROM REGISTRY ===
                    st.write("")
                    st.markdown("### 🖨️ Official Institutional Document Generator")
                    st.info("💡 The print engine is fully connected. The ledger header below automatically uses the credentials set in your Global Registry panel at the top.")
                    
                    # Date picking manual entry
                    ledger_date = st.date_input("Ledger Issue Date:", value=None, key="theory_ledger_date")

                    if st.button("📄 Compile Standardized Theory Ledger Roster", use_container_width=True, type="primary", key="print_theory_ledger_btn"):
                        sub_details = pd.read_sql_query("SELECT name FROM subjects WHERE id = ?", conn, params=(int(sel_sub_id),))
                        s_name = sub_details.iloc[0]['name'] if not sub_details.empty else "Selected Subject"
                        formatted_date = ledger_date.strftime("%Y-%m-%d") if ledger_date else "............................."
                        
                        t_html = f"""
                        <script>
                            function downloadExcel() {{
                                var table = document.getElementById("theory_ledger_table");
                                var html = table.outerHTML;
                                var url = 'data:application/vnd.ms-excel,' + encodeURIComponent(html);
                                var a = document.createElement('a');
                                a.href = url;
                                a.download = '{s_name.replace(" ", "_")}_Theory_Ledger.xls';
                                a.click();
                            }}
                        </script>
                        <style>
                            @page {{ 
                                size: landscape; 
                                margin: 10mm 10mm 10mm 10mm; 
                            }}
                            @media print {{
                                div[data-testid="stSidebar"], button, header, .stAppDeployButton, .no-print {{ display: none !important; }}
                                body, .main .block-container {{ padding: 0 !important; margin: 0 !important; background: #fff !important; }}
                                .repeat-header {{ display: table-header-group !important; }}
                                .ledger-row {{ page-break-inside: avoid !important; break-inside: avoid !important; }}
                            }}
                            .download-btn {{
                                background-color: #10B981; color: white; padding: 8px 16px; 
                                border: none; border-radius: 4px; font-weight: bold; cursor: pointer;
                                font-size: 12px; margin-bottom: 15px; float: right; font-family: Arial, sans-serif;
                            }}
                            .print-table {{
                                width: 100%; border-collapse: collapse; font-family: Arial, sans-serif; color: #111111;
                                margin: 0 auto;
                            }}
                            .print-table th, .print-table td {{
                                border: 1px solid #000000 !important; padding: 6px 4px; text-align: center; font-size: 11px;
                            }}
                            .text-left {{ text-align: left !important; }}
                            .nq-text {{ color: #dc2626 !important; font-weight: bold; background-color: #fee2e2 !important; }}
                            
                            /* 🎨 REFINED SYSTEM SCHEME CLASSES */
                            .meta-info-table {{
                                width: 100%;
                                border-collapse: collapse !important;
                                margin-top: 5px;
                            }}
                            .meta-info-table td {{
                                border: none !important; /* Strips ugly outer line contamination */
                                padding: 3px 0px !important;
                                font-size: 12px !important;
                                text-align: left !important;
                            }}
                            .breakdown-box-table {{
                                width: 100%;
                                border-collapse: collapse !important;
                                background-color: #ffffff;
                            }}
                            .breakdown-box-table th {{
                                background-color: #fafafa !important;
                                color: #000000 !important;
                                border: 1px solid #000000 !important;
                                font-size: 11px !important;
                                padding: 5px !important;
                                font-weight: bold !important;
                                text-transform: uppercase;
                            }}
                            .breakdown-box-table td {{
                                border: 1px solid #000000 !important;
                                font-size: 10px !important;
                                padding: 3px 8px !important;
                                text-align: left !important; /* Force identical uniform starting point line */
                            }}
                            .breakdown-label {{
                                display: inline-block;
                                width: 110px;
                                font-weight: 500;
                            }}
                        </style>
                        
                        <div style="background-color: #ffffff; padding: 5px; color: #111111;">
                            <button class="download-btn no-print" onclick="downloadExcel()">📥 Download Excel Spreadsheet</button>
                            <button class="download-btn no-print" style="background-color: #3b82f6; margin-right: 10px;" onclick="window.print()">🖨️ Print / Save PDF</button>
                            <div style="clear: both;"></div>

                            <table class="print-table" id="theory_ledger_table">
                                <thead class="repeat-header">
                                    <tr>
                                        <th colspan="10" style="background-color: #ffffff; border: none !important; padding-bottom: 8px;">
                                            <div style="text-align: center; font-weight: bold; line-height: 1.3; margin-bottom: 10px;">
                                                <div style="font-size: 16px; text-transform: uppercase; letter-spacing: 0.5px;">{st.session_state.g_univ}</div>
                                                <div style="font-size: 13px;">{st.session_state.g_inst_body}</div>
                                                <div style="font-size: 14px; font-weight: bold;">{st.session_state.g_college}</div>
                                                <div style="font-size: 12px; margin-top: 4px; padding-bottom: 2px; font-weight: bold; color: #222;">
                                                    {st.session_state.g_exam_title}
                                                </div>
                                            </div>
                                            
                                            <table class="meta-info-table">
                                                <tr>
                                                    <td style="width: 38.5%;"><b>Batch:</b> {st.session_state.g_batch}</td>
                                                    <td style="width: 33.5%;"><b>Level:</b> Bachelor</td>
                                                    <td style="width: 28%; padding: 0 !important; vertical-align: top;" rowspan="5">
                                                        <table class="breakdown-box-table">
                                                            <thead>
                                                                <tr>
                                                                    <th colspan="2">Marks Breakdown</th>
                                                                </tr>
                                                            </thead>
                                                            <tbody>
                                                                <tr><td><span class="breakdown-label">Attendance</span>: 10%</td></tr>
                                                                <tr><td><span class="breakdown-label">Assignments</span>: 25%</td></tr>
                                                                <tr><td><span class="breakdown-label">Mid-Term Exam</span>: 25%</td></tr>
                                                                <tr><td><span class="breakdown-label">Final Internal</span>: 25%</td></tr>
                                                                <tr><td><span class="breakdown-label">Tutorials</span>: 15%</td></tr>
                                                            </tbody>
                                                        </table>
                                                    </td>
                                                </tr>
                                                <tr>
                                                    <td><b>Year/Part:</b> {st.session_state.g_yp}</td>
                                                    <td><b>Programme:</b> {st.session_state.g_prog}</td>
                                                </tr>
                                                <tr>
                                                    <td><b>Subject Name:</b> {s_name.upper()}</td>
                                                    <td><b>Evaluation:</b> Theory Ledger Matrix</td>
                                                </tr>
                                                <tr>
                                                    <td><b>Subject Code No:</b> {st.session_state.g_sub_code}</td>
                                                    <td><b>Full Marks:</b> 40</td>
                                                </tr>
                                                <tr>
                                                    <td><b>Department:</b> {st.session_state.g_dept}</td>
                                                    <td><b>Pass Marks:</b> 16</td>
                                                </tr>
                                            </table>
                                        </th>
                                    </tr>
                                    <tr style="background-color: #fafafa; font-weight: bold;">
                                        <th style="width: 4%;">S.N.</th>
                                        <th style="text-align: left; padding-left: 8px; width: 26%;">Student Name</th>
                                        <th style="width: 14%;">CRN</th>
                                        <th style="width: 7%;">Att.</th>
                                        <th style="width: 7%;">Asse.</th>
                                        <th style="width: 7%;">Mid-Term</th>
                                        <th style="width: 7%;">Final-Term</th>
                                        <th style="width: 7%;">Tut</th>
                                        <th style="width: 7%;">In Figures</th>
                                        <th style="width: 14%;">In Words</th>
                                    </tr>
                                </thead>
                                <tbody>
                        """
                        
                        # ===================================================================
                        # 🖨️ STRICT CUMULATIVE INCREMENTAL LEDGER GENERATOR LOOP
                        # ===================================================================
                        for idx, row in edited_t.iterrows():
                            s_meta = row.to_dict()
                            c_tot, is_elig = calculate_internal_theory(s_meta, sel_sub_id, conn)
                            word_tot = score_to_words(c_tot) if is_elig else "RETAINED"
                            fig_out = f"{c_tot:.0f}" if is_elig else "NQ"
                            
                            # 🧠 1. Fetch all submission marks earned by this student for this subject
                            q_stud_marks = """
                            SELECT NULLIF(marks, '') as marks FROM submissions 
                            WHERE assignment_id IN (SELECT id FROM assignments WHERE subject_id = ?) AND student_id = ?
                            """
                            m_df = pd.read_sql_query(q_stud_marks, conn, params=(int(sel_sub_id), int(s_meta['student_id'])))
                            live_cum_earned = 0.0
                            if not m_df.empty:
                                for _, m_row in m_df.iterrows():
                                    if m_row['marks'] is not None and str(m_row['marks']).strip() != "":
                                        try: 
                                            live_cum_earned += float(m_row['marks'])
                                        except ValueError: 
                                            pass

                            # 🧠 2. Process attendance scoring out of 4.0 marks max
                            r_att = (s_meta['t_att_present'] / s_meta['t_att_total']) * 4.0 if s_meta['t_att_total'] > 0 else 0.0
                            
                            # 🧠 3. CRITICAL CALIBRATION: Calculate incremental marks out of a fixed 50 baseline
                            # Math: (Live Earned Sum / 50.0 Max Raw) * 10.0 Max Assignment Ledger Weight
                            r_hw = (live_cum_earned / 50.0) * 10.0
                            
                            # 🧠 4. Calculate exams and remaining continuous assessments
                            r_mid = (s_meta['t_mid_raw'] / cfg_max_mid) * 10.0
                            r_final = (s_meta['t_final_raw'] / cfg_max_final) * 10.0
                            r_ot = (s_meta['t_other_raw'] / cfg_max_other) * 6.0

                            row_class = 'class="nq-text"' if not is_elig else ''

                            t_html += f'''
                                    <tr class="ledger-row">
                                        <td>{idx + 1}</td>
                                        <td class="text-left" style="font-weight: bold; padding-left: 8px;">{s_meta['Name'].upper()}</td>
                                        <td style="font-family: monospace;">{s_meta['Roll']}</td>
                                        <td>{r_att:.1f}</td>
                                        <td>{r_hw:.1f}</td>
                                        <td>{r_mid:.1f}</td>
                                        <td>{r_final:.1f}</td>
                                        <td>{r_ot:.1f}</td>
                                        <td {row_class}>{fig_out}</td>
                                        <td class="text-left" style="font-size: 10px; font-weight: bold;" {row_class}>{word_tot}</td>
                                    </tr>
                            '''
                            
                        t_html += f"""
                                    </tbody>
                                </table>

                                <table style="width: 100%; margin-top: 40px; font-size: 11px; line-height: 1.8; font-family: Arial, sans-serif; font-weight: bold;">
                                    <tr>
                                        <td style="width: 35%; vertical-align: top;"><strong>Date:</strong> {formatted_date}</td>
                                        <td style="width: 35%; vertical-align: top;">
                                            <strong>Name of Examiner:</strong> {st.session_state.g_teacher}<br>
                                            <strong>Name of HoD:</strong> {st.session_state.g_hod}
                                        </td>
                                        <td style="width: 30%; vertical-align: top; text-align: right;">
                                            <strong>Signature:</strong> ........................................<br>
                                            <strong>Signature:</strong> ........................................
                                        </td>
                                    </tr>
                                    <tr>
                                        <td style="padding-top: 15px; font-weight: bold;" colspan="2">Note: Absentees-A And Failed Marks must be incircled in red.</td>
                                        <td style="padding-top: 15px; font-weight: bold; text-align: right;">Received Date (Exam Section) : .................</td>
                                    </tr>
                                </table>
                            </div>
                        </div>
                        """
                        import streamlit.components.v1 as components
                        calc_height = 500 + (len(edited_t) * 45)
                        components.html(t_html, height=max(calc_height, 700), scrolling=True)
        # ================= Free-Standing Full Width Practical Ledger =================
        elif view_mode == "🧪 Practical Ledger (25 Marks)":
            st.markdown("## 🧪 Practical Assessment Ledger (25 Marks)")
            
            sems_grading_p = pd.read_sql_query("SELECT * FROM semesters ORDER BY name ASC", conn)
            if sems_grading_p.empty:
                st.warning("Please create a semester first.")
            else:
                col_sel_p1, col_sel_p2 = st.columns(2)
                with col_sel_p1:
                    sel_sem_name_p = st.selectbox("Semester", sems_grading_p["name"], key="grad_sem_sel_p")
                    sel_sem_id_p = int(sems_grading_p[sems_grading_p["name"] == sel_sem_name_p]["id"].values[0])
                with col_sel_p2:
                    subjects_grading_p = pd.read_sql_query("SELECT * FROM subjects WHERE semester_id=?", conn, params=(sel_sem_id_p,))
                    if subjects_grading_p.empty:
                        st.error("No subjects found.")
                        sel_sub_id_p = None
                    else:
                        sel_sub_name_p = st.selectbox("Subject", subjects_grading_p["name"], key="grad_sub_sel_p")
                        sel_sub_id_p = int(subjects_grading_p[subjects_grading_p["name"] == sel_sub_name_p]["id"].values[0])

                if sel_sub_id_p:
                    st.divider()
                    st.markdown("### 📊 Step 1: Input Raw Practical & Lab Scores")
                    
                    # 🛡️ Safe Extraction of Teacher's Custom Max Practical Denominators
                    active_lab_cfg = pd.read_sql_query("SELECT * FROM subject_schemes WHERE subject_id = ?", conn, params=(int(sel_sub_id_p),))
                    cfg_max_perf = float(active_lab_cfg.iloc[0]['p_max_raw_perf']) if (not active_lab_cfg.empty and 'p_max_raw_perf' in active_lab_cfg.columns and pd.notna(active_lab_cfg.iloc[0]['p_max_raw_perf'])) else 100.0
                    cfg_max_report = float(active_lab_cfg.iloc[0]['p_max_raw_report']) if (not active_lab_cfg.empty and 'p_max_raw_report' in active_lab_cfg.columns and pd.notna(active_lab_cfg.iloc[0]['p_max_raw_report'])) else 100.0
                    cfg_max_test = float(active_lab_cfg.iloc[0]['p_max_raw_test']) if (not active_lab_cfg.empty and 'p_max_raw_test' in active_lab_cfg.columns and pd.notna(active_lab_cfg.iloc[0]['p_max_raw_test'])) else 100.0
                    cfg_max_viva = float(active_lab_cfg.iloc[0]['p_max_raw_viva']) if (not active_lab_cfg.empty and 'p_max_raw_viva' in active_lab_cfg.columns and pd.notna(active_lab_cfg.iloc[0]['p_max_raw_viva'])) else 100.0

                    query_p = """
                        SELECT u.id as student_id, u.username as Roll, u.full_name as Name,
                        IFNULL(m.p_att_present, 0) as p_att_present,
                        IFNULL(m.p_att_total, 12) as p_att_total,
                        IFNULL(m.p_perf_raw, 0.0) as p_perf_raw,
                        IFNULL(m.p_report_raw, 0.0) as p_report_raw,
                        IFNULL(m.p_test_raw, 0.0) as p_test_raw,
                        IFNULL(m.p_viva_raw, 0.0) as p_viva_raw
                        FROM users u LEFT JOIN student_marks m ON u.id = m.student_id AND m.subject_id = ?
                        WHERE u.role = 'student' AND u.semester_id = ?
                        ORDER BY u.username ASC
                    """
                    df_p = pd.read_sql_query(query_p, conn, params=(sel_sub_id_p, sel_sem_id_p))
                    
                    edited_p = st.data_editor(
                        df_p, 
                        column_config={
                            "student_id": None, 
                            "Roll": st.column_config.TextColumn("Roll No.", disabled=True),
                            "Name": st.column_config.TextColumn("Student Name", disabled=True),
                            "p_att_present": st.column_config.NumberColumn("Lab Attended", min_value=0, step=1),
                            "p_att_total": st.column_config.NumberColumn("Total Labs", min_value=1, step=1),
                            "p_perf_raw": st.column_config.NumberColumn(f"Lab Performance (Max {cfg_max_perf:.0f})", min_value=0.0, max_value=cfg_max_perf, step=0.5),
                            "p_report_raw": st.column_config.NumberColumn(f"Lab Reports (Max {cfg_max_report:.0f})", min_value=0.0, max_value=cfg_max_report, step=0.5),
                            "p_test_raw": st.column_config.NumberColumn(f"Practical Test (Max {cfg_max_test:.0f})", min_value=0.0, max_value=cfg_max_test, step=0.5),
                            "p_viva_raw": st.column_config.NumberColumn(f"Viva Voce (Max {cfg_max_viva:.0f})", min_value=0.0, max_value=cfg_max_viva, step=0.5)
                        }, 
                        use_container_width=True, 
                        hide_index=True, 
                        key="practical_editor"
                    )

                    if st.button("💾 Synchronize Practical Marks", use_container_width=True, type="primary"):
                        for _, r in edited_p.iterrows():
                            c.execute("""
                                INSERT INTO student_marks (
                                    student_id, subject_id, p_att_present, p_att_total,
                                    p_perf_raw, p_report_raw, p_test_raw, p_viva_raw
                                ) VALUES (?,?,?,?,?,?,?,?)
                                ON CONFLICT(student_id, subject_id) DO UPDATE SET 
                                    p_att_present=excluded.p_att_present,
                                    p_att_total=excluded.p_att_total,
                                    p_perf_raw=excluded.p_perf_raw,
                                    p_report_raw=excluded.p_report_raw,
                                    p_test_raw=excluded.p_test_raw,
                                    p_viva_raw=excluded.p_viva_raw
                            """, (
                                int(r['student_id']), int(sel_sub_id_p),
                                int(r['p_att_present']), int(r['p_att_total']),
                                float(r['p_perf_raw']), float(r['p_report_raw']),
                                float(r['p_test_raw']), float(r['p_viva_raw'])
                            ))
                        conn.commit()
                        st.success("✅ Practical lab records successfully synchronized and locked.")
                        st.rerun()

                    # 🌟 THE RESTORED PROCESSED PRACTICAL TOTALS MATRIX VIEW
                    st.write("")
                    st.divider()
                    st.subheader("🧪 Step 2: Processed Practical Totals (Out of 25)")
                    
                    res_p = []
                    for _, r in edited_p.iterrows():
                        calc_res_p = calculate_internal_practical(r.to_dict(), sel_sub_id_p, conn)
                        res_p.append({
                            "Roll No.": r['Roll'],
                            "Student Name": r['Name'],
                            "Total Score (/25)": f"{calc_res_p[0]:.2f}",
                            "Lab Standing": "✅ Eligible" if calc_res_p[1] else "❌ Ineligible (Lab Attendance < 70%)"
                        })
                    st.dataframe(res_p, use_container_width=True, hide_index=True)

                # === REMOVED CLUTTERING LOCAL INPUT FIELDS - READS FROM REGISTRY ===
                    st.write("")
                    st.markdown("### 🖨️ Official Institutional Document Generator")
                    st.info("💡 The print engine is fully connected. The ledger header below automatically uses the credentials set in your Global Registry panel at the top.")
                    
                    # Date picking manual entry
                    ledger_date_p = st.date_input("Ledger Issue Date:", value=None, key="prac_ledger_date")

                    if st.button("📄 Compile Standardized Practical Ledger Roster", use_container_width=True, type="primary", key="print_prac_ledger_btn"):
                        sub_details_p = pd.read_sql_query("SELECT name FROM subjects WHERE id = ?", conn, params=(int(sel_sub_id_p),))
                        s_name_p = sub_details_p.iloc[0]['name'] if not sub_details_p.empty else "Engineering Hydrology"
                        formatted_date_p = ledger_date_p.strftime("%Y-%m-%d") if ledger_date_p else "............................."
                        
                        p_html = f"""
                        <script>
                            function downloadExcelPrac() {{
                                var table = document.getElementById("practical_ledger_table");
                                var html = table.outerHTML;
                                var url = 'data:application/vnd.ms-excel,' + encodeURIComponent(html);
                                var a = document.createElement('a');
                                a.href = url;
                                a.download = '{s_name_p.replace(" ", "_")}_Practical_Ledger.xls';
                                a.click();
                            }}
                        </script>
                        <style>
                            @page {{ 
                                size: landscape; 
                                margin: 10mm 10mm 10mm 10mm; 
                            }}
                            @media print {{
                                div[data-testid="stSidebar"], button, header, .stAppDeployButton, .no-print {{ display: none !important; }}
                                body, .main .block-container {{ padding: 0 !important; margin: 0 !important; background: #fff !important; }}
                                .repeat-header {{ display: table-header-group !important; }}
                                .ledger-row {{ page-break-inside: avoid !important; break-inside: avoid !important; }}
                            }}
                            .download-btn {{
                                background-color: #10B981; color: white; padding: 8px 16px; 
                                border: none; border-radius: 4px; font-weight: bold; cursor: pointer;
                                font-size: 12px; margin-bottom: 15px; float: right; font-family: Arial, sans-serif;
                            }}
                            .print-table {{
                                width: 100%; border-collapse: collapse; font-family: Arial, sans-serif; color: #111111;
                                margin: 0 auto;
                            }}
                            .print-table th, .print-table td {{
                                border: 1px solid #000000 !important; padding: 6px 4px; text-align: center; font-size: 11px;
                            }}
                            .text-left {{ text-align: left !important; }}
                            .nq-text {{ color: #dc2626 !important; font-weight: bold; background-color: #fee2e2 !important; }}
                            
                            /* 🎨 REFINED SYSTEM SCHEME CLASSES */
                            .meta-info-table {{
                                width: 100%;
                                border-collapse: collapse !important;
                                margin-top: 5px;
                            }}
                            .meta-info-table td {{
                                border: none !important;
                                padding: 3px 0px !important;
                                font-size: 12px !important;
                                text-align: left !important;
                            }}
                            .breakdown-box-table {{
                                width: 100%;
                                border-collapse: collapse !important;
                                background-color: #ffffff;
                            }}
                            .breakdown-box-table th {{
                                background-color: #fafafa !important;
                                color: #000000 !important;
                                border: 1px solid #000000 !important;
                                font-size: 11px !important;
                                padding: 5px !important;
                                font-weight: bold !important;
                                text-transform: uppercase;
                            }}
                            .breakdown-box-table td {{
                                border: 1px solid #000000 !important;
                                font-size: 10px !important;
                                padding: 3px 8px !important;
                                text-align: left !important;
                            }}
                            .breakdown-label {{
                                display: inline-block;
                                width: 170px;
                                font-weight: 500;
                            }}
                        </style>
                        
                        <div style="background-color: #ffffff; padding: 5px; color: #111111;">
                            <button class="download-btn no-print" onclick="downloadExcelPrac()">📥 Download Excel Spreadsheet</button>
                            <button class="download-btn no-print" style="background-color: #3b82f6; margin-right: 10px;" onclick="window.print()">🖨️ Print / Save PDF</button>
                            <div style="clear: both;"></div>

                            <table class="print-table" id="practical_ledger_table">
                                <thead class="repeat-header">
                                    <tr>
                                        <th colspan="10" style="background-color: #ffffff; border: none !important; padding-bottom: 8px;">
                                            <div style="text-align: center; font-weight: bold; line-height: 1.3; margin-bottom: 10px;">
                                                <div style="font-size: 16px; text-transform: uppercase; letter-spacing: 0.5px;">{st.session_state.g_univ}</div>
                                                <div style="font-size: 13px;">{st.session_state.g_inst_body}</div>
                                                <div style="font-size: 14px; font-weight: bold;">{st.session_state.g_college}</div>
                                                <div style="font-size: 12px; margin-top: 4px; padding-bottom: 2px; font-weight: bold; color: #222;">
                                                    {st.session_state.g_exam_title}
                                                </div>
                                            </div>
                                            
                                            <table class="meta-info-table">
                                                <tr>
                                                    <td style="width: 38.5%;"><b>Batch:</b> {st.session_state.g_batch}</td>
                                                    <td style="width: 33.5%;"><b>Level:</b> {st.session_state.g_prog}</td>
                                                    <td style="width: 28%; padding: 0 !important; vertical-align: top;" rowspan="5">
                                                        <table class="breakdown-box-table">
                                                            <thead>
                                                                <tr>
                                                                    <th colspan="2">Marks Breakdown</th>
                                                                </tr>
                                                            </thead>
                                                            <tbody>
                                                                <tr><td><span class="breakdown-label">Attendance/Lab Performance</span>: 20%</td></tr>
                                                                <tr><td><span class="breakdown-label">Initial Report</span>: 20%</td></tr>
                                                                <tr><td><span class="breakdown-label">Final Report</span>: 20%</td></tr>
                                                                <tr><td><span class="breakdown-label">Viva/Quiz</span>: 20%</td></tr>
                                                                <tr><td><span class="breakdown-label">Lab Test/Presentation</span>: 20%</td></tr>
                                                            </tbody>
                                                        </table>
                                                    </td>
                                                </tr>
                                                <tr>
                                                    <td><b>Year/Part:</b> {st.session_state.g_yp}</td>
                                                    <td><b>Programme:</b> {st.session_state.g_prog}</td>
                                                </tr>
                                                <tr>
                                                    <td><b>Subject Name:</b> {s_name_p.upper()}</td>
                                                    <td><b>Evaluation:</b> Practical Ledger Board</td>
                                                </tr>
                                                <tr>
                                                    <td><b>Subject Code No:</b> {st.session_state.g_sub_code}</td>
                                                    <td><b>Full Marks:</b> {st.session_state.g_f_marks}</td>
                                                </tr>
                                                <tr>
                                                    <td><b>Department:</b> {st.session_state.g_dept}</td>
                                                    <td><b>Pass Marks:</b> {st.session_state.g_p_marks}</td>
                                                </tr>
                                            </table>
                                        </th>
                                    </tr>
                                    <tr style="background-color: #fafafa; font-weight: bold;">
                                        <th style="width: 4%;">S.N.</th>
                                        <th style="text-align: left; padding-left: 8px; width: 25%;">Student Name</th>
                                        <th style="width: 15%;">CRN</th>
                                        <th style="padding: 6px; font-size: 11px;">Attendance/Lab Performance</th>
                                        <th style="padding: 6px; font-size: 11px;">Initial Report</th>
                                        <th style="padding: 6px; font-size: 11px;">Final Report</th>
                                        <th style="padding: 6px; font-size: 11px;">Viva/Quiz</th>
                                        <th style="padding: 6px; font-size: 11px;">Lab Test/Presentation</th>
                                        <th style="width: 8%;">In Figures</th>
                                        <th style="width: 15%;">In Words</th>
                                    </tr>
                                </thead>
                                <tbody>
                        """
                        
                        for idx, row in edited_p.iterrows():
                            s_meta_p = row.to_dict()
                            c_tot_p, is_elig_p = calculate_internal_practical(s_meta_p, sel_sub_id_p, conn)
                            word_tot_p = score_to_words(c_tot_p) if is_elig_p else "RETAINED"
                            fig_out_p = f"{c_tot_p:.0f}" if is_elig_p else "NQ"
                            
                            r_p_att = (s_meta_p['p_att_present'] / s_meta_p['p_att_total']) * 5.0 if s_meta_p['p_att_total'] > 0 else 0.0
                            r_p_perf = (s_meta_p['p_perf_raw'] / cfg_max_perf) * 5.0
                            r_p_rep = (s_meta_p['p_report_raw'] / cfg_max_report) * 5.0
                            r_p_tst = (s_meta_p['p_test_raw'] / cfg_max_test) * 5.0
                            r_p_viv = (s_meta_p['p_viva_raw'] / cfg_max_viva) * 5.0

                            row_class_p = 'class="nq-text"' if not is_elig_p else ''

                            p_html += f'''
                                    <tr class="ledger-row">
                                        <td>{idx + 1}</td>
                                        <td class="text-left" style="font-weight: bold; padding-left: 8px;">{s_meta_p['Name'].upper()}</td>
                                        <td style="font-family: monospace;">{s_meta_p['Roll']}</td>
                                        <td>{(r_p_att + r_p_perf):.1f}</td>
                                        <td>{r_p_rep:.1f}</td>
                                        <td>{r_p_rep:.1f}</td>
                                        <td>{r_p_viv:.1f}</td>
                                        <td>{r_p_tst:.1f}</td>
                                        <td {row_class_p}>{fig_out_p}</td>
                                        <td class="text-left" style="font-size: 10px; font-weight: bold;" {row_class_p}>{word_tot_p}</td>
                                    </tr>
                            '''
                            
                        p_html += f"""
                                    </tbody>
                                </table>

                                <table style="width: 100%; margin-top: 40px; font-size: 11px; line-height: 1.8; font-family: Arial, sans-serif; font-weight: bold;">
                                    <tr>
                                        <td style="width: 35%; vertical-align: top;"><strong>Date:</strong> {formatted_date_p}</td>
                                        <td style="width: 35%; vertical-align: top;">
                                            <strong>Name of Examiner:</strong> {st.session_state.g_teacher}<br>
                                            <strong>Name of HoD:</strong> {st.session_state.g_hod}
                                        </td>
                                        <td style="width: 30%; vertical-align: top; text-align: right;">
                                            <strong>Signature:</strong> ........................................<br>
                                            <strong>Signature:</strong> ........................................
                                        </td>
                                    </tr>
                                    <tr>
                                        <td style="padding-top: 15px; font-weight: bold;" colspan="2">Note: Absentees-A And Failed Marks must be incircled in red.</td>
                                        <td style="padding-top: 15px; font-weight: bold; text-align: right;">Received Date (Exam Section) : .................</td>
                                    </tr>
                                </table>
                            </div>
                        </div>
                        """
                        import streamlit.components.v1 as components
                        calc_height_p = 500 + (len(edited_p) * 45)
                        components.html(p_html, height=max(calc_height_p, 700), scrolling=True)
           # ================= MANAGE STUDENTS (TABS[6] - SECTION AWARE) =================
    with tabs[6]:
        st.subheader("⚠️ Emergency Fix for Existing Students")
        col_fix1, col_fix2 = st.columns(2)
        
        with col_fix1:
            if st.button("🔧 Fix ALL Students with NULL semester", use_container_width=True):
                default_sem = pd.read_sql_query("SELECT id FROM semesters ORDER BY id ASC LIMIT 1", conn)
                if not default_sem.empty:
                    default_sem_id = int(default_sem.iloc[0]['id'])
                    c.execute("UPDATE users SET semester_id = ? WHERE role = 'student' AND semester_id IS NULL", (default_sem_id,))
                    conn.commit()
                    st.success("✅ Fixed {} students - assigned to semester_id {}".format(c.rowcount, default_sem_id))
                    st.rerun()
                else:
                    st.error("No semesters available to assign")
                    
        with col_fix2:
            if st.button("🧼 Fix ALL Students with NULL section", use_container_width=True):
                c.execute("UPDATE users SET section = 'A' WHERE role = 'student' AND (section IS NULL OR section = '')")
                conn.commit()
                st.success("✅ Cleaned {} student profiles - assigned to default Section A".format(c.rowcount))
                st.rerun()
    
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
                
                # Side-by-side pickers for Section and Lab Group
                c_sel_a, c_sel_b = st.columns(2)
                with c_sel_a:
                    student_section = st.selectbox("Assign Section", ["A", "B"], key="student_section_picker")
                with c_sel_b:
                    # ➕ Choose the Lab Group allocation
                    student_lab_group = st.selectbox("Assign Lab Group", ["Group 1", "Group 2", "Group 3", "Group 4"], key="student_lab_group_picker")
                    
                st.info(f"Will assign to Semester ID: {semester_id} | Sec: {student_section} | {student_lab_group}")

                if st.button("Create Student", use_container_width=True, type="primary"):
                    if not username or not password or not student_name:
                        st.error("All fields except email are required.")
                    else:
                        try:
                            c.execute("""
                                INSERT INTO users(full_name, username, password, role, semester_id, email, section, lab_group)
                                VALUES(?, ?, ?, ?, ?, ?, ?, ?)
                            """, (
                                student_name.strip(),
                                username.strip(),
                                hash_password(password.strip()),
                                "student",
                                semester_id,
                                email_input.strip() if email_input else None,
                                student_section,
                                student_lab_group
                            ))
                            conn.commit()
                            st.success(f"✅ Student '{username}' created successfully in Section {student_section} [{student_lab_group}]!")
                            st.rerun()
                        except sqlite3.IntegrityError:
                            st.error("Username already exists.")
                        except Exception as e:
                            st.error("Error: {}".format(str(e)))

        st.divider()

        # ================= FIX: BULK CSV STUDENT LOADER ENGINE WITH SECTIONS =================
        st.subheader("Bulk Upload Students via CSV")
        st.info("CSV layout must strictly follow headers: name, username, password, semester, email, section")
        csv_file = st.file_uploader("Upload CSV Registry Document", type=["csv"], key="student_csv")

        if csv_file:
            df_csv = pd.read_csv(csv_file)
            # Normalize column text headers to match key parsing expectations
            df_csv.columns = df_csv.columns.str.strip().str.lower()
            
            # ➕ Updated to explicitly check for the section field column header
            required_cols = {"name", "username", "password", "semester", "email", "section"}

            if not required_cols.issubset(df_csv.columns):
                st.error("❌ CSV layout invalid. Ensure it contains exactly: name, username, password, semester, email, section")
            else:
                st.write("🔍 **Data Stream Preview:**", df_csv.head())
                
                if st.button("🚀 Process & Register Students into Database", use_container_width=True, type="primary"):
                    sems_list = pd.read_sql_query("SELECT * FROM semesters", conn)
                    success_count, error_count = 0, 0

                    for _, row in df_csv.iterrows():
                        try:
                            clean_name = str(row["name"]).strip()
                            clean_user = str(row["username"]).strip()
                            clean_sem = str(row["semester"]).strip()
                            clean_email = str(row["email"]).strip() if not pd.isna(row["email"]) else None
                            
                            # ➕ Read section data cleanly, default to 'A' if field is blank
                            clean_sec = str(row["section"]).strip().upper() if not pd.isna(row["section"]) else "A"
                            if clean_sec not in ["A", "B"]:
                                clean_sec = "A"
                                
                            raw_pw = str(row["password"]).replace('.0', '').strip()
                        
                            # Match semester text name directly to relational primary database index key mappings
                            sem_match = sems_list[sems_list["name"] == clean_sem]
                            if not sem_match.empty:
                                sem_id = int(sem_match["id"].values[0])
                                
                                c.execute("""
                                    INSERT INTO users(full_name, username, password, role, semester_id, email, section)
                                    VALUES(?,?,?,?,?,?,?)
                                """, (clean_name, clean_user, hash_password(raw_pw), "student", sem_id, clean_email, clean_sec))
                                success_count += 1
                            else:
                                error_count += 1
                        except Exception as e:
                            error_count += 1
                
                    # Permanently commit data to database storage file
                    conn.commit()
                    
                    if success_count > 0:
                        st.success("✅ Master registry parsed successfully! {} student accounts securely created.".format(success_count))
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ Record injection failed. {} processing conflicts encountered.".format(error_count))

        st.divider()

        # ================= REGISTERED STUDENT LIST (INTERACTIVE EDITABLE GRID - TEMP NO LAB GROUP) =================
        st.subheader("📋 Registered Student List")
        all_sems_list = pd.read_sql_query("SELECT * FROM semesters ORDER BY name ASC", conn)
        
        col_dir1, col_dir2 = st.columns(2)
        with col_dir1:
            list_filter = st.selectbox("View Students by Semester", ["All"] + all_sems_list["name"].tolist(), key="view_filter")
        with col_dir2:
            list_sec_filter = st.selectbox("Filter Directory by Section", ["All Sections", "Section A", "Section B"], key="view_sec_filter")

        # Dynamically build structural query restrictions based on selectors
        params = []
        where_clauses = ["users.role='student'"]

        if list_filter != "All":
            where_clauses.append("semesters.name = ?")
            params.append(list_filter)

        if list_sec_filter != "All Sections":
            sec_letter = "A" if list_sec_filter == "Section A" else "B"
            where_clauses.append("users.section = ?")
            params.append(sec_letter)

        where_stmt = " AND ".join(where_clauses)

        # Query including the structural lab group field data
        query = f"""
            SELECT users.id as student_id, users.username as [Roll No.], users.full_name as [Student Name], 
                   users.email as [Email], COALESCE(semesters.name, 'No Semester') as Semester,
                   users.section as Section, users.lab_group as [Lab Group]
            FROM users 
            LEFT JOIN semesters ON users.semester_id = semesters.id 
            WHERE {where_stmt}
            ORDER BY semesters.name ASC, users.section ASC, users.username ASC
        """
        students_df = pd.read_sql_query(query, conn, params=params)

        if students_df.empty:
            st.info("No students found matching those selection criteria.")
        else:
            st.info("💡 **Tip:** You can change any student's **Section** or **Lab Group** directly inside the table rows below, then click the Save button.")
            
            edited_roster_df = st.data_editor(
                students_df,
                column_config={
                    "student_id": None, 
                    "Roll No.": st.column_config.TextColumn("Roll No.", disabled=True),
                    "Student Name": st.column_config.TextColumn("Student Name", disabled=True),
                    "Email": st.column_config.TextColumn("Email Address", disabled=True),
                    "Semester": st.column_config.TextColumn("Semester", disabled=True),
                    "Section": st.column_config.SelectboxColumn("Section", options=["A", "B"], required=True),
                    # ➕ Added interactive dropdown mapping option right inside row structures!
                    "Lab Group": st.column_config.SelectboxColumn("Lab Group", options=["Group 1", "Group 2", "Group 3", "Group 4"], required=True)
                },
                use_container_width=True,
                hide_index=True,
                key="interactive_student_roster_grid"
            )
            
            if st.button("💾 Save Roster Changes", use_container_width=True, type="primary"):
                try:
                    success_sync = 0
                    for _, row in edited_roster_df.iterrows():
                        s_id = int(row['student_id'])
                        updated_sec = str(row['Section']).strip().upper()
                        updated_grp = str(row['Lab Group']).strip()
                        
                        # Committing both settings live back into our permanent logs
                        c.execute("""
                            UPDATE users 
                            SET section = ?, lab_group = ? 
                            WHERE id = ?
                        """, (updated_sec, updated_grp, s_id))
                        success_sync += 1
                        
                    conn.commit()
                    st.success(f"✅ Roster configuration synchronized! Updated {success_sync} profiles successfully.")
                    st.balloons()
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Synchronization Error: {str(e)}")
        
            st.info(f"📊 Total Matches Found: **{len(students_df)} students**")
        
            csv_data = students_df[['Roll No.', 'Student Name', 'Email', 'Semester', 'Section']].to_csv(index=False).encode('utf-8')
            st.download_button(f"📥 Download {list_filter}_{list_sec_filter.replace(' ', '_')} List (CSV)", csv_data, f"Students_{list_filter}_{list_sec_filter}.csv", "text/csv", use_container_width=True)

        st.divider()

        # ================= ENHANCED: SELECTIVE & BULK STUDENT DELETION METRICS =================
        st.subheader("🗑️ Advanced Student Deletion Suite")
        
        if students_df.empty:
            st.info("No active students loaded in the directory to delete.")
        else:
            # Create a checkable selection workspace dataframe 
            delete_prep_df = students_df.copy()
            delete_prep_df.insert(0, "Select", False) # 👈 Add target selection checkboxes
            
            st.markdown("#### Mode 1: Selective Dropdown Deletion (Individual)")
            student_options = {
                f"{row['Semester']} | Sec {row['Section']} | {row['Roll No.']} | {row['Student Name']}": row['student_id'] 
                for _, row in students_df.iterrows()
            }
            selected_to_delete = st.selectbox("Pick an individual student to remove immediately", list(student_options.keys()), key="ind_del_select")
            
            if st.button("🗑️ Delete Single Selected Student", type="primary", key="btn_single_del"):
                s_id = student_options[selected_to_delete]
                c.execute("DELETE FROM submissions WHERE student_id=?", (int(s_id),))
                c.execute("DELETE FROM users WHERE id=?", (int(s_id),))
                conn.commit()
                st.success("✅ Individual profile and submission records removed.")
                st.rerun()

            st.divider()
            st.markdown("#### Mode 2: Selective Batch Deletion via Grid Selection")
            st.info("Check the **'Select'** column boxes for the specific students you want to delete in batch.")
            
            # Interactive deletion grid
            editable_del_grid = st.data_editor(
                delete_prep_df,
                column_config={
                    "Select": st.column_config.CheckboxColumn("Select", default=False),
                    "student_id": None,
                    "Roll No.": st.column_config.TextColumn("Roll No.", disabled=True),
                    "Student Name": st.column_config.TextColumn("Student Name", disabled=True),
                    "Email": st.column_config.TextColumn("Email Address", disabled=True),
                    "Semester": st.column_config.TextColumn("Semester", disabled=True),
                    "Section": st.column_config.TextColumn("Section", disabled=True)
                },
                use_container_width=True,
                hide_index=True,
                key="selective_deletion_grid"
            )
            
            # Extract target lists checked by user
            selected_rows = editable_del_grid[editable_del_grid["Select"] == True]
            target_ids = selected_rows["student_id"].tolist()
            
            col_b1, col_b2 = st.columns([1, 2])
            with col_b1:
                btn_label = f"🗑️ Delete Checked ({len(target_ids)})"
                if st.button(btn_label, type="primary", key="btn_checked_del", disabled=(len(target_ids) == 0)):
                    # Convert IDs to tuple for SQLite bulk transaction processing
                    id_tuple = tuple(int(x) for x in target_ids)
                    query_placeholder = f"({','.join(['?']*len(target_ids))})"
                    
                    c.execute(f"DELETE FROM submissions WHERE student_id IN {query_placeholder}", id_tuple)
                    c.execute(f"DELETE FROM users WHERE id IN {query_placeholder}", id_tuple)
                    conn.commit()
                    st.success(f"✅ Successfully wiped {len(target_ids)} selected student accounts!")
                    st.rerun()
            with col_b2:
                st.warning(f"⚠️ Action will purge all checked rows and their corresponding assignment file uploads.")

            st.divider()
            st.markdown("#### Mode 3: Nuclear Bulk Deletion (All filtered items matches)")
            # Captures the text filters currently being applied in Mode 1's View Filters (e.g. "All", "Semester 1", etc.)
            active_sem_scope = list_filter
            active_sec_scope = list_sec_filter
            
            st.error(f"🚨 **DANGER ZONE:** This will instantly drop **ALL {len(students_df)} students** showing in your filtered view directory above (**{active_sem_scope} | {active_sec_scope}**).")
            
            # Setup a matching validation phrase confirmation input trap to prevent accidents
            bulk_confirm_phrase = st.text_input(
                f"Type exactly **PURGE-{active_sem_scope.upper().replace(' ', '')}** to confirm total wipeout:",
                key="bulk_wipe_confirm_text"
            )
            
            expected_phrase = f"PURGE-{active_sem_scope.upper().replace(' ', '')}"
            
            if st.button(f"💥 Execute Bulk Purge of All {len(students_df)} Listed Students", type="primary", disabled=(bulk_confirm_phrase != expected_phrase), use_container_width=True):
                all_listed_ids = students_df["student_id"].tolist()
                id_listed_tuple = tuple(int(y) for y in all_listed_ids)
                query_listed_placeholder = f"({','.join(['?']*len(all_listed_ids))})"
                
                c.execute(f"DELETE FROM submissions WHERE student_id IN {query_listed_placeholder}", id_listed_tuple)
                c.execute(f"DELETE FROM users WHERE id IN {query_listed_placeholder}", id_listed_tuple)
                conn.commit()
                st.error(f"💥 Complete Purge Triggered: Cleaned out {len(all_listed_ids)} accounts from database logs.")
                st.rerun()

        st.divider()

        # ================= UPDATE ASSIGNMENT (WITH SECTIONS) =================
        st.subheader("🔧 Update Semester & Section Assignment")
        all_students = pd.read_sql_query("SELECT id, username, full_name, section FROM users WHERE role='student' ORDER BY username ASC", conn)
        if not all_students.empty:
            student_map = {f"{row['username']} ({row['full_name']}) [Current: {row['section']}]": row['id'] for _, row in all_students.iterrows()}
            c_up1, c_up2, c_up3 = st.columns(3)
            with c_up1:
                target_student = st.selectbox("Select Student", list(student_map.keys()), key="up_stud")
            with c_up2:
                new_sem_list = pd.read_sql_query("SELECT id, name FROM semesters ORDER BY name ASC", conn)
                target_sem = st.selectbox("New Semester Target", new_sem_list["name"], key="up_sem")
            with c_up3:
                # ➕ Allows fast on-the-fly cross-section reassignments
                target_sec = st.selectbox("New Section Target", ["A", "B"], key="up_sec")
        
            if st.button("💾 Update Assignment Metrics", use_container_width=True):
                new_sem_id = int(new_sem_list[new_sem_list["name"] == target_sem]["id"].values[0])
                c.execute("UPDATE users SET semester_id=?, section=? WHERE id=?", (new_sem_id, target_sec, student_map[target_student]))
                conn.commit()
                st.success("Student assigned to {} Section {} successfully!".format(target_sem, target_sec))
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
    # ===================================================================
    # 🎓 360° STUDENT BIO PORTFOLIO & CONTINUOUS ASSESSMENT SCORECARD
    # ===================================================================
    with tabs[9]:
        st.markdown("## 🔍 Student Profile & Performance Analytics Hub")
        st.write("Search for any individual student to review their complete institutional bio, assignment statistics, and cross-subject exam ledger cards.")
        
        # 1. Harvest overall student lists dynamically from database architecture
        all_students = pd.read_sql_query("""
            SELECT users.id, users.username, users.full_name, semesters.name as semester, users.semester_id
            FROM users
            LEFT JOIN semesters ON users.semester_id = semesters.id
            WHERE users.role='student'
            ORDER BY users.username ASC
        """, conn)
        
        if all_students.empty:
            st.info("No students registered yet in the system roster.")
        else:
            # Search filter blocks
            col_profile1, col_profile2 = st.columns([2, 1])
            with col_profile1:
                search_profile = st.text_input("🔍 Search student by name or username ID handle:", key="search_profile_input")
            
            with col_profile2:
                if search_profile:
                    filtered = all_students[
                        all_students['username'].str.contains(search_profile, case=False) |
                        all_students['full_name'].str.contains(search_profile, case=False)
                    ]
                else:
                    filtered = all_students
            
            if filtered.empty:
                st.warning("No matching student entities discovered.")
            else:
                # Map dynamic handles onto drop selector metrics
                student_options = {
                    f"{row['username'].upper()} ({row['full_name'].upper()}) — {row['semester']}": row.to_dict()
                    for _, row in filtered.iterrows()
                }
                
                selected_key = st.selectbox("🎯 Target Select Student Record Viewport:", list(student_options.keys()))
                
                if selected_key:
                    selected_student_meta = student_options[selected_key]
                    student_id = int(selected_student_meta['id'])
                    active_semester_id = selected_student_meta['semester_id']
                    
                    # Package execution parameters into structural dictionary matching original bio engine assumptions
                    profile = get_student_profile(student_id)
                    
                    if profile:
                        st.write("")
                        # Premium Corporate Bio Identity Banner
                        st.markdown(f"""
                        <div style='background: linear-gradient(135deg, #004b87 0%, #002845 100%); 
                                    padding: 25px; border-radius: 8px; color: white; font-family: Arial, sans-serif; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
                            <h2 style='margin:0; text-transform: uppercase; letter-spacing: 0.5px;'>{profile['info']['full_name']}</h2>
                            <p style='margin:6px 0 0 0; font-size:14px; opacity:0.9;'>
                                <strong>CRN / Username:</strong> {profile['info']['username']} | 
                                <strong>Current Stage:</strong> {profile['info']['semester']} | 
                                <strong>Program:</strong> Civil Engineering
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.write("")
                        
                        # 📊 SECTION A: ORIGINAL AI QUIZ / ASSIGNMENT ANALYSIS ENGINE
                        st.subheader("📊 Personal Growth & Assignment Performance")
                        submissions_df = profile['submissions']
                        graded_df = submissions_df[submissions_df['marks'].notna() & (submissions_df['marks'] != '')].copy()

                        if not graded_df.empty:
                            graded_df['Marks'] = pd.to_numeric(graded_df['marks'], errors='coerce')
                            graded_df = graded_df.sort_values(by='deadline')
                            chart_data = graded_df[['assignment', 'Marks']].set_index('assignment')
                            st.line_chart(chart_data)
                        else:
                            st.info("Awaiting graded platform assignments to generate growth trends.")
                        
                        # KPI Badges
                        col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
                        with col_stat1:
                            st.metric("📤 Total Submissions", profile['stats']['total_submissions'])
                        with col_stat2:
                            st.metric("✅ Graded Items", profile['stats']['total_graded'])
                        with col_stat3:
                            st.metric("📊 Average Quiz Score", f"{profile['stats']['average']}/10")
                        with col_stat4:
                            st.metric("🏆 Best Quiz Score", f"{profile['stats']['highest']}/10")
                        
                        # 📋 Submission Tab History Dataframe
                        with st.expander("📋 Review AI Quiz & Assignment Submission History Log", expanded=False):
                            if profile['submissions'].empty:
                                st.info("No submissions entered yet.")
                            else:
                                def get_status(row):
                                    if row['marks'] and str(row['marks']).strip():
                                        return f"✅ Graded ({float(row['marks']):.1f}/10)"
                                    return "⏳ Pending Evaluation"
                                
                                display_df = profile['submissions'].copy()
                                display_df['Status'] = display_df.apply(get_status, axis=1)
                                st.dataframe(
                                    display_df[['subject', 'assignment', 'deadline', 'submission_time', 'Status']],
                                    use_container_width=True, hide_index=True
                                )
                        
                        st.divider()
                        
                        # 🏢 SECTION B: UNIVERSITY INTERNAL EXAM LEDGER MATRIX INSIGHTS
                        st.subheader("🏢 Official University Internal Assessment Scorecard")
                        st.write("Below are the current verified continuous internal assessment entries logged across departments for this semester tier.")
                        
                        # 📝 1. Cross-Subject Theory Mark Aggregator Ledger Card
                        st.markdown("#### 📝 Internal Theory Performance (Scaled to 40 Marks Matrix)")
                        
                        # ✅ DEFINED FIRST: Run the query right here to create tm_df securely!
                        theory_marks_query = """
                            SELECT sub.name as subject_name, sub.code as subject_code, sm.*
                            FROM student_marks sm
                            JOIN subjects sub ON sm.subject_id = sub.id
                            WHERE sm.student_id = ? AND sub.semester_id = ?
                        """
                        tm_df = pd.read_sql_query(theory_marks_query, conn, params=(int(student_id), int(active_semester_id)))
                        
                        if tm_df.empty:
                            st.info("No standardized internal theory entries registered for this semester layer yet.")
                        else:
                            theory_profile_rows = []
                            for _, tm_row in tm_df.iterrows():
                                c_tot, is_elig = calculate_internal_theory(tm_row.to_dict(), tm_row['subject_id'], conn)
                                word_tot = score_to_words(c_tot) if is_elig else "RETAINED"
                                fig_out = f"{c_tot:.0f}" if is_elig else "NQ"
                                
                                t_total_classes = tm_row['t_att_total'] if tm_row['t_att_total'] > 0 else 34
                                attendance_rate = (tm_row['t_att_present'] / t_total_classes * 100)
                                eligibility_status = "🟢 QUALIFIED" if is_elig else "🔴 NQ / RETAINED"
                                
                                active_cfg = pd.read_sql_query("SELECT * FROM subject_schemes WHERE subject_id = ?", conn, params=(int(tm_row['subject_id']),))
                                cfg_max_hw = float(active_cfg.iloc[0]['t_max_raw_hw']) if (not active_cfg.empty and 't_max_raw_hw' in active_cfg.columns) else 50.0
                                cfg_max_mid = float(active_cfg.iloc[0]['t_max_raw_mid']) if (not active_cfg.empty and 't_max_raw_mid' in active_cfg.columns) else 40.0
                                cfg_max_final = float(active_cfg.iloc[0]['t_max_raw_final']) if (not active_cfg.empty and 't_max_raw_final' in active_cfg.columns) else 40.0
                                cfg_max_other = float(active_cfg.iloc[0]['t_max_raw_other']) if (not active_cfg.empty and 't_max_raw_other' in active_cfg.columns) else 100.0

                                # 🧠 LIVE CUMULATIVE ASSIGNMENT CALCULATOR FOR PROFILE HUB
                                q_stud_marks_l = """
                                SELECT NULLIF(marks, '') as marks FROM submissions 
                                WHERE assignment_id IN (SELECT id FROM assignments WHERE subject_id = ?) AND student_id = ?
                                """
                                m_df_l = pd.read_sql_query(q_stud_marks_l, conn, params=(int(tm_row['subject_id']), int(student_id)))
                                live_cum_earned_l = 0.0
                                if not m_df_l.empty:
                                    for _, m_row_l in m_df_l.iterrows():
                                        m_val = m_row_l['marks']
                                        if m_val is not None and str(m_val).strip() != "" and str(m_val).strip().lower() != "none":
                                            try: 
                                                live_cum_earned_l += float(m_val)
                                            except ValueError: 
                                                pass

                                # Calculate scaled weights based on your stable infrastructure conversions
                                r_att = (tm_row['t_att_present'] / t_total_classes) * 4.0 if t_total_classes > 0 else 0.0
                                
                                # 🎯 FIXED CUMULATIVE MATH: Scales raw assignment sum out of 50.0 to its 10-mark ledger weight
                                r_hw = (float(live_cum_earned_l) / 50.0) * 10.0
                                
                                r_mid = (float(tm_row['t_mid_raw']) / float(cfg_max_mid)) * 10.0 if (cfg_max_mid and float(cfg_max_mid) > 0) else 0.0
                                r_final = (float(tm_row['t_final_raw']) / float(cfg_max_final)) * 10.0 if (cfg_max_final and float(cfg_max_final) > 0) else 0.0
                                r_ot = (float(tm_row['t_other_raw']) / float(cfg_max_other)) * 6.0 if (cfg_max_other and float(cfg_max_other) > 0) else 0.0

                                theory_profile_rows.append({
                                    "Code": tm_row['subject_code'],
                                    "Subject Name": tm_row['subject_name'].upper(),
                                    "Attendance %": f"{attendance_rate:.1f}%",
                                    "Att (4)": f"{r_att:.1f}",
                                    "Asmt (10)": f"{r_hw:.1f}",
                                    "Mid (10)": f"{r_mid:.1f}",
                                    "Final (10)": f"{r_final:.1f}",
                                    "Tut (6)": f"{r_ot:.1f}",
                                    "Score (40)": fig_out,
                                    "Status": eligibility_status
                                })
                            
                            # Render structured student dataframe matrix cleanly
                            theory_df_display = pd.DataFrame(theory_profile_rows)
                            st.dataframe(
                                theory_df_display.style.map(
                                    lambda val: 'background-color: #fee2e2; color: #dc2626; font-weight: bold;' if '🔴' in str(val) else None,
                                    subset=['Status']
                                ),
                                use_container_width=True, 
                                hide_index=True
                            )

                        st.write("")
                        
                        # 🧪 2. Cross-Subject Practical Mark Aggregator Ledger Card
                        st.markdown("#### 🧪 Practical Ledger Performance (Scaled to 25 Marks Matrix)")
                        
                        prac_marks_query = """
                            SELECT sub.name as subject_name, sub.code as subject_code, sm.*
                            FROM student_marks sm
                            JOIN subjects sub ON sm.subject_id = sub.id
                            WHERE sm.student_id = ? AND sub.semester_id = ?
                        """
                        pm_df = pd.read_sql_query(prac_marks_query, conn, params=(student_id, active_semester_id))
                        
                        if pm_df.empty:
                            st.info("No standardized practical tracking entries registered for this semester layer yet.")
                        else:
                            practical_profile_rows = []
                            for _, pm_row in pm_df.iterrows():
                                # 🔥 Force the unified practical calculator engine to execute live
                                c_tot_p, is_elig_p = calculate_internal_practical(pm_row.to_dict(), pm_row['subject_id'], conn)
                                fig_out_p = f"{c_tot_p:.0f}" if is_elig_p else "NQ"

                                p_total_classes = pm_row['p_att_total'] if pm_row['p_att_total'] > 0 else 12
                                prac_attendance_rate = (pm_row['p_att_present'] / p_total_classes * 100)
                                eligibility_status_p = "🟢 QUALIFIED" if is_elig_p else "🔴 NQ / RETAINED"
                                
                                # Fetch custom denominators set for this specific subject scheme template
                                active_lab_cfg = pd.read_sql_query("SELECT * FROM subject_schemes WHERE subject_id = ?", conn, params=(int(pm_row['subject_id']),))
                                cfg_max_perf = float(active_lab_cfg.iloc[0]['p_max_raw_perf']) if (not active_lab_cfg.empty and 'p_max_raw_perf' in active_lab_cfg.columns) else 100.0
                                cfg_max_report = float(active_lab_cfg.iloc[0]['p_max_raw_report']) if (not active_lab_cfg.empty and 'p_max_raw_report' in active_lab_cfg.columns) else 100.0
                                cfg_max_test = float(active_lab_cfg.iloc[0]['p_max_raw_test']) if (not active_lab_cfg.empty and 'p_max_raw_test' in active_lab_cfg.columns) else 100.0
                                cfg_max_viva = float(active_lab_cfg.iloc[0]['p_max_raw_viva']) if (not active_lab_cfg.empty and 'p_max_raw_viva' in active_lab_cfg.columns) else 100.0

                                # Process localized weight fractions out of 5.0 marks per category envelope safely
                                r_p_att = (pm_row['p_att_present'] / p_total_classes) * 5.0 if p_total_classes > 0 else 0.0
                                r_p_perf = (float(pm_row['p_perf_raw']) / float(cfg_max_perf)) * 5.0 if (cfg_max_perf and float(cfg_max_perf) > 0) else 0.0
                                r_p_rep = (float(pm_row['p_report_raw']) / float(cfg_max_report)) * 5.0 if (cfg_max_report and float(cfg_max_report) > 0) else 0.0
                                r_p_tst = (float(pm_row['p_test_raw']) / float(cfg_max_test)) * 5.0 if (cfg_max_test and float(cfg_max_test) > 0) else 0.0
                                r_p_viv = (float(pm_row['p_viva_raw']) / float(cfg_max_viva)) * 5.0 if (cfg_max_viva and float(cfg_max_viva) > 0) else 0.0

                                practical_profile_rows.append({
                                    "Code": pm_row['subject_code'],
                                    "Subject Name": pm_row['subject_name'].upper(),
                                    "Attendance %": f"{prac_attendance_rate:.1f}%",
                                    "Lab Perf (5)": f"{(r_p_att + r_p_perf):.1f}",
                                    "Init Report (5)": f"{r_p_rep:.1f}",
                                    "Final Report (5)": f"{r_p_rep:.1f}",
                                    "Viva/Quiz (5)": f"{r_p_viv:.1f}",
                                    "Lab Test (5)": f"{r_p_tst:.1f}",
                                    "Score (25)": fig_out_p,
                                    "Status": eligibility_status_p
                                })
                            
                            practical_df_display = pd.DataFrame(practical_profile_rows)
                            st.dataframe(
                                practical_df_display.style.map(
                                    lambda val: 'background-color: #fee2e2; color: #dc2626; font-weight: bold;' if '🔴' in str(val) else None,
                                    subset=['Status']
                                ),
                                use_container_width=True, hide_index=True
                            )
                            
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
                
                # ✅ FIXED: Mode-Adaptive container handles both Light and Dark backgrounds seamlessly
                st.markdown("""
                <div style='background-color: rgba(128, 128, 128, 0.08); 
                            padding: 15px; 
                            border-radius: 8px; 
                            border-left: 6px solid {}; 
                            margin-bottom: 10px;
                            border-top: 1px solid rgba(128, 128, 128, 0.15);
                            border-right: 1px solid rgba(128, 128, 128, 0.15);
                            border-bottom: 1px solid rgba(128, 128, 128, 0.15);'>
                    <h4 style='margin:0; color: {}; font-weight: 700;'>{} {}</h4>
                    <p style='color: inherit; margin: 10px 0; font-size: 1.1em; font-weight: 500;'>{}</p>
                    <small style='color: inherit; opacity: 0.7; font-weight: 400;'>Posted by {} on {}</small>
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
                
                # ⏱️ Evaluate soft window hours cleanly
                deadline_date = datetime.strptime(str(assignment['deadline']), '%Y-%m-%d').date()
                current_date = datetime.now(NST).date()
                
                today_dt = datetime.now(NST)
                deadline_dt = datetime.combine(deadline_date, datetime.min.time()).replace(tzinfo=NST)
                hours_late = (today_dt - deadline_dt).total_seconds() / 3600.0 if current_date > deadline_date else 0.0

                assignment_info = {
                    'id': assignment['id'],
                    'title': assignment['title'],
                    'subject': assignment['subject'],
                    'deadline': assignment['deadline'],
                    'days': days,
                    'status': status,
                    'color': color,
                    'hours_late': hours_late
                }
                
                if not submission.empty:
                    completed.append(assignment_info)
                elif current_date > deadline_date and hours_late > 48.0:
                    # Only mark as hard overdue if past 48 hours completely
                    overdue.append(assignment_info)
                elif status == "Due Today":
                    due_today.append(assignment_info)
                elif (current_date > deadline_date and hours_late <= 48.0) or status == "Due Soon":
                    # Sit in the yellow grace window section if late but under 48 hours
                    due_soon.append(assignment_info)
                else:
                    upcoming.append(assignment_info)
            
            # Display metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("🔴 Expired (>48h)", len(overdue))
            with col2:
                st.metric("🟠 Due Today", len(due_today))
            with col3:
                st.metric("🟡 Grace Window / Soon", len(due_soon))
            with col4:
                st.metric("✅ Completed", len(completed))
            
            st.divider()
            
            # Show completely expired assignments
            if overdue:
                st.error("🔴 **EXPIRED ASSIGNMENTS - Submission Closed!**")
                for assign in overdue:
                    st.warning("🔒 **{}** - {} (Locked: Past the maximum 48-hour leniency window)".format(
                        assign['subject'],
                        assign['title']
                    ))
            
            # Show due today (if any)
            if due_today:
                st.warning("🟠 **DUE TODAY - Final Chance for On-Time Credit!**")
                for assign in due_today:
                    st.info("⏰ **{}** - {}".format(assign['subject'], assign['title']))
            
            # Show grace window or due soon assignments
            if due_soon:
                st.info("🟡 **ACTIVE TASKS (Grace Window or Due Soon)**")
                for assign in due_soon:
                    if assign['hours_late'] > 0:
                        # Give a specific warning that they are in a penalty window but can still upload
                        if assign['hours_late'] <= 24.0:
                            st.error("⚠️ **LATE (Tier 1):** **{}** - {} (Overdue! Submit now to lock in a maximum **10% penalty deduction**)".format(assign['subject'], assign['title']))
                        else:
                            st.error("🚨 **CRITICAL LATE (Tier 2):** **{}** - {} (Overdue! Final 24-hour window before lock. Automatic **50% penalty deduction** applies)".format(assign['subject'], assign['title']))
                    else:
                        st.write("📌 **{}** - {} ({} days left)".format(
                            assign['subject'],
                            assign['title'],
                            assign['days']
                        ))
        
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

                    elif is_late and deadline_date is not None:
                        today_dt = datetime.now(NST)
                        deadline_dt = datetime.combine(deadline_date, datetime.min.time()).replace(tzinfo=NST)
                        hours_late = (today_dt - deadline_dt).total_seconds() / 3600.0
                        if hours_late <= 24.0:
                            st.warning("⚠️ **LATE SUBMISSION TIER 1:** The official deadline has passed. You may still upload your work within this 24-hour grace window, but an automatic **10% late penalty deduction** will be applied to your final score.")
                            uploaded = st.file_uploader("📤 Upload Your Answer PDF (10% Penalty Applied)", type=["pdf"], key="upload_l_10_{}".format(row['id']))
                            if st.button("Submit Late Assignment (Tier 1)", key="btn_l_10_{}".format(row['id']), type="secondary"):
                                if not uploaded:
                                    st.warning("⚠️ Please select a valid PDF file before submitting.")
                                else:
                                    timestamp = datetime.now(NST).strftime("%Y%m%d_%H%M%S")
                                    file_path = f"submission_files/{st.session_state.username}_{row['id']}_{timestamp}.pdf"
                                    with open(file_path, "wb") as f:
                                        f.write(uploaded.getbuffer())
                                    
                                    # Stamp database submission records with an unmistakable penalty marker tag
                                    late_tag = f"{datetime.now(NST).strftime('%Y-%m-%d %H:%M:%S')} [LATE-10%]"
                                    c.execute("""
                                        INSERT INTO submissions(assignment_id, student_id, submission_time, submission_file, marks, ai_summary) 
                                        VALUES(?,?,?,?,?,?)
                                    """, (int(row["id"]), int(st.session_state.user_id), late_tag, file_path, "", ""))
                                    conn.commit()
                                    st.error("🔴 Assignment logged successfully as Late (Tier 1: -10%).")
                                    st.balloons()
                                    st.rerun()

                        elif hours_late <= 48.0:
                            # 🟠 Late Submission Tier 2: 24 to 48 Hours Overdue
                            st.error("🚨 **CRITICAL LATE SUBMISSION (TIER 2):** This assignment is more than 24 hours overdue and is in the final grace window. You can submit your file, but an automatic **50% penalty deduction** will be stripped from your score.")
                            
                            uploaded = st.file_uploader("📤 Upload Your Answer PDF (50% Penalty Applied)", type=["pdf"], key="upload_l_50_{}".format(row['id']))
                            if st.button("Submit Late Assignment (Tier 2)", key="btn_l_50_{}".format(row['id']), type="primary"):
                                if not uploaded:
                                    st.warning("⚠️ Please select a valid PDF file before submitting.")
                                else:
                                    timestamp = datetime.now(NST).strftime("%Y%m%d_%H%M%S")
                                    file_path = f"submission_files/{st.session_state.username}_{row['id']}_{timestamp}.pdf"
                                    with open(file_path, "wb") as f:
                                        f.write(uploaded.getbuffer())
                                    
                                    # Stamp database submission records with an unmistakable penalty marker tag
                                    late_tag = f"{datetime.now(NST).strftime('%Y-%m-%d %H:%M:%S')} [LATE-50%]"
                                    c.execute("""
                                        INSERT INTO submissions(assignment_id, student_id, submission_time, submission_file, marks, ai_summary) 
                                        VALUES(?,?,?,?,?,?)
                                    """, (int(row["id"]), int(st.session_state.user_id), late_tag, file_path, "", ""))
                                    conn.commit()
                                    st.error("🔴 Assignment logged successfully as Critical Late (Tier 2: -50%).")
                                    st.balloons()
                                    st.rerun()

                        else:
                            # 🔒 Hard Lockout Tier 3: Past 48 Hours
                            st.error("🔒 **Submission Portal Locked:** This assignment has passed the maximum 48-hour late leniency threshold. The submission window is permanently closed.")
                            st.info("Automated uploads are no longer accepted for this record. Please coordinate with Er. Nirajan Katuwal directly.")

                    else:
                        # ✅ Case C: Not submitted and deadline is still open (On Time Submission)
                        days_left, _, _ = get_deadline_status(row['deadline'])
                        if days_left == 0:
                            st.warning("⚠️ **Final Call:** This assignment is due today!")
                        elif days_left is not None and days_left <= 2:
                            st.info("🟡 Only {} days left to submit!".format(days_left))

                        uploaded = st.file_uploader("📤 Upload Your Answer PDF", type=["pdf"], key="upload_on_time_{}".format(row['id']))
                        if st.button("Submit Assignment", key="submit_on_time_{}".format(row['id']), type="primary"):
                            if not uploaded:
                                st.warning("⚠️ Please upload a PDF file before submitting.")
                            else:
                                timestamp = datetime.now(NST).strftime("%Y%m%d_%H%M%S")
                                file_path = f"submission_files/{st.session_state.username}_{row['id']}_{timestamp}.pdf"
                                with open(file_path, "wb") as f:
                                    f.write(uploaded.getbuffer())

                                on_time_tag = datetime.now(NST).strftime("%Y-%m-%d %H:%M:%S")
                                c.execute("""
                                    INSERT INTO submissions(assignment_id, student_id, submission_time, submission_file, marks, ai_summary) 
                                    VALUES(?,?,?,?,?,?)
                                """, (int(row["id"]), int(st.session_state.user_id), on_time_tag, file_path, "", ""))
                                conn.commit()
                                st.success("✅ Assignment submitted successfully on time!")
                                st.balloons()
                                st.rerun()                                                
                   

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
    # ===================================================================
        # 🎓 PREMIUM CRASH-PROOF VISUAL PORTFOLIO LAYOUT (STUDENT VIEW)
        # ===================================================================
    with tabs[2]:
        st.header("📝 My Official Internal Performance")
        
        # 🌟 CSS FIX FOR EXPANDER FOCUS/OPEN BLINDING WHITE STATE
        st.markdown("""
        <style>
            div[data-testid="stExpander"] [data-testid="stMarkdownContainer"] p {
                color: #00E5FF !important;
                font-weight: 600 !important;
            }
            .streamlit-expanderHeader {
                background-color: rgba(10, 15, 30, 0.8) !important;
                border: 1px solid rgba(0, 229, 255, 0.2) !important;
                transition: all 0.3s ease !important;
            }
            .streamlit-expanderHeader:hover, .streamlit-expanderHeader:focus {
                background-color: rgba(0, 229, 255, 0.1) !important;
                border-color: #00E5FF !important;
            }
            .caption-white {
                color: #FFFFFF !important;
                font-size: 0.9rem !important;
                font-weight: 500;
                margin-bottom: 4px;
            }
        </style>
        """, unsafe_allow_html=True)
        
        # 1. Core Data Retrieval
        student_id = int(st.session_state.user_id)
        
        st.subheader("📊 Subject Standing & Marks Breakdown")
        subjects = pd.read_sql_query("SELECT id, name FROM subjects WHERE semester_id=?", conn, params=(sem_id,))
        
        for _, sub in subjects.iterrows():
            with st.container(border=True):
                # Dynamic Title Header
                st.markdown(f"### 📘 {sub['name'].upper()}")
                
                # Fetch official internal marks from the consolidated student_marks table
                m = pd.read_sql_query("SELECT * FROM student_marks WHERE student_id=? AND subject_id=?", 
                                     conn, params=(student_id, sub['id']))
                
                # Fetch dynamic subject configurations to calculate progress scales cleanly
                active_cfg = pd.read_sql_query("SELECT * FROM subject_schemes WHERE subject_id = ?", conn, params=(int(sub['id']),))
                cfg_max_hw = float(active_cfg.iloc[0]['t_max_raw_hw']) if (not active_cfg.empty and 't_max_raw_hw' in active_cfg.columns and pd.notna(active_cfg.iloc[0]['t_max_raw_hw'])) else 50.0
                cfg_max_mid = float(active_cfg.iloc[0]['t_max_raw_mid']) if (not active_cfg.empty and 't_max_raw_mid' in active_cfg.columns and pd.notna(active_cfg.iloc[0]['t_max_raw_mid'])) else 40.0
                cfg_max_final = float(active_cfg.iloc[0]['t_max_raw_final']) if (not active_cfg.empty and 't_max_raw_final' in active_cfg.columns and pd.notna(active_cfg.iloc[0]['t_max_raw_final'])) else 40.0
                cfg_max_other = float(active_cfg.iloc[0]['t_max_raw_other']) if (not active_cfg.empty and 't_max_raw_other' in active_cfg.columns and pd.notna(active_cfg.iloc[0]['t_max_raw_other'])) else 100.0
                
                cfg_max_perf = float(active_cfg.iloc[0]['p_max_raw_perf']) if (not active_cfg.empty and 'p_max_raw_perf' in active_cfg.columns and pd.notna(active_cfg.iloc[0]['p_max_raw_perf'])) else 100.0
                cfg_max_report = float(active_cfg.iloc[0]['p_max_raw_report']) if (not active_cfg.empty and 'p_max_raw_report' in active_cfg.columns and pd.notna(active_cfg.iloc[0]['p_max_raw_report'])) else 100.0
                cfg_max_test = float(active_cfg.iloc[0]['p_max_raw_test']) if (not active_cfg.empty and 'p_max_raw_test' in active_cfg.columns and pd.notna(active_cfg.iloc[0]['p_max_raw_test'])) else 100.0
                cfg_max_viva = float(active_cfg.iloc[0]['p_max_raw_viva']) if (not active_cfg.empty and 'p_max_raw_viva' in active_cfg.columns and pd.notna(active_cfg.iloc[0]['p_max_raw_viva'])) else 100.0

                if m.empty:
                    st.info("⏳ The lecturer has not finalized internal marks scores for this subject yet.")
                else:
                    try:
                        # 📦 1. EXTRACT DATA VALUES SAFELY FROM THE ACCOUNT LEDGER ROW
                        db_row = m.iloc[0]
                        
                        att_present_t = int(db_row['t_att_present']) if 't_att_present' in db_row and pd.notna(db_row['t_att_present']) else 0
                        att_total_t = int(db_row['t_att_total']) if 't_att_total' in db_row and pd.notna(db_row['t_att_total']) else 34
                        mid_raw_t = float(db_row['t_mid_raw']) if 't_mid_raw' in db_row and pd.notna(db_row['t_mid_raw']) else 0.0
                        final_raw_t = float(db_row['t_final_raw']) if 't_final_raw' in db_row and pd.notna(db_row['t_final_raw']) else 0.0
                        other_raw_t = float(db_row['t_other_raw']) if 't_other_raw' in db_row and pd.notna(db_row['t_other_raw']) else 0.0
                        
                        att_present_p = int(db_row['p_att_present']) if 'p_att_present' in db_row and pd.notna(db_row['p_att_present']) else 0
                        att_total_p = int(db_row['p_att_total']) if 'p_att_total' in db_row and pd.notna(db_row['p_att_total']) else 12
                        perf_raw_p = float(db_row['p_perf_raw']) if 'p_perf_raw' in db_row and pd.notna(db_row['p_perf_raw']) else 0.0
                        report_raw_p = float(db_row['p_report_raw']) if 'p_report_raw' in db_row and pd.notna(db_row['p_report_raw']) else 0.0
                        test_raw_p = float(db_row['p_test_raw']) if 'p_test_raw' in db_row and pd.notna(db_row['p_test_raw']) else 0.0
                        viva_raw_p = float(db_row['p_viva_raw']) if 'p_viva_raw' in db_row and pd.notna(db_row['p_viva_raw']) else 0.0

                        # Calculate totals from master math functions
                        t_total, t_eligible = calculate_internal_theory(db_row, sub['id'], conn)
                        p_total, p_eligible = calculate_internal_practical(db_row, sub['id'], conn)
                        
                        t_pct = (att_present_t / att_total_t * 100) if att_total_t > 0 else 0.0
                        p_pct = (att_present_p / att_total_p * 100) if att_total_p > 0 else 0.0

                        status_badge_t = "🟢 QUALIFIED" if t_eligible else "🔴 NOT QUALIFIED (NQ)"
                        status_badge_p = "🟢 QUALIFIED" if p_eligible else "🔴 NOT QUALIFIED (NQ)"
                        
                        # 🏛️ THEORY PORTFOLIO VISUAL BLOCKS
                        st.markdown("#### 📝 Theory Marks Breakdown")
                        
                        is_theory_eligible = (t_pct >= 70.0) and (t_total >= 16.0)
                        t_status_text = "🟢 QUALIFIED" if is_theory_eligible else "🔴 NOT QUALIFIED (NQ)"
                        
                        col_t1, col_t2, col_t3 = st.columns([1, 1, 2])
                        with col_t1:
                            fig_out = f"{t_total:.0f}" if is_theory_eligible else "NQ"
                            st.metric("Final Theory Score", f"{fig_out} / 40")
                        with col_t2:
                            st.metric("Theory Attendance Rate", f"{t_pct:.1f}%", f"{att_present_t}/{att_total_t} Days")
                        with col_t3:
                            st.write("") 
                            if is_theory_eligible:
                                st.success(f"Theory Exam Board Status: {t_status_text}")
                            else:
                                st.error(f"Theory Exam Board Status: {t_status_text}")

                        # 🧠 2. LIVE CUMULATIVE ASSIGNMENT SUMMATION ENGINE
                        q_stud_marks_p = """
                        SELECT NULLIF(marks, '') as marks FROM submissions 
                        WHERE assignment_id IN (SELECT id FROM assignments WHERE subject_id = ?) AND student_id = ?
                        """
                        m_df_p = pd.read_sql_query(q_stud_marks_p, conn, params=(int(sub['id']), int(student_id)))
                        live_cum_earned_p = 0.0
                        
                        if not m_df_p.empty:
                            for _, m_row_p in m_df_p.iterrows():
                                m_val = m_row_p['marks']
                                # Accumulate marks cleanly while completely filtering out non-graded items
                                if m_val is not None and str(m_val).strip() != "" and str(m_val).strip().lower() != "none":
                                    try: 
                                        live_cum_earned_p += float(m_val)
                                    except ValueError: 
                                        pass

                        # 🧮 3. CRASH-PROOF SCALE CONVERSION CALCULATION MATRIX
                        r_att = (int(att_present_t) / int(att_total_t)) * 4.0 if att_total_t > 0 else 0.0
                        
                        # Apply your strict cumulative math formula out of 50 raw assignment marks max
                        r_hw = (float(live_cum_earned_p) / 50.0) * 10.0
                        
                        # Safely normalize exams against custom denominators to protect against division by zero errors
                        r_mid = (float(mid_raw_t) / float(cfg_max_mid)) * 10.0 if (cfg_max_mid and float(cfg_max_mid) > 0) else 0.0
                        r_final = (float(final_raw_t) / float(cfg_max_final)) * 10.0 if (cfg_max_final and float(cfg_max_final) > 0) else 0.0
                        r_ot = (float(other_raw_t) / float(cfg_max_other)) * 6.0 if (cfg_max_other and float(cfg_max_other) > 0) else 0.0

                        # 🛡️ 4. CRASH-PROOF METRIC RENDERING UTILITIES
                        import math

                        def clean_nan_to_zero(val):
                            try:
                                if val is None or math.isnan(float(val)):
                                    return 0.0
                                return float(val)
                            except:
                                return 0.0

                        def compute_safe_progress(val, limit):
                            try:
                                cleaned_val = clean_nan_to_zero(val)
                                if cleaned_val <= 0.0 or limit <= 0.0:
                                    return 0.0
                                return min(max(cleaned_val / float(limit), 0.0), 1.0)
                            except:
                                return 0.0

                        disp_att = clean_nan_to_zero(r_att)
                        disp_hw = clean_nan_to_zero(r_hw)
                        disp_mid = clean_nan_to_zero(r_mid)
                        disp_final = clean_nan_to_zero(r_final)
                        disp_ot = clean_nan_to_zero(r_ot)

                        col_p1, col_p2, col_p3, col_p4, col_p5 = st.columns(5)
                        with col_p1:
                            st.markdown(f'<p class="caption-white">Attendance: <b>{disp_att:.1f}/4.0</b></p>', unsafe_allow_html=True)
                            st.progress(compute_safe_progress(r_att, 4.0))
                        with col_p2:
                            st.markdown(f'<p class="caption-white">Assignments: <b>{disp_hw:.1f}/10.0</b></p>', unsafe_allow_html=True)
                            st.progress(compute_safe_progress(r_hw, 10.0))
                        with col_p3:
                            st.markdown(f'<p class="caption-white">Mid-Term: <b>{disp_mid:.1f}/10.0</b></p>', unsafe_allow_html=True)
                            st.progress(compute_safe_progress(r_mid, 10.0))
                        with col_p4:
                            st.markdown(f'<p class="caption-white">Final Term: <b>{disp_final:.1f}/10.0</b></p>', unsafe_allow_html=True)
                            st.progress(compute_safe_progress(r_final, 10.0))
                        with col_p5:
                            st.markdown(f'<p class="caption-white">Tutorial: <b>{disp_ot:.1f}/6.0</b></p>', unsafe_allow_html=True)
                            st.progress(compute_safe_progress(r_ot, 6.0))

                        st.write("") 
                        
                        # 🔬 PRACTICAL PORTFOLIO VISUAL BLOCKS
                        st.markdown("#### 🧪 Practical Labs Breakdown")
                        
                        # 🔄 Evaluate Practical Component Gates Independently
                        is_prac_eligible = (p_pct >= 70.0) and (p_total >= 10.0)
                        p_status_text = "🟢 QUALIFIED" if is_prac_eligible else "🔴 NOT QUALIFIED (NQ)"
                        
                        col_p_a, col_p_b, col_p_c = st.columns([1, 1, 2])
                        with col_p_a:
                            fig_out_p = f"{p_total:.0f}" if is_prac_eligible else "NQ"
                            st.metric("Practical Lab Score", f"{fig_out_p} / 25")
                        with col_p_b:
                            st.metric("Lab Attendance Rate", f"{p_pct:.1f}%", f"{att_present_p}/{att_total_p} Labs")
                        with col_p_c:
                            st.write("")
                            if is_prac_eligible:
                                st.success(f"Lab Standing Status: {p_status_text}")
                            else:
                                st.error(f"Lab Standing Status: {p_status_text}")

                        r_p_att = (att_present_p / att_total_p) * 5.0 if att_total_p > 0 else 0.0
                        r_p_perf = (perf_raw_p / cfg_max_perf) * 5.0
                        r_p_rep = (report_raw_p / cfg_max_report) * 5.0
                        r_p_tst = (test_raw_p / cfg_max_test) * 5.0
                        r_p_viv = (viva_raw_p / cfg_max_viva) * 5.0

                        col_pb1, col_pb2, col_pb3, col_pb4 = st.columns(4)
                        with col_pb1:
                            st.markdown(f'<p class="caption-white">Lab Performance: <b>{(r_p_att + r_p_perf):.1f}/5.0</b></p>', unsafe_allow_html=True)
                            st.progress(min(max((r_p_att + r_p_perf) / 5.0, 0.0), 1.0))
                        with col_pb2:
                            st.markdown(f'<p class="caption-white">Lab Reports: <b>{r_p_rep:.1f}/5.0</b></p>', unsafe_allow_html=True)
                            st.progress(min(max(r_p_rep / 5.0, 0.0), 1.0))
                        with col_pb3:
                            st.markdown(f'<p class="caption-white">Viva/Quiz: <b>{r_p_viv:.1f}/5.0</b></p>', unsafe_allow_html=True)
                            st.progress(min(max(r_p_viv / 5.0, 0.0), 1.0))
                        with col_pb4:
                            st.markdown(f'<p class="caption-white">Practical Test: <b>{r_p_tst:.1f}/5.0</b></p>', unsafe_allow_html=True)
                            st.progress(min(max(r_p_tst / 5.0, 0.0), 1.0))
                    except Exception as loop_error:
                        st.error(f"Error parsing metrics for {sub['name']}: {str(loop_error)}")

        # ===================================================================
        # 📑 BUG-FREE CHRONOLOGICAL ASSIGNMENT UPLOAD HISTORY LOG
        # ===================================================================
        st.write("")
        st.divider()
        st.subheader("📑 Chronological Assignment Upload History")
        
        # FIXED SQL: COALESCE forces empty database text strings into absolute clean NULLs
        query_assignments = """
        SELECT s.name as Subject, a.title as Assignment, a.deadline as Deadline, 
               NULLIF(sub.marks, '') as Marks, 
               NULLIF(sub.submission_time, '') as Submitted_On
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
                
                # 🛡️ BULLETPROOF DETECTION: If they are locked out by the deadline, Submitted_On will be completely missing (None/NaN)
                is_submitted = pd.notna(row['Submitted_On']) and str(row['Submitted_On']).strip() != "None" and str(row['Submitted_On']).strip() != ""
                
                if is_submitted:
                    # 📤 Case 1: Student HAS turned in the assignment
                    sub_time_str = str(row['Submitted_On'])
                    
                    if "[LATE-10%]" in sub_time_str:
                        status = "⚠️ Submitted Late (-10%)"
                        score = f"{float(raw_marks):.1f}/10" if has_marks else "⏳ Pending (-10% Penalty)"
                    elif "[LATE-50%]" in sub_time_str:
                        status = "🚨 Submitted Late (-50%)"
                        score = f"{float(raw_marks):.1f}/10" if has_marks else "⏳ Pending (-50% Penalty)"
                    else:
                        status = "📤 Submitted"
                        score = f"{float(raw_marks):.1f}/10" if has_marks else "⏳ Pending"
                else:
                    # ❌ Case 2: Student HAS NOT submitted anything
                    if current_date > deadline_date:
                        # ⏱️ Check how many hours have passed since the midnight deadline to see if it passed 48h
                        today_dt = datetime.now(NST)
                        deadline_dt = datetime.combine(deadline_date, datetime.min.time()).replace(tzinfo=NST)
                        hours_late = (today_dt - deadline_dt).total_seconds() / 3600.0
                        
                        if hours_late > 48.0:
                            status = "❌ Unsubmitted (Expired)"
                        else:
                            status = "❌ Unsubmitted"
                        score = "N/A"
                    else:
                        status = "📖 Open"
                        score = "⏳ Awaiting Upload"

                display_data.append({
                    "Subject": row['Subject'], 
                    "Assignment": row['Assignment'],
                    "Deadline": row['Deadline'], 
                    "Status": status, 
                    "Marks": score
                })
            
            # Render a fresh clean table layout matching the state updates perfectly
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
