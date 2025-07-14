import psycopg2
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import classification_report
from imblearn.over_sampling import SMOTE

# PostgreSQL Connection
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
    print("Connection Error:", e)
    exit()

#  Load Data from DB
query = "SELECT * FROM crime_data WHERE crime_description IS NOT NULL;"
df = pd.read_sql_query(query, conn)

print(f"🔍 Rows Fetched: {len(df)}")

# Time conversion and feature engineering
df['time_occurred'] = pd.to_datetime(df['time_occurred'], errors='coerce')
df['hour_of_day'] = df['time_occurred'].dt.hour

# Fill missing values
df['victim_age'] = df['victim_age'].fillna(df['victim_age'].median())
df['victim_gender'] = df['victim_gender'].fillna(df['victim_gender'].mode()[0])
df['weapon_used'] = df['weapon_used'].fillna(df['weapon_used'].mode()[0])
df['crime_domain'] = df['crime_domain'].fillna(df['crime_domain'].mode()[0])
# df['hour_of_day'] = df['hour_of_day'].fillna(df['hour_of_day'].mode()[0])
hour_mode = df['hour_of_day'].mode()
if not hour_mode.empty:
    df['hour_of_day'] = df['hour_of_day'].fillna(hour_mode[0])
else:
    df['hour_of_day'] = df['hour_of_day'].fillna(3)

# Combine similar classes to reduce number of categories
crime_map = {
    'ROBBERY': 'ROBBERY',
    'BURGLARY': 'BURGLARY',
    'MURDER': 'VIOLENT_CRIME',
    'ASSAULT': 'VIOLENT_CRIME',
    'BATTERY': 'VIOLENT_CRIME',
    'RAPE': 'SEXUAL_OFFENSE',
    'SEXUAL ASSAULT': 'SEXUAL_OFFENSE',
    'VANDALISM': 'PROPERTY_DAMAGE',
    'THEFT': 'THEFT',
    'MOTOR VEHICLE THEFT': 'VEHICLE_THEFT',
    'SHOPLIFTING': 'THEFT',
    'ARSON': 'PROPERTY_DAMAGE',
    'FRAUD': 'FINANCIAL_CRIME',
    'EMBEZZLEMENT': 'FINANCIAL_CRIME',
    'DRUG OFFENSE': 'DRUG_OFFENSE',
    'NARCOTICS': 'DRUG_OFFENSE',
    'KIDNAPPING': 'VIOLENT_CRIME',
    'TRESPASSING': 'OTHER',
    'GAMBLING': 'OTHER',
    'PUBLIC INTOXICATION': 'OTHER',
    'OTHER': 'OTHER'
}

df['crime_group'] = df['crime_description'].map(lambda x: crime_map.get(x.upper(), 'OTHER'))

#  Check class count
print(f" Remaining Rows After Cleaning: {len(df)}")
print(" Unique Classes After Grouping:", df['crime_group'].nunique())

# Encode target
le = LabelEncoder()
df['crime_label'] = le.fit_transform(df['crime_group'])

# Features & Target
X = df[['hour_of_day', 'victim_gender', 'city', 'victim_age', 'weapon_used', 'crime_domain']]
y = df['crime_label']

# Encode Categorical Features
X = pd.get_dummies(X)

# Fill any remaining NaNs
X = X.fillna(0)

# Scale
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Apply SMOTE to balance class distribution
smote = SMOTE(random_state=42)
X_resampled, y_resampled = smote.fit_resample(X_scaled, y)

X_train, X_test, y_train, y_test = train_test_split(X_resampled, y_resampled, test_size=0.2, random_state=42)

clf = RandomForestClassifier(n_estimators=100, max_depth=20, random_state=42)
clf.fit(X_train, y_train)

# Predict & Evaluate
y_pred = clf.predict(X_test)
print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=le.classes_))

conn.close()
