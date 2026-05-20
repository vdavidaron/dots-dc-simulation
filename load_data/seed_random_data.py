import os
import random
from datetime import datetime, timedelta, timezone
from influxdb import InfluxDBClient
from dotenv import load_dotenv

load_dotenv()

# --- 1. SETUP INFLUXDB CONNECTION ---
influx_host = os.environ.get('INFLUXDB_HOST', 'localhost')
influx_port = int(os.environ.get('INFLUXDB_PORT', 8096))
influx_user = os.environ.get('INFLUXDB_USER', 'admin')
influx_pass = os.environ.get('INFLUXDB_PASSWORD', 'admin')
database_name = os.environ.get('INFLUXDB_NAME', 'GO-e')

print(f"Connecting to InfluxDB at {influx_host}:{influx_port}...")
client = InfluxDBClient(
    host=influx_host, 
    port=influx_port, 
    username=influx_user, 
    password=influx_pass, 
    database=database_name
)

client.create_database(database_name)

# --- 2. CONFIGURATION ---
start_date = datetime(2023, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
end_date = datetime(2024, 6, 1, 0, 0, 0, tzinfo=timezone.utc) # 1.5 years to cover long simulations

print(f"Generating random data from {start_date} to {end_date} at 15-minute resolution...")

carbon_points = []
price_points = []

current_time = start_date
step = timedelta(minutes=15)

# Initialize seed for predictability but allow realistic variation
random.seed(42)

# Simple random walk parameters for realistic variation
last_ci = 300.0
last_price = 80.0

while current_time < end_date:
    # 1. Carbon intensity (random walk constrained between 80 and 600)
    last_ci = max(80.0, min(600.0, last_ci + random.uniform(-30.0, 30.0)))
    
    # 2. Price (random walk constrained between 10.0 and 250.0)
    last_price = max(10.0, min(250.0, last_price + random.uniform(-15.0, 15.0)))
    
    t_str = current_time.strftime('%Y-%m-%dT%H:%M:%SZ')
    
    # Carbon Intensity Point
    carbon_points.append({
        "measurement": "carbon_intensity",
        "time": t_str,
        "tags": {
            "name": "Grid Connection",
            "zone": "NL"
        },
        "fields": {
            "carbon_intensity": float(round(last_ci, 2))
        }
    })
    
    # Price Day Ahead Point
    price_points.append({
        "measurement": "price-day-ahead",
        "time": t_str,
        "tags": {
            "name": "Grid Connection",
            "zone": "NL",
            "unit": "EUR",
            "source": "ENTSOE"
        },
        "fields": {
            "price": float(round(last_price, 2))
        }
    })
    
    current_time += step

# --- 3. WRITE TO INFLUXDB ---
print(f"Prepared {len(carbon_points)} carbon intensity points and {len(price_points)} price points.")

try:
    print("Writing carbon_intensity to InfluxDB...")
    client.write_points(carbon_points, batch_size=5000)
    print("✅ Successfully saved carbon_intensity data.")
    
    print("Writing price-day-ahead to InfluxDB...")
    client.write_points(price_points, batch_size=5000)
    print("✅ Successfully saved price-day-ahead data.")
    
    print("🎉 InfluxDB populated with random testing data successfully!")
except Exception as e:
    print(f"❌ Error writing to InfluxDB: {e}")
