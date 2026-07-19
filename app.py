import os
import sqlite3
import pandas as pd
import numpy as np
import joblib
import base64
import matplotlib.pyplot as plt
from datetime import datetime
from fpdf import FPDF
import streamlit as st

# Load models and encoders
model = joblib.load('models/logistic_model.pkl')
scaler = joblib.load('models/scaler.pkl')
model_columns = joblib.load('models/model_columns.pkl')

# Page config
st.set_page_config(page_title="Heart Disease Predictor", layout="wide")
st.title("🔮 Heart Disease Prediction")

# Input columns
col1, col2 = st.columns(2)
with col1:
    age = st.number_input("Age", 29, 77, step=1)
    sex = st.selectbox("Sex", ["Male", "Female"])
    cp = st.selectbox("Chest Pain Type", ["Typical Angina", "Atypical Angina", "Non-anginal Pain", "Asymptomatic"])
    trestbps = st.number_input("Resting BP", 80, 200)
    chol = st.number_input("Cholesterol", 100, 600)
    fbs = st.selectbox("Fasting Sugar > 120", ["Yes", "No"])

with col2:
    restecg = st.selectbox("Resting ECG", ["Normal", "ST-T abnormality", "Left ventricular hypertrophy"])
    thalach = st.number_input("Max Heart Rate", 60, 220)
    exang = st.selectbox("Exercise Induced Angina", ["Yes", "No"])
    oldpeak = st.number_input("ST Depression", 0.0, 6.0)
    slope = st.selectbox("Slope", ["Upsloping", "Flat", "Downsloping"])
    ca = st.selectbox("Number of vessels (0–3)", [0, 1, 2, 3])
    thal = st.selectbox("Thalassemia", ["Normal", "Fixed Defect", "Reversible Defect"])

cp_map = {"Typical Angina": 0, "Atypical Angina": 1, "Non-anginal Pain": 2, "Asymptomatic": 3}
restecg_map = {"Normal": 0, "ST-T abnormality": 1, "Left ventricular hypertrophy": 2}
slope_map = {"Upsloping": 0, "Flat": 1, "Downsloping": 2}
thal_map = {"Normal": 1, "Fixed Defect": 2, "Reversible Defect": 3}

if st.button("🔍 Predict"):
    try:
        user_data = {
            'age': age,
            'sex': 1 if sex == "Male" else 0,
            'cp': cp_map[cp],
            'trestbps': trestbps,
            'chol': chol,
            'fbs': 1 if fbs == "Yes" else 0,
            'restecg': restecg_map[restecg],
            'thalach': thalach,
            'exang': 1 if exang == "Yes" else 0,
            'oldpeak': oldpeak,
            'slope': slope_map[slope],
            'ca': ca,
            'thal': thal_map[thal]
        }

        df = pd.DataFrame([user_data])
        df_scaled = df.copy()
        df_scaled[['age', 'trestbps', 'chol', 'thalach', 'oldpeak']] = scaler.transform(
            df_scaled[['age', 'trestbps', 'chol', 'thalach', 'oldpeak']])
        df_scaled = pd.get_dummies(df_scaled)
        df_scaled = df_scaled.reindex(columns=model_columns, fill_value=0)

        prediction = model.predict(df_scaled)[0]
        prob = model.predict_proba(df_scaled)[0][prediction]

        result = "Heart Disease" if prediction == 1 else "No Heart Disease"

        if prediction == 1:
            st.error(f"💔 You are likely to HAVE heart disease. Confidence: {prob*100:.2f}%")
        else:
            st.success(f"💚 You are NOT likely to have heart disease. Confidence: {prob*100:.2f}%")
            st.balloons()

        # Store in SQLite
        conn = sqlite3.connect("patients_data.db")
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS heart_patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                age REAL, sex REAL, cp REAL, trestbps REAL, chol REAL,
                fbs REAL, restecg REAL, thalach REAL, exang REAL,
                oldpeak REAL, slope REAL, ca REAL, thal REAL,
                prediction TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            INSERT INTO heart_patients (age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang,
            oldpeak, slope, ca, thal, prediction) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                user_data['age'], user_data['sex'], user_data['cp'], user_data['trestbps'],
                user_data['chol'], user_data['fbs'], user_data['restecg'], user_data['thalach'],
                user_data['exang'], user_data['oldpeak'], user_data['slope'], user_data['ca'],
                user_data['thal'], result
            )
        )
        conn.commit()
        conn.close()

        # PDF generation
        st.markdown("---")
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "Heart Disease Prediction Report", ln=True, align='C')
        pdf.ln(10)

        for k, v in user_data.items():
            pdf.set_font("Arial", '', 12)
            pdf.cell(0, 10, f"{k}: {v}", ln=True)

        pdf.ln(5)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, f"Prediction: {result} ({prob*100:.2f}% confidence)", ln=True)

        if not os.path.exists("reports"):
            os.makedirs("reports")

        filename = f"reports/heart_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf.output(filename)

        with open(filename, "rb") as f:
            st.download_button("📄 Download PDF Report", f, file_name=os.path.basename(filename), mime="application/pdf")

        # Feedback button
        if st.button("📝 Give Feedback"):
            st.switch_page("pages/3_Feedback.py")

    except Exception as e:
        st.error(f"Error: {e}")