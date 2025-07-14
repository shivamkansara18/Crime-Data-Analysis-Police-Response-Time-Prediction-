import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Connect to PostgreSQL
conn = psycopg2.connect(
    dbname="crime_db",
    user="postgres",
    password="1234",
    host="localhost",
    port="5432"
)

# Query: Get city-level stats with valid response times only
query = """
SELECT city,
       COUNT(*) AS total_crimes,
       ROUND(AVG(EXTRACT(EPOCH FROM (date_reported - date_occurred)) / 60), 2) AS avg_response_time_minutes
FROM crime_data
WHERE date_occurred IS NOT NULL 
  AND date_reported IS NOT NULL
  AND date_reported >= date_occurred
GROUP BY city
HAVING COUNT(*) > 10
ORDER BY total_crimes DESC;
"""

df = pd.read_sql(query, conn)
conn.close()

# Plotting
plt.figure(figsize=(14, 7))
scatter = sns.scatterplot(
    data=df, 
    x="total_crimes", 
    y="avg_response_time_minutes", 
    hue="city", 
    s=120, 
    palette="tab20"
)

plt.title("Hotspots vs Response Time", fontsize=16)
plt.xlabel("Number of Crimes (Hotspot Level)", fontsize=12)
plt.ylabel("Average Response Time (minutes)", fontsize=12)
plt.grid(True)

# Move the legend to the right
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', title='City')
plt.tight_layout()
plt.show()

