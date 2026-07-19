import streamlit as st
import joblib
import sqlite3
import pandas as pd

# Load the model and encoders
model = joblib.load("fitness_model.joblib")
le_diet = joblib.load("le_diet.joblib")
le_smoking = joblib.load("le_smoking.joblib")
le_alcohol = joblib.load("le_alcohol.joblib")

st.title("🏋️ Fitness Prediction")
st.markdown("###  Please enter your health and lifestyle details")

# User input fields
age = st.number_input("🎂 Age", min_value=10, max_value=100, step=1)
weight = st.number_input("⚖️ Weight (kg)", min_value=20.0, max_value=200.0, step=0.5)
height = st.number_input("📏 Height (cm)", min_value=100.0, max_value=250.0, step=0.5)
exercise_days = st.slider("🏃‍♂️ Exercise Days per Week", 0, 7, 3)
sleep_hours = st.slider("💤 Sleep Hours per Night", 0, 12, 7)
diet = st.selectbox("🥗 Diet Preference", ["Vegetarian", "Non-Vegetarian", "Vegan", "Junk Food Often"])
smoking = st.radio("🚬 Do You Smoke?", ["No", "Sometimes", "Regularly"])
alcohol = st.radio("🍷 Alcohol Consumption?", ["Never", "Occasionally", "Frequently"])

if st.button("🔍 Check Fitness Status"):
    # Encode inputs
    diet_enc = le_diet.transform([diet])[0]
    smoking_enc = le_smoking.transform([smoking])[0]
    alcohol_enc = le_alcohol.transform([alcohol])[0]

    input_data = pd.DataFrame({
        'age': [age],
        'weight': [weight],
        'height': [height],
        'exercise_days': [exercise_days],
        'sleep_hours': [sleep_hours],
        'diet_enc': [diet_enc],
        'smoking_enc': [smoking_enc],
        'alcohol_enc': [alcohol_enc]
    })

    prediction = model.predict(input_data)[0]
    prob = model.predict_proba(input_data)[0][prediction]

    if prediction == 1:
        st.success(f"✅ You are Fit! (Confidence: {prob*100:.2f}%) 💪")
        result_text = "Fit"
    else:
        st.error(f"❌ You need to focus on your fitness! (Confidence: {prob*100:.2f}%) 🏃‍♀️")
        result_text = "Not Fit"

    try:
        conn = sqlite3.connect("patients_data.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO fitness_patients 
            (age, weight, height, exercise_days, sleep_hours, diet, smoking, alcohol, prediction)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (age, weight, height, exercise_days, sleep_hours, diet, smoking, alcohol, result_text))
        conn.commit()
        conn.close()
        st.info("📁 Your data has been saved successfully.")
    except Exception as e:
        st.warning(f"⚠️ Failed to save data: {e}")