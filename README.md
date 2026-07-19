# ❤️ Heart Disease Prediction System

A complete **Machine Learning–based Heart Disease Prediction application** built using **FastAPI** for the backend and **Streamlit** for the frontend.  
The project predicts the likelihood of heart disease based on patient health parameters and provides an easy-to-use web interface.

---

## 📌 Project Overview

Heart disease is one of the leading causes of death worldwide.  
This project aims to assist in **early risk assessment** by using trained ML models to predict whether a person is likely to have heart disease based on clinical attributes.

The system includes:
- A **FastAPI backend** for model inference
- A **Streamlit frontend** for user interaction
- Trained **Machine Learning models**
- Clean project structure suitable for **internships and interviews**

---

## 🛠️ Tech Stack

- **Programming Language:** Python 3.11  
- **Backend:** FastAPI, Uvicorn  
- **Frontend:** Streamlit  
- **Machine Learning:** Scikit-learn  
- **Data Handling:** Pandas, NumPy  
- **Visualization:** Matplotlib, Seaborn  
- **Version Control:** Git, GitHub  

---

## 📂 Project Structure

```python
INTERNSHIP_PROJECT/
│
├── .venv/
│
├── pages/
│   ├── 2_Fitness.py
│   ├── 3_Attributes_Restrictions.py
│   ├── 4_Feedback.py
│   └── 5_Admin.py
│
├── reports/
│   └── heart_report_20250703_232032.pdf
│
├── .env
├── 1_Heart.py
├── app.py
├── main.py
├── requirements.txt
│
├── HDPrj.ipynb
├── heart1.csv
├── patients_data.db
│
├── fitness_model.joblib
├── logistic_model.pkl
├── random_forest_model.pkl
├── svm_model.pkl
├── scaler.pkl
├── model_columns.pkl
│
├── le_alcohol.joblib
├── le_diet.joblib
├── le_smoking.joblib
│
└── risk_chart.png

```
---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository
```python
git clone https://github.com/Mohnish4246/heart-disease-prediction.git
cd heart-disease-prediction
```
### 2️⃣ Create Virtual Environment (Python 3.11)
```python
py -3.11 -m venv .venv
```
> Activate the environment:
> Windows
```python
.venv\Scripts\activate
```
### 3️⃣ Install Dependencies
```python
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```
### Start FastAPI Backend
```python
python -m uvicorn main:app --reload
```
#### API will be available : Click on the link
### Start Streamlit Frontend
```python
streamlit run 1_Heart.py
```
### Machine Learning Models Used
* Logistic Regression
* Support Vector Machine (SVM)
* Random Forest Classifier

> Models were trained, evaluated, and saved using Scikit-learn.
> Feature scaling and categorical encoding are handled using saved encoders and scalers.

### Features
* User-friendly Streamlit interface
* Real-time heart disease prediction
* Probability-based prediction output
* Modular project structure
* Ready for deployment and further extension
### Future Enhancements
* User authentication
* Database integration for storing predictions
* Model performance comparison dashboard
### Author
#### Mohnish Sharma
#### Python | Machine Learning | FastAPI | Streamlit
### Acknowledgements
* Scikit-learn documentation
* FastAPI & Streamlit community
* Open-source ML resources
### License
**This project is for educational and internship purposes.**
