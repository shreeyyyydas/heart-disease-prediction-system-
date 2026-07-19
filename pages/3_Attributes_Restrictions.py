import streamlit as st

st.set_page_config(page_title="📊 Input Column Guide", layout="wide")
st.title("📊 Heart Disease Prediction – Detailed Column Guide")

st.markdown("""
<style>
    .desc-table th, .desc-table td {
        padding: 8px 12px;
        border: 1px solid #ddd;
        vertical-align: top;
    }
    .desc-table th {
        background-color: #f0f0f0;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
### 🩺 What Do These Columns Mean?

Each value you enter helps predict the risk of heart disease. Here's a breakdown of each input, in simple terms.

<table class="desc-table">
<thead>
<tr>
<th>Column</th>
<th>Description (Layman Terms)</th>
<th>Allowed Values / Range</th>
</tr>
</thead>
<tbody>

<tr>
<td><b>age</b></td>
<td>How old is the patient?</td>
<td>29 to 77 years</td>
</tr>

<tr>
<td><b>sex</b></td>
<td>Patient's gender.</td>
<td>0 = Female<br>1 = Male</td>
</tr>

<tr>
<td><b>cp</b> <br>(Chest Pain Type)</td>
<td>What kind of chest pain the patient has.<br><i>This helps identify if the pain is heart-related.</i></td>
<td>
0 = Typical Angina (exertion related)<br>
1 = Atypical Angina (not exertion related)<br>
2 = Non-anginal Pain (not heart related)<br>
3 = Asymptomatic (no pain but disease may be present)
</td>
</tr>

<tr>
<td><b>trestbps</b> <br>(Resting Blood Pressure)</td>
<td>Blood pressure when at rest.<br><i>Measured in mm Hg (millimeters of mercury).</i><br>High values may indicate stress on the heart.</td>
<td>80 to 200 mm Hg</td>
</tr>

<tr>
<td><b>chol</b> <br>(Cholesterol)</td>
<td>Amount of cholesterol in the blood.<br><i>Measured in mg/dl (milligrams per deciliter).</i><br>Higher values can increase heart risk.</td>
<td>100 to 600 mg/dl</td>
</tr>

<tr>
<td><b>fbs</b> <br>(Fasting Blood Sugar)</td>
<td>Is blood sugar level above 120 after fasting?<br><i>High fasting sugar = risk of diabetes & heart issues.</i></td>
<td>0 = No<br>1 = Yes</td>
</tr>

<tr>
<td><b>restecg</b> <br>(Resting ECG)</td>
<td>Electrocardiogram result taken at rest.<br><i>Shows how the heart is working electrically.</i></td>
<td>
0 = Normal<br>
1 = ST-T abnormality (possible problem)<br>
2 = Left Ventricular Hypertrophy (heart strain)
</td>
</tr>

<tr>
<td><b>thalach</b> <br>(Max Heart Rate)</td>
<td>Maximum heart rate during exercise.<br>Low values may suggest poor heart fitness.</td>
<td>60 to 220 bpm (beats per minute)</td>
</tr>

<tr>
<td><b>exang</b> <br>(Exercise Angina)</td>
<td>Does the patient have chest pain during exercise?</td>
<td>0 = No<br>1 = Yes</td>
</tr>

<tr>
<td><b>oldpeak</b></td>
<td>ST depression during exercise.<br><i>Represents how much the heart struggles during activity.</i></td>
<td>0.0 to 6.0</td>
</tr>

<tr>
<td><b>slope</b></td>
<td>Trend of ST segment in ECG during peak exercise.<br><i>Used to check how blood flows to the heart under stress.</i></td>
<td>
0 = Upsloping (better)<br>
1 = Flat (riskier)<br>
2 = Downsloping (most concerning)
</td>
</tr>

<tr>
<td><b>ca</b></td>
<td>No. of major blood vessels seen in X-ray with dye.<br>More vessels = better blood flow.</td>
<td>0 to 3 (integer)</td>
</tr>

<tr>
<td><b>thal</b></td>
<td>Blood flow result from thalassemia test.<br><i>Helps detect blockages or damaged tissue.</i></td>
<td>
1 = Normal<br>
2 = Fixed Defect (permanent damage)<br>
3 = Reversible Defect (shows under stress)
</td>
</tr>

<tr>
<td><b>target</b></td>
<td>Is heart disease present?</td>
<td>0 = No<br>1 = Yes</td>
</tr>

</tbody>
</table>

---

### 📘 Medical Terms Made Easy

- **mm Hg**: Unit used to measure blood pressure (millimeters of mercury).
- **mg/dl**: Measures concentration like sugar or cholesterol in your blood.
- **ECG**: Electrocardiogram, test that checks how your heart beats.
- **ST segment**: Part of ECG that shows how blood flows to your heart during activity.
- **Angina**: Chest pain due to reduced blood flow to the heart.

""", unsafe_allow_html=True)
