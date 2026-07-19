from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import joblib
import pandas as pd
import sqlite3
from datetime import datetime

# === FastAPI app ===
app = FastAPI()

# === Enable CORS ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Load models and encoders ===
heart_model = joblib.load("logistic_model.pkl")
scaler = joblib.load("scaler.pkl")
model_columns = joblib.load("model_columns.pkl")
svm_model = joblib.load("svm_model.pkl")
rf_model = joblib.load("random_forest_model.pkl")

fitness_model = joblib.load("fitness_model.joblib")
le_diet = joblib.load("le_diet.joblib")
le_smoking = joblib.load("le_smoking.joblib")
le_alcohol = joblib.load("le_alcohol.joblib")

# === Database setup ===
def init_db():
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
        CREATE TABLE IF NOT EXISTS fitness_patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            age REAL, weight REAL, height REAL, exercise_days INTEGER,
            sleep_hours REAL, diet TEXT, smoking TEXT, alcohol TEXT,
            prediction TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, mobile TEXT, age TEXT, email TEXT,
            state TEXT, district TEXT, rating INTEGER,
            technical_issues TEXT, comments TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()

init_db()

# === Pydantic models ===
class HeartInput(BaseModel):
    age: float
    sex: float
    cp: float
    trestbps: float
    chol: float
    fbs: float
    restecg: float
    thalach: float
    exang: float
    oldpeak: float
    slope: float
    ca: float
    thal: float

class FitnessInput(BaseModel):
    age: int
    weight: float
    height: float
    exercise_days: int
    sleep_hours: float
    diet: str
    smoking: str
    alcohol: str

class FeedbackInput(BaseModel):
    name: str
    mobile: str
    age: str
    email: str
    state: str
    district: str
    rating: int
    technical_issues: str
    comments: str

# === Routes ===
@app.get("/")
def home():
    return {"message": "Heart & Fitness Prediction API is live!"}

@app.post("/predict-heart")
def predict_heart(data: HeartInput, model_name: str = "logistic"):
    try:
        # Step 1: Convert input to DataFrame
        df = pd.DataFrame([data.dict()])

        # Step 2: One-hot encode categorical features (if any)
        df = pd.get_dummies(df)

        # Step 3: Add any missing columns
        missing_cols = set(model_columns) - set(df.columns)
        for col in missing_cols:
            df[col] = 0

        # Step 4: Match column order
        df = df[model_columns]

        # Step 5: Scale numeric columns
        num_cols = ['age', 'trestbps', 'chol', 'thalach', 'oldpeak']
        df[num_cols] = scaler.transform(df[num_cols])

        # Step 6: Predict probability and result
        if model_name == "logistic":
            proba = heart_model.predict_proba(df)[0][1]
        elif model_name == "svm":
            proba = svm_model.predict_proba(df)[0][1]
        elif model_name == "random_forest":
            proba = rf_model.predict_proba(df)[0][1]
        else:
            return {"error": "Invalid model_name. Use 'logistic', 'svm', or 'random_forest'."}

        result = "Heart Disease" if proba >= 0.4 else "No Heart Disease"
        probability_percent = round(proba * 100, 2)
        

        # Step 7: Save to DB
        conn = sqlite3.connect("patients_data.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO heart_patients (
                age, sex, cp, trestbps, chol, fbs, restecg,
                thalach, exang, oldpeak, slope, ca, thal, prediction
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.age, data.sex, data.cp, data.trestbps, data.chol,
            data.fbs, data.restecg, data.thalach, data.exang,
            data.oldpeak, data.slope, data.ca, data.thal,
            result
        ))
        conn.commit()
        conn.close()

        # Step 8: Return result
        return {
            "prediction": result,
            "probability": probability_percent
        }

    except Exception as e:
        return {"error": str(e)}

@app.post("/predict-fitness")
def predict_fitness(data: FitnessInput):
    try:
        diet_enc = le_diet.transform([data.diet])[0]
        smoking_enc = le_smoking.transform([data.smoking])[0]
        alcohol_enc = le_alcohol.transform([data.alcohol])[0]

        features = [[
            data.age, data.weight, data.height,
            data.exercise_days, data.sleep_hours,
            diet_enc, smoking_enc, alcohol_enc
        ]]

        prediction = fitness_model.predict(features)[0]
        result = "Fit" if prediction == 1 else "Not Fit"

        conn = sqlite3.connect("patients_data.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO fitness_patients (
                age, weight, height, exercise_days,
                sleep_hours, diet, smoking, alcohol, prediction
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.age, data.weight, data.height,
            data.exercise_days, data.sleep_hours,
            data.diet, data.smoking, data.alcohol,
            result
        ))
        conn.commit()
        conn.close()

        return {"prediction": result}
    except Exception as e:
        return {"error": str(e)}

@app.post("/submit-feedback")
def submit_feedback(data: FeedbackInput):
    try:
        conn = sqlite3.connect("patients_data.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO feedback (
                name, mobile, age, email, state, district, rating,
                technical_issues, comments
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.name, data.mobile, data.age, data.email,
            data.state, data.district, data.rating,
            data.technical_issues, data.comments
        ))
        conn.commit()
        conn.close()

        return {"message": "Feedback saved successfully!"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/records/heart")
def get_heart_records():
    conn = sqlite3.connect("patients_data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM heart_patients ORDER BY timestamp DESC")
    records = cursor.fetchall()
    conn.close()
    return {"records": records}

@app.get("/records/fitness")
def get_fitness_records():
    conn = sqlite3.connect("patients_data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM fitness_patients ORDER BY timestamp DESC")
    records = cursor.fetchall()
    conn.close()
    return {"records": records}

@app.get("/records/feedback")
def get_feedback_records():
    conn = sqlite3.connect("patients_data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM feedback ORDER BY timestamp DESC")
    records = cursor.fetchall()
    conn.close()
    return {"records": records}