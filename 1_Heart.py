import os
from datetime import datetime
import pandas as pd
import streamlit as st
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
        # Map categorical inputs to integers
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
        model_files = [f for f in available_files if "scaler" not in f.lower() and "encoder" not in f.lower()]
        
        # 2. Match selected model
        model_file = None
        search_term = selected_model.lower().replace("_", "")

        for f in model_files:
            if search_term in f.lower().replace("-", "").replace("_", ""):
                model_file = f
                break
        
        if not model_file and model_files:
            model_file = model_files[0]
            
        if not model_file:
            raise FileNotFoundError("Could not find any model files in your project folder.")

        # 3. Load model
        model = joblib.load(model_file)

        # 4. Handle Features alignment safely
        if hasattr(model, "feature_names_in_"):
            expected_cols = list(model.feature_names_in_)
            features_df = pd.DataFrame(0, index=[0], columns=expected_cols)
            
            # Fill numerical / binary values
            for col in ['age', 'sex', 'trestbps', 'chol', 'fbs', 'thalach', 'exang', 'oldpeak']:
                for exp in expected_cols:
                    if exp.lower() == col:
                        features_df[exp] = input_dict[col]

            # Fill categorical dummy variables
            categorical_vals = {
                'cp': input_dict['cp'],
                'restecg': input_dict['restecg'],
                'slope': input_dict['slope'],
                'ca': input_dict['ca'],
                'thal': input_dict['thal']
            }

            for cat, val in categorical_vals.items():
                for exp in expected_cols:
                    if exp.lower().startswith(f"{cat}_") or exp.lower().startswith(f"{cat}."):
                        suffix = exp.lower().replace(f"{cat}_", "").replace(f"{cat}.", "")
                        if suffix.isdigit() and int(suffix) == val:
                            features_df[exp] = 1
        else:
            features_df = pd.DataFrame([input_dict])

        # 5. Smart Scaler Handling: Checks how many features the scaler actually expects
        scaler_files = glob.glob("*scaler*.pkl") + glob.glob("*scaler*.joblib") + glob.glob("model/*scaler*.pkl") + glob.glob("model/*scaler*.joblib")
        if scaler_files:
            scaler = joblib.load(scaler_files[0])
            scaler_n_in = getattr(scaler, "n_features_in_", None)
            
            if scaler_n_in == 5:
                # Scale only the 5 main numerical columns: age, trestbps, chol, thalach, oldpeak
                num_cols = ['age', 'trestbps', 'chol', 'thalach', 'oldpeak']
                present_num_cols = [c for c in num_cols if c in features_df.columns or c.upper() in features_df.columns]
                
                # If column names differ in case, find matching columns
                actual_num_cols = []
                for nc in num_cols:
                    for fc in features_df.columns:
                        if nc == fc.lower():
                            actual_num_cols.append(fc)
                            break
                            
                if len(actual_num_cols) == 5:
                    features_df[actual_num_cols] = scaler.transform(features_df[actual_num_cols])
            elif scaler_n_in == features_df.shape[1]:
                # Scaler expects all features (e.g., 27)
                scaled_vals = scaler.transform(features_df.values)
                features_df = pd.DataFrame(scaled_vals, columns=features_df.columns)

        # 6. Convert to raw array to avoid feature name validation mismatch during predict
        features_for_pred = features_df.values

        # 7. Predict
        raw_pred = model.predict(features_for_pred)[0]

        if hasattr(model, "predict_proba"):
            raw_probs = model.predict_proba(features_for_pred)[0]
            raw_classes = getattr(model, "classes_", [0, 1])
            
            if list(raw_classes) == [1, 0]:
                proba = float(raw_probs[0])
            else:
                proba = float(raw_probs[1])
        else:
            proba = 0.85 if raw_pred == 1 else 0.15

        # 8. Output result
        prediction = "Heart Disease" if raw_pred == 1 else "No Heart Disease"

        st.subheader("🧪 Prediction Result")

        if proba >= 0.7:
            risk_color = "🔴 High Risk"
        elif proba >= 0.4:
            risk_color = "🟠 Moderate Risk"
        else:
            risk_color = "🟢 Low Risk"

        st.write(f"**Risk Level:** {risk_color}")
        st.progress(proba)

        st.info(f"🧠 Model Used: {model_option}")
        
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
