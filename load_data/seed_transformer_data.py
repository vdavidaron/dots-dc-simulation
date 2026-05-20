import os
import csv
from datetime import datetime, timedelta, timezone
from influxdb import InfluxDBClient

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
csv_file_path = "HSMS_station.csv"
target_year_column = "Jaar1"
measurement_name = "transformer_background"
asset_name = "Grid Connection" # Using Name instead of ID for stability


# Adjust the year to match your simulation start year
simulation_start_year = 2023
simulation_start_date = datetime(simulation_start_year, 1, 1, 0, 0, 0, tzinfo=timezone.utc)

data_points = []

# --- 3. PARSE CSV AND FORMAT POINTS ---
print(f"Reading hourly data from {csv_file_path} for year {simulation_start_year}...")

try:
    with open(csv_file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter=';')
        hour_index = 0 

        for row in reader:
            raw_value = row[target_year_column]
            # Convert European decimal comma to dot and scale to Watts
            clean_value = float(raw_value.replace(',', '.')) * 1000000

            current_time = simulation_start_date + timedelta(hours=hour_index)

            for i in range(4): # 15-min steps
                t = current_time + timedelta(minutes=15 * i)
                point = {
                    "measurement": measurement_name,
                    "time": t.strftime('%Y-%m-%dT%H:%M:%SZ'),
                    "tags": {
                        "name": asset_name
                    },
                    "fields": {
                        "background_w": clean_value
                    }
                }
                data_points.append(point)

            hour_index += 1

    # --- 4. WRITE TO DATABASE ---
    print(f"Prepared {len(data_points)} points. Writing to InfluxDB...")
    client.write_points(data_points, batch_size=1000)
    print(f"✅ Successfully saved data with tag name='{asset_name}'")

except FileNotFoundError:
    print(f"❌ Error: Could not find '{csv_file_path}'.")
except Exception as e:
    print(f"❌ Error: {e}")