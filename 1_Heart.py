import os
from datetime import datetime
import pandas as pd
import streamlit as st
import requests
import matplotlib.pyplot as plt
from fpdf import FPDF

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

        # Send to FastAPI backend
        response = requests.post(
            f"http://127.0.0.1:8000/predict-heart?model_name={selected_model}",
            json=input_dict
        )
        result = response.json()

        if "error" in result:
            st.error(f"❌ Prediction failed: {result['error']}")
        else:
            prediction = result["prediction"]
            proba = result["probability"] / 100  # Convert to 0–1

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
