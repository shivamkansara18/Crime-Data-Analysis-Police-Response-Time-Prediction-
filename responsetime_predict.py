import pandas as pd
import numpy as np
import psycopg2
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import matplotlib.pyplot as plt
from datetime import datetime

# --- PostgreSQL Connection ---
try:
    conn = psycopg2.connect(
        dbname="crime_db",
        user="postgres",
        password="1234",
        host="localhost",
        port="5432"
    )
    print("Connected to PostgreSQL!")
except Exception as e:
    print("Error connecting to PostgreSQL:", e)
    exit()

# --- Load Data ---
query = "SELECT * FROM crime_data;"
df = pd.read_sql_query(query, conn)

# Convert to datetime
df['date_occurred'] = pd.to_datetime(df['date_occurred'], errors='coerce')
df['date_reported'] = pd.to_datetime(df['date_reported'], errors='coerce')

# Remove null dates
df.dropna(subset=['date_occurred', 'date_reported'], inplace=True)

# Calculate response time in hours
df['response_time'] = (df['date_reported'] - df['date_occurred']).dt.total_seconds() / 3600.0

# Remove unreasonable response times
df = df[(df['response_time'] > 0) & (df['response_time'] < 336)]  # 2 weeks max

# Extract useful features
df['hour_occurred'] = pd.to_datetime(df['time_occurred'], format='%H:%M:%S', errors='coerce').dt.hour
df['victim_age'] = pd.to_numeric(df['victim_age'], errors='coerce').fillna(0)

# Encode categorical features
for col in ['city', 'crime_description', 'victim_gender', 'weapon_used', 'crime_domain']:
    df[col] = df[col].fillna("Unknown")
    df[col] = LabelEncoder().fit_transform(df[col])

# Final features
features = ['hour_occurred', 'city', 'crime_description', 'victim_age',
            'victim_gender', 'weapon_used', 'crime_domain', 'police_deployed']
X = df[features]
y = df['response_time']

# --- Split Data ---
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# --- Train Models ---
rf = RandomForestRegressor(n_estimators=100, random_state=42)
rf.fit(X_train, y_train)
y_pred_rf = rf.predict(X_test)

lr = LinearRegression()
lr.fit(X_train, y_train)
y_pred_lr = lr.predict(X_test)

# --- Evaluation Function ---
def evaluate_model(name, y_true, y_pred):
    print(f"\n{name} Evaluation:")
    print(f"MAE  = {mean_absolute_error(y_true, y_pred):.2f} hours")
    # print(f"RMSE = {mean_squared_error(y_true, y_pred, squared=False):.2f} hours")
    rmse = mean_squared_error(y_true, y_pred) ** 0.5
    print(f"RMSE = {rmse:.2f} hours")   
    print(f"R²   = {r2_score(y_true, y_pred):.2f}")

evaluate_model("Random Forest", y_test, y_pred_rf)
evaluate_model("Linear Regression", y_test, y_pred_lr)

# --- Sample Predictions ---
print("\n🔮 Sample Predictions (Random Forest):")
for actual, pred in zip(y_test[:10], y_pred_rf[:10]):
    print(f"Actual: {actual:.2f} hrs | Predicted: {pred:.2f} hrs")

# --- Plot Predictions ---
plt.figure(figsize=(8,6))
plt.scatter(y_test, y_pred_rf, alpha=0.5, color='blue')
plt.xlabel("Actual Response Time (hrs)")
plt.ylabel("Predicted Response Time (hrs)")
plt.title("Random Forest - Actual vs Predicted")
plt.grid(True)
plt.tight_layout()
plt.show()

