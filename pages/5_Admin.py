import streamlit as st
import sqlite3
import pandas as pd
import os
from dotenv import load_dotenv

st.set_page_config(page_title="🔐 Admin Panel", layout="wide")
st.title("🔐 Admin Dashboard")

# Load .env variables
ADMIN_USERNAME = "hehe"
ADMIN_PASSWORD = "181284"

# Sidebar login form
st.sidebar.header("🔐 Admin Login")
admin_username = st.sidebar.text_input("Username")
admin_password = st.sidebar.text_input("Password", type="password")
login_btn = st.sidebar.button("Login")

# Check credentials securely
if login_btn:
    if admin_username == ADMIN_USERNAME and admin_password == ADMIN_PASSWORD:
        st.session_state["admin_logged_in"] = True
        st.sidebar.success("🛡️ Logged in as admin")
    else:
        st.sidebar.error("❌ Invalid credentials")

# Force a page rerun immediately upon button click to show tables instantly
if login_btn and st.session_state.get("admin_logged_in", False):
    st.rerun()
if st.session_state.get("admin_logged_in", False):
    st.success("Welcome Admin! Use the sections below to view data:")

    # Connect to SQLite database
    conn = sqlite3.connect("patients_data.db")

    # === Feedback table ===
    st.subheader("📝 Feedback Submissions")
    feedback_df = pd.read_sql_query("SELECT * FROM feedback", conn)
    st.dataframe(feedback_df, use_container_width=True)

    # === Heart prediction records ===
    st.subheader("❤️ Heart Disease Prediction Records")
    heart_df = pd.read_sql_query("SELECT * FROM heart_patients", conn)

    # Human-readable mappings
    sex_map = {0: "Female", 1: "Male"}
    fbs_map = {0: "No", 1: "Yes"}
    exang_map = {0: "No", 1: "Yes"}
    cp_map = {0: "Typical Angina", 1: "Atypical Angina", 2: "Non-anginal Pain", 3: "Asymptomatic"}
    restecg_map = {0: "Normal", 1: "ST-T abnormality", 2: "LV Hypertrophy"}
    slope_map = {0: "Upsloping", 1: "Flat", 2: "Downsloping"}
    thal_map = {0: "Unknown", 1: "Normal", 2: "Fixed Defect", 3: "Reversible Defect"}

    # Apply maps
    if not heart_df.empty:
        heart_df["sex"] = heart_df["sex"].map(sex_map)
        heart_df["fbs"] = heart_df["fbs"].map(fbs_map)
        heart_df["exang"] = heart_df["exang"].map(exang_map)
        heart_df["cp"] = heart_df["cp"].map(cp_map)
        heart_df["restecg"] = heart_df["restecg"].map(restecg_map)
        heart_df["slope"] = heart_df["slope"].map(slope_map)
        heart_df["thal"] = heart_df["thal"].map(thal_map)

    st.dataframe(heart_df, use_container_width=True)

    # === Fitness prediction records ===
    st.subheader("🏋️ Fitness Prediction Records")
    fitness_df = pd.read_sql_query("SELECT * FROM fitness_patients", conn)
    st.dataframe(fitness_df, use_container_width=True)

    conn.close()

else:
    st.warning("🔐 Please login as admin using the sidebar to view the data.")


# import streamlit as st
# import sqlite3
# import pandas as pd
# import os
# from dotenv import load_dotenv

# st.set_page_config(page_title="🔐 Admin Panel", layout="wide")
# st.title("🔐 Admin Dashboard")

# # Load .env variables
# load_dotenv()
# ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
# ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

# # Sidebar login form
# st.sidebar.header("🔐 Admin Login")
# admin_username = st.sidebar.text_input("Username")
# admin_password = st.sidebar.text_input("Password", type="password")
# login_btn = st.sidebar.button("Login")

# # Check credentials
# if login_btn:
#     if admin_username == ADMIN_USERNAME and admin_password == ADMIN_PASSWORD:
#         st.session_state["admin_logged_in"] = True
#         st.sidebar.success("🛡️ Logged in as admin")
#     else:
#         st.sidebar.error("❌ Invalid credentials")

# # If logged in
# if st.session_state.get("admin_logged_in", False):
#     st.success("Welcome Admin! Use the sections below to view data:")

#     # Connect to SQLite database
#     conn = sqlite3.connect("patients_data.db")

#     # Feedback table
#     st.subheader("📝 Feedback Submissions")
#     feedback_df = pd.read_sql_query("SELECT * FROM feedback", conn)
#     st.dataframe(feedback_df)

#     # Heart prediction records
#     st.subheader("❤️ Heart Disease Prediction Records")
#     heart_df = pd.read_sql_query("SELECT * FROM heart_patients", conn)
#     st.dataframe(heart_df)

#     # Fitness prediction records
#     st.subheader("🏋️ Fitness Prediction Records")
#     fitness_df = pd.read_sql_query("SELECT * FROM fitness_patients", conn)
#     st.dataframe(fitness_df)

#     conn.close()

# else:
#     st.warning("🔐 Please login as admin using the sidebar to view the data.")
