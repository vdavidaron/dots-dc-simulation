import os
import requests
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
measurement_name = "price-day-ahead"
asset_name = "Grid Connection" # Using Name instead of ID for stability

# API Configuration
API_TOKEN = os.getenv("ELECTRICITYMAPS_API_TOKEN")
API_URL = "https://api.electricitymaps.com/v3/price-day-ahead/past-range"
ZONE = "NL"

# Simulation Range (Fetch 2 weeks of data by default to have plenty for simulation)
start_date = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
end_date = datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc)

# The API limited to ~10 days per request for 15-min granularity usually, 
# but user said "a few days at a time max". We'll use 2-day chunks.
CHUNK_SIZE_DAYS = 3

def fetch_carbon_intensity(start, end):
    headers = {"auth-token": API_TOKEN}
    params = {
        "zone": ZONE,
        "start": start.strftime('%Y-%m-%dT%H:%M:%S.000Z'),
        "end": end.strftime('%Y-%m-%dT%H:%M:%S.000Z'),
        "temporalGranularity": "15_minutes"
    }
    
    print(f"  Fetching: {params['start']} to {params['end']}...")
    response = requests.get(API_URL, headers=headers, params=params)
    
    if response.status_code != 200:
        print(f"  ❌ API Error: {response.status_code} - {response.text}")
        return []
    
    data = response.json()
    # The API returns a list under "data" or directly as a list depending on version
    if isinstance(data, dict):
        return data.get("data", [])
    return data

# --- 3. FETCH AND FORMAT POINTS ---
data_points = []
current_start = start_date

print(f"Requesting data from {start_date} to {end_date} in {CHUNK_SIZE_DAYS}-day chunks...")

while current_start < end_date:
    current_end = min(current_start + timedelta(days=CHUNK_SIZE_DAYS), end_date)
    
    results = fetch_carbon_intensity(current_start, current_end)
    
    for item in results:
        # Example: {"zone": "NL", "value": 229, "datetime": "2023-01-01T20:30:00.000Z", ...}
        t_str = item.get("datetime")
        ci_val = item.get("value")
        unit = item.get("unit")
        source = item.get("source")
        
        if t_str and ci_val is not None:
            point = {
                "measurement": measurement_name,
                "time": t_str,
                "tags": {
                    "name": asset_name,
                    "zone": ZONE,
                    "unit": unit,
                    "source": source
                },
                "fields": {
                    "price": float(ci_val)
                }
            }
            data_points.append(point)
    
    current_start = current_end

# --- 4. WRITE TO DATABASE ---
if data_points:
    print(f"Prepared {len(data_points)} points. Writing to InfluxDB...")
    try:
        client.write_points(data_points, batch_size=500)
        print(f"✅ Successfully saved data to '{measurement_name}' measurement.")
    except Exception as e:
        print(f"❌ Error writing to InfluxDB: {e}")
else:
    print("⚠ No data points collected. Check API response or auth token.")
