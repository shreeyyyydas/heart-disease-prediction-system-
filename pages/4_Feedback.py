import streamlit as st
import pandas as pd
import os
import sqlite3
from datetime import datetime

st.set_page_config(page_title="Feedback Form", page_icon="📝")
st.title("📝 Feedback Form")

# --- Feedback Form UI ---
with st.form("feedback_form"):
    name = st.text_input("Your Name")
    mobile = st.text_input("Mobile Number")
    age = st.text_input("Your Age")
    email = st.text_input("Email ID (Optional)")
    state = st.text_input("State")
    district = st.text_input("District")
    rating = st.slider("How accurate/trustworthy was the prediction?", 1, 5)
    technical_issues = st.text_area("Did you encounter any technical issues? If yes, please describe.")
    comments = st.text_area("Additional comments or suggestions")

    submit_button = st.form_submit_button("Submit Feedback")

# --- Handle Feedback Submission ---
if submit_button:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Save to SQLite database
    try:
        conn = sqlite3.connect("patients_data.db")
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT, mobile TEXT, age TEXT, email TEXT,
                state TEXT, district TEXT, rating INTEGER,
                technical_issues TEXT, comments TEXT,
                timestamp TEXT
            )
        ''')

        cursor.execute('''
            INSERT INTO feedback (
                name, mobile, age, email, state, district,
                rating, technical_issues, comments, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            name, mobile, age, email, state, district,
            rating, technical_issues, comments, timestamp
        ))

        conn.commit()
        conn.close()
        st.success("✅ Thank you! Your feedback has been recorded.")
    except Exception as e:
        st.error(f"❌ Failed to save feedback: {e}")