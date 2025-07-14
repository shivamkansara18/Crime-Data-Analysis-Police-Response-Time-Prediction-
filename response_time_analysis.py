import pandas as pd
import psycopg2
import matplotlib.pyplot as plt
import seaborn as sns

#  Connect to PostgreSQL Database
conn = psycopg2.connect(
    dbname="crime_db", 
    user="postgres", 
    password="1234", 
    host="localhost", 
    port="5432"
)

#  SQL Query to Calculate **Corrected** Average Response Time
query = """
    SELECT city, 
    AVG(ABS(EXTRACT(EPOCH FROM (date_reported - date_occurred)) / 60)) AS avg_response_time 
    FROM crime_data 
    WHERE date_reported >= date_occurred  -- Ensure valid timestamps
    GROUP BY city 
    ORDER BY avg_response_time DESC;
"""
response_time_df = pd.read_sql(query, con=conn)

# Close the Database Connection
conn.close()

#  Check for Errors
print(response_time_df.head())

#  Box Plot for Response Time
plt.figure(figsize=(12, 6))
sns.boxplot(x="city", y="avg_response_time", data=response_time_df)

plt.xticks(rotation=45)
plt.xlabel("City")
plt.ylabel("Average Response Time (minutes)")
plt.title("Police Response Time by City")
plt.show()
