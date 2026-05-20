import os
import sys
import argparse
from influxdb import InfluxDBClient

# =============================================================================
# InfluxDB Configuration (Aligned with your local seed script)
# =============================================================================
INFLUX_HOST = os.environ.get('INFLUXDB_HOST', 'localhost')
INFLUX_PORT = int(os.environ.get('INFLUXDB_PORT', 8096))
INFLUX_USER = os.environ.get('INFLUXDB_USER', 'admin')
INFLUX_PASS = os.environ.get('INFLUXDB_PASSWORD', 'admin')
DATABASE    = os.environ.get('INFLUXDB_NAME', 'GO-e')

# The specific measurements requested for cleanup
TARGET_MEASUREMENTS = [
    "Battery",
    "ElectricityDemand",
    "ElectricityNetwork",
    "GasProducer",
    "PVInstallation",
    "PowerPlant"
]

def clean_influxdb(force=False):
    print(f"Connecting to InfluxDB at {INFLUX_HOST}:{INFLUX_PORT} (DB: {DATABASE})...")
    client = InfluxDBClient(
        host=INFLUX_HOST, 
        port=INFLUX_PORT, 
        username=INFLUX_USER, 
        password=INFLUX_PASS,
        database=DATABASE
    )

    try:
        # Check if DB exists
        databases = client.get_list_database()
        if not any(db['name'] == DATABASE for db in databases):
            print(f"❌ Error: Database '{DATABASE}' does not exist at {INFLUX_HOST}:{INFLUX_PORT}.")
            return

        print(f"Using database '{DATABASE}'.")
        
        # Get list of existing measurements to avoid errors
        existing_measurements = [m['name'] for m in client.get_list_measurements()]
        
        cleaned_any = False
        for m_name in TARGET_MEASUREMENTS:
            if m_name in existing_measurements:
                if not force:
                    confirm = input(f"Delete all data from measurement '{m_name}'? (y/n): ")
                    if confirm.lower() != 'y':
                        print(f"Skipping {m_name}.")
                        continue
                
                print(f"Dropping measurement '{m_name}'...")
                client.query(f'DROP MEASUREMENT "{m_name}"')
                print(f"✅ Measurement '{m_name}' cleared.")
                cleaned_any = True
            else:
                print(f"ℹ️  Measurement '{m_name}' not found, skipping.")

        if not cleaned_any:
            print("No matching measurements found to clean.")
        else:
            print("\nCleanup complete.")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean specific simulation measurements from InfluxDB.")
    parser.add_argument("--force", action="store_true", help="Delete measurements automatically without confirmation.")
    args = parser.parse_args()

    clean_influxdb(force=args.force)
