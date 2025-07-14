from sqlalchemy import create_engine
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Connect to PostgreSQL using SQLAlchemy
engine = create_engine("postgresql+psycopg2://postgres:1234@localhost:5432/crime_db")

# SQL query to get city-wise crime count (with valid timestamps only)
query = """
SELECT city,
       COUNT(*) AS total_crimes
FROM crime_data
WHERE date_occurred IS NOT NULL 
  AND date_reported IS NOT NULL
  AND date_reported >= date_occurred
GROUP BY city
HAVING COUNT(*) > 10
ORDER BY total_crimes DESC;
"""

# Load data into DataFrame
df = pd.read_sql(query, engine)

# Plot: Bar Graph – City vs Number of Crimes
sns.set(style="whitegrid")
plt.figure(figsize=(14, 6))
barplot = sns.barplot(data=df, x="city", y="total_crimes", palette="viridis")
plt.title("City vs Number of Crimes", fontsize=16)
plt.xlabel("City", fontsize=12)
plt.ylabel("Total Crimes", fontsize=12)
plt.xticks(rotation=45, ha="right")

# Add value labels above each bar
for index, row in df.iterrows():
    barplot.text(index, row.total_crimes + 10, int(row.total_crimes), color='black', ha="center", fontsize=10)

plt.tight_layout()
plt.show()
