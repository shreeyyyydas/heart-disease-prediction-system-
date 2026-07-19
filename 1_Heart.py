import os
from datetime import datetime
import pandas as pd
import streamlit as st
import requests
import matplotlib.pyplot as plt
from fpdf import FPDF
import joblib
import numpy as np
import glob

# Page setup
st.set_page_config(page_title="Heart Disease Prediction", layout="wide")
st.title("❤️ Heart Disease Prediction")
st.markdown("""
Welcome to the **Heart Disease Prediction System**.  
This tool helps you estimate the risk of heart disease based on medically relevant parameters.  
👉 Fill in the required details about the patient, choose the model you want to use for prediction, and click **Predict**.  
💡 After prediction, you will get a visual result, risk level, and the option to download a PDF report for reference.

**Note**: This is a machine learning-based prediction and is not a substitute for medical advice. Always consult a doctor for diagnosis and treatment.
""")

st.markdown("### 🔧 Choose Prediction Model")
model_option = st.selectbox(
    "Select Model to Use:",
    ("Logistic Regression", "SVM", "Random Forest")
)

# Map dropdown value to backend model name
model_name_map = {
    "Logistic Regression": "logistic",
    "SVM": "svm",
    "Random Forest": "random_forest"
}
selected_model = model_name_map[model_option]

# Input form
with st.form("heart_form"):
    st.subheader("📝 Enter Patient Details")
    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input("Age", 29, 77)
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
        ca = st.selectbox("No. of vessels", [0, 1, 2, 3])
        thal = st.selectbox("Thalassemia", ["Normal", "Fixed Defect", "Reversible Defect"])

    submitted = st.form_submit_button("🔮 Predict")

# On form submit
if submitted:
    try:
        # Map categorical inputs
        mappings = {
            "cp": {"Typical Angina": 0, "Atypical Angina": 1, "Non-anginal Pain": 2, "Asymptomatic": 3},
            "restecg": {"Normal": 0, "ST-T abnormality": 1, "Left ventricular hypertrophy": 2},
            "slope": {"Upsloping": 0, "Flat": 1, "Downsloping": 2},
            "thal": {"Normal": 1, "Fixed Defect": 2, "Reversible Defect": 3}
        }

        input_dict = {
            'age': age,
            'sex': 1 if sex == "Male" else 0,
            'cp': mappings['cp'][cp],
            'trestbps': trestbps,
            'chol': chol,
            'fbs': 1 if fbs == "Yes" else 0,
            'restecg': mappings['restecg'][restecg],
            'thalach': thalach,
            'exang': 1 if exang == "Yes" else 0,
            'oldpeak': oldpeak,
            'slope': mappings['slope'][slope],
            'ca': ca,
            'thal': mappings['thal'][thal]
        }

        # 1. Scan directory for matching model files (.pkl or .joblib)
        available_files = glob.glob("*.pkl") + glob.glob("*.joblib") + glob.glob("model/*.pkl") + glob.glob("model/*.joblib")
        
        # 2. Match selected model to available files
        model_file = None
        search_term = selected_model.lower().replace("_", "") # e.g., 'randomforest', 'logistic', 'svm'

        for f in available_files:
            if search_term in f.lower().replace("-", "").replace("_", ""):
                model_file = f
                break
        
        # Fallback: pick first available model if explicit match fails
        if not model_file and available_files:
            model_file = available_files[0]
            
        if not model_file:
            raise FileNotFoundError("Could not find any .pkl or .joblib model files in your project folder.")

        # 3. Load model
        model = joblib.load(model_file)

        # 4. Format inputs into a pandas DataFrame (preserves feature names for accuracy)
        features = pd.DataFrame([input_dict])

        # 5. Dynamic alignment if model expects encoded feature columns
        if hasattr(model, "feature_names_in_"):
            missing_cols = set(model.feature_names_in_) - set(features.columns)
            for c in missing_cols:
                features[c] = 0
            features = features[model.feature_names_in_]

        # 6. Make prediction
        raw_pred = model.predict(features)[0]

        # Debugging Output to pinpoint the issue
        raw_classes = getattr(model, "classes_", "No classes attribute")
        st.write(f"🔍 **Debug Info - Raw Prediction:** `{raw_pred}`")
        st.write(f"🔍 **Debug Info - Model Classes:** `{raw_classes}`")
        if hasattr(model, "predict_proba"):
            raw_probs = model.predict_proba(features)[0]
            st.write(f"🔍 **Debug Info - Raw Probabilities:** `{raw_probs}`")

        # Handle class mapping accurately
        if hasattr(model, "predict_proba"):
            # Check if class 1 is at index 1 or index 0
            if list(raw_classes) == [1, 0]:
                proba = float(raw_probs[0])
            else:
                proba = float(raw_probs[1])
        else:
            proba = 0.85 if raw_pred == 1 else 0.15

        prediction = "Heart Disease" if raw_pred == 1 else "No Heart Disease"

        # Show confidence as progress bar
        st.subheader("🧪 Prediction Result")

        # Color-coded risk badge
        if proba >= 0.7:
            risk_color = "🔴 High Risk"
        elif proba >= 0.4:
            risk_color = "🟠 Moderate Risk"
        else:
            risk_color = "🟢 Low Risk"

        st.write(f"**Risk Level:** {risk_color}")
        st.progress(proba)

        st.info(f"🧠 Model Used: {model_option}")
        
        # Show prediction
        if prediction == "Heart Disease":
            st.error(f"💔 Likely to HAVE heart disease. (Confidence: {proba*100:.2f}%)")
        else:
            st.success(f"💚 NOT likely to have heart disease. (Confidence: {proba*100:.2f}%)")
            st.balloons()

        st.markdown("---")
        st.subheader("ℹ️ About This Result")
        st.markdown("""
        The prediction is based on the input parameters you provided.  
        It uses a trained **machine learning model** to estimate your **likelihood of having heart disease**.  
        Interpret the result with care, and consult a healthcare professional if needed.
        """)

        # Generate chart
        def generate_chart(p):
            fig, ax = plt.subplots(figsize=(5, 1))
            ax.barh(["Risk"], [p * 100], color='red' if p > 0.7 else 'orange' if p > 0.4 else 'green')
            ax.set_xlim(0, 100)
            ax.set_xlabel("%")
            ax.set_title("Risk Estimate")
            for spine in ax.spines.values():
                spine.set_visible(False)
            plt.tight_layout()
            plt.savefig("risk_chart.png")
            plt.close()

        generate_chart(proba)

        # Generate PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "Heart Disease Report", ln=True, align="C")
        pdf.ln(10)
        pdf.set_font("Arial", '', 12)
        for k, v in input_dict.items():
            pdf.cell(0, 10, f"{k.capitalize()}: {v}", ln=True)
        pdf.ln(5)
        pdf.cell(0, 10, f"Model Used: {model_option}", ln=True)
        pdf.multi_cell(0, 10, f"Prediction: You are predicted to {'NOT ' if prediction == 'No Heart Disease' else ''}have heart disease with {proba*100:.2f}% confidence.", border=1)
        pdf.image("risk_chart.png", x=10, w=pdf.w - 20)

        filename = f"heart_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join("reports", filename)
        os.makedirs("reports", exist_ok=True)
        pdf.output(filepath)

        with open(filepath, "rb") as f:
            st.download_button("📄 Download PDF Report", f, file_name=filename, mime="application/pdf")

    except Exception as e:
        st.error(f"Error: {e}")

if st.button("🗣️ Give Feedback"):
    st.switch_page("pages/4_Feedback.py")
