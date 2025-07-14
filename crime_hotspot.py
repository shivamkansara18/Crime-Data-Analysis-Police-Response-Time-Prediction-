# import pandas as pd
# import psycopg2
# from sqlalchemy import create_engine
# import folium
# from folium.plugins import HeatMap
# from geopy.geocoders import Nominatim
# import time

# # Initialize geocoder
# geolocator = Nominatim(user_agent="crime_map")

# # Create SQLAlchemy engine
# engine = create_engine("postgresql://postgres:1234@localhost:5432/crime_db")

# # Database query to get the city data
# query = "SELECT city FROM crime_data WHERE city IS NOT NULL"
# crime_data = pd.read_sql(query, con=engine)

# # Function to get latitude and longitude from city name
# def geocode_city(city_name):
#     try:
#         location = geolocator.geocode(city_name)
#         if location:
#             return location.latitude, location.longitude
#         else:
#             return None, None
#     except Exception as e:
#         print(f"Error geocoding {city_name}: {e}")
#         return None, None

# # Geocode all cities and store latitude and longitude
# coordinates = []
# for city in crime_data['city'].dropna():
#     latitude, longitude = geocode_city(city)
#     if latitude and longitude:
#         coordinates.append([latitude, longitude])
#     time.sleep(1)  # Sleep to avoid hitting API limits

# # Create the map centered at a default location
# crime_map = folium.Map(location=[37.77, -122.42], zoom_start=12)

# # Create the heatmap
# HeatMap(coordinates).add_to(crime_map)

# # Save the heatmap as an HTML file
# crime_map.save("crime_hotspots.html")
# print("Heatmap generated: Open 'crime_hotspots.html' in a browser.")





import pandas as pd
import psycopg2
import folium
from folium.plugins import HeatMap
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import time

# 🔹 Database Connection
try:
    conn = psycopg2.connect(
        dbname="crime_db",
        user="postgres",
        password="1234",
        host="localhost",
        port="5432"
    )
    cursor = conn.cursor()
    print(" Connected to PostgreSQL!")
except Exception as e:
    print(" Error connecting to PostgreSQL:", e)
    exit()

# 🔹 Fetch Crime Data from PostgreSQL
query = "SELECT city FROM crime_data"
crime_data = pd.read_sql(query, con=conn)

# 🔹 Geocoding Setup
geolocator = Nominatim(user_agent="crime_heatmap_app")

# 🔹 Function for Geocoding with Retry
def geocode_with_retry(city, retries=3, delay=2):
    for attempt in range(retries):
        try:
            location = geolocator.geocode(city, timeout=10)
            return location
        except GeocoderTimedOut:
            print(f"Geocoding timeout for {city}. Retrying...")
            time.sleep(delay * (2 ** attempt))  # Exponential backoff
    print(f"Failed to geocode {city} after {retries} retries.")
    return None  # Return None if all retries fail

# 🔹 Collect Coordinates for Each City
coordinates = []
for city in crime_data["city"].unique():
    print(f"Geocoding {city}...")
    location = geocode_with_retry(city)
    if location:
        coordinates.append([location.latitude, location.longitude])
    else:
        coordinates.append([None, None])  # Append None if geocoding fails

# 🔹 Create Folium Map and Add HeatMap
crime_map = folium.Map(location=[37.77, -122.42], zoom_start=12)

# Filter out rows with missing coordinates
coordinates = [coord for coord in coordinates if coord[0] is not None and coord[1] is not None]

if coordinates:
    HeatMap(coordinates).add_to(crime_map)
    crime_map.save("crime_hotspots.html")
    print(" Heatmap generated: Open 'crime_hotspots.html' in a browser.")
else:
    print(" No valid coordinates found to generate heatmap.")

# 🔹 Close Database Connection
cursor.close()
conn.close()
print(" Connection closed.")
