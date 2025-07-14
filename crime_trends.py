
import pandas as pd
import psycopg2
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

# Query: Group crimes by year instead of month
query = """
    SELECT EXTRACT(YEAR FROM date_occurred) AS year, COUNT(*) AS crime_count 
    FROM crime_data 
    GROUP BY year 
    ORDER BY year;
"""
crime_trends = pd.read_sql(query, con=conn)

# Plot as bar chart
plt.figure(figsize=(10, 6))
sns.barplot(x="year", y="crime_count", data=crime_trends, palette="viridis")

plt.title("Year-wise Crime Trends")
plt.xlabel("Year")
plt.ylabel("Number of Crimes")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

