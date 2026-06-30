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
measurement_name = "carbon_intensity"
asset_name = "Grid Connection" # Using Name instead of ID for stability

# API Configuration
API_TOKEN = os.getenv("ELECTRICITYMAPS_API_TOKEN")
API_URL = "https://api.electricitymaps.com/v3/carbon-intensity/past-range"
# Carbon-free energy (CFE) share — nuclear + renewables as a % of consumption.
# Stored as a second field on the same measurement/timestamps as carbon_intensity.
CFE_API_URL = "https://api.electricitymaps.com/v3/carbon-free-energy/past-range"
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
        "temporalGranularity": "15_minutes",
        "emissionFactorType": "direct",
        "disableEstimations": "true"
    }

    print(f"  Fetching CI: {params['start']} to {params['end']}...")
    response = requests.get(API_URL, headers=headers, params=params)

    if response.status_code != 200:
        print(f"  ❌ API Error: {response.status_code} - {response.text}")
        return []

    data = response.json()
    # The API returns a list under "data" or directly as a list depending on version
    if isinstance(data, dict):
        return data.get("data", [])
    return data


def fetch_carbon_free_pct(start, end):
    """Carbon-free energy share [%] over the same range/granularity as CI.

    Returns { datetime_str : value_pct } so it can be joined onto the CI points
    by timestamp. Endpoint payload items look like
    {"datetime": "...Z", "unit": "%", "value": 77, "isEstimated": false}.
    """
    headers = {"auth-token": API_TOKEN}
    params = {
        "zone": ZONE,
        "start": start.strftime('%Y-%m-%dT%H:%M:%S.000Z'),
        "end": end.strftime('%Y-%m-%dT%H:%M:%S.000Z'),
        "temporalGranularity": "15_minutes",
        "disableEstimations": "true"
    }

    print(f"  Fetching CFE: {params['start']} to {params['end']}...")
    response = requests.get(CFE_API_URL, headers=headers, params=params)

    if response.status_code != 200:
        print(f"  ❌ CFE API Error: {response.status_code} - {response.text}")
        return {}

    data = response.json()
    items = data.get("data", []) if isinstance(data, dict) else data
    return {
        item["datetime"]: float(item["value"])
        for item in items
        if item.get("datetime") and item.get("value") is not None
    }

# --- 3. FETCH AND FORMAT POINTS ---
data_points = []
current_start = start_date

print(f"Requesting data from {start_date} to {end_date} in {CHUNK_SIZE_DAYS}-day chunks...")

while current_start < end_date:
    current_end = min(current_start + timedelta(days=CHUNK_SIZE_DAYS), end_date)
    
    results = fetch_carbon_intensity(current_start, current_end)
    cfe_by_time = fetch_carbon_free_pct(current_start, current_end)

    for item in results:
        # Example: {"zone": "NL", "carbonIntensity": 229, "datetime": "2023-01-01T20:30:00.000Z", ...}
        t_str = item.get("datetime")
        ci_val = item.get("carbonIntensity")

        if t_str and ci_val is not None:
            fields = {"carbon_intensity": float(ci_val)}
            # Join CFE share by timestamp; omit the field when absent so a missing
            # CFE value never silently masquerades as 0% carbon-free.
            cfe_val = cfe_by_time.get(t_str)
            if cfe_val is not None:
                fields["carbon_free_pct"] = float(cfe_val)

            point = {
                "measurement": measurement_name,
                "time": t_str,
                "tags": {
                    "name": asset_name,
                    "zone": ZONE
                },
                "fields": fields
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
