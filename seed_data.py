import os
import csv
import argparse
from datetime import datetime, timedelta, timezone
from influxdb import InfluxDBClient
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
LOGGER = logging.getLogger(__name__)

def parse_args():
    parser = argparse.ArgumentParser(description="Standardized Data Seeder for DOTS InfluxDB")
    
    # Connection details
    parser.add_argument("--host", default=os.environ.get('INFLUXDB_HOST', 'localhost'), help="InfluxDB Host")
    parser.add_argument("--port", type=int, default=int(os.environ.get('INFLUXDB_PORT', 8086)), help="InfluxDB Port")
    parser.add_argument("--user", default=os.environ.get('INFLUXDB_USER', 'admin'), help="InfluxDB User")
    parser.add_argument("--password", default=os.environ.get('INFLUXDB_PASSWORD', 'admin'), help="InfluxDB Password")
    parser.add_argument("--db", default=os.environ.get('INFLUXDB_NAME', 'GO-e'), help="InfluxDB Database Name")
    
    # Data details
    parser.add_argument("--file", required=True, help="Path to the CSV file")
    parser.add_argument("--delimiter", default=";", help="CSV delimiter (default: ;)")
    parser.add_argument("--measurement", required=True, help="InfluxDB measurement name (e.g., transformer_background)")
    parser.add_argument("--esdl-id", help="Default ESDL ID to tag the data with")
    parser.add_argument("--tags", help="Comma-separated key=value pairs for additional tags (e.g., profile=high_demand,region=north)")
    
    # Column mapping
    parser.add_argument("--columns", required=True, help="Comma-separated list of columns to import as fields")
    parser.add_argument("--field-names", help="Comma-separated list of field names in Influx (defaults to column names)")
    
    # Time management
    parser.add_argument("--start-date", default="2023-01-01T00:00:00Z", help="Start date for the data (ISO 8601)")
    parser.add_argument("--step-minutes", type=int, default=60, help="Minutes between each row in the CSV (default: 60)")
    parser.add_argument("--sim-step-minutes", type=int, help="If provided, will upsample data to this resolution (e.g., 15)")
    parser.add_argument("--time-column", help="Column name if time is already in the CSV (overrides start-date/step)")
    parser.add_argument("--time-format", default="%Y-%m-%d %H:%M:%S", help="Format of the time column if used")

    return parser.parse_args()

def main():
    args = parse_args()
    
    # 1. Connect to InfluxDB
    client = InfluxDBClient(host=args.host, port=args.port, username=args.user, password=args.password, database=args.db)
    client.create_database(args.db)
    
    # 2. Prepare Mappings
    cols = args.columns.split(',')
    fields = args.field_names.split(',') if args.field_names else cols
    if len(cols) != len(fields):
        LOGGER.error("Error: Number of columns must match number of field names.")
        return

    mapping = dict(zip(cols, fields))
    
    # 3. Handle Extra Tags
    extra_tags = {}
    if args.tags:
        for pair in args.tags.split(','):
            if '=' in pair:
                k, v = pair.split('=', 1)
                extra_tags[k.strip()] = v.strip()

    # 4. Handle Time
    start_dt = datetime.fromisoformat(args.start_date.replace('Z', '+00:00'))
    
    data_points = []
    LOGGER.info(f"Reading {args.file}...")
    
    try:
        with open(args.file, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=args.delimiter)
            
            for i, row in enumerate(reader):
                # Calculate the start time for this CSV row
                if args.time_column:
                    row_start_dt = datetime.strptime(row[args.time_column], args.time_format).replace(tzinfo=timezone.utc)
                else:
                    row_start_dt = start_dt + timedelta(minutes=args.step_minutes * i)
                
                # Determine how many sub-steps we need if upsampling
                num_sub_steps = 1
                sub_step_delta = args.step_minutes
                if args.sim_step_minutes and args.sim_step_minutes < args.step_minutes:
                    num_sub_steps = args.step_minutes // args.sim_step_minutes
                    sub_step_delta = args.sim_step_minutes

                for s in range(num_sub_steps):
                    current_dt = row_start_dt + timedelta(minutes=sub_step_delta * s)
                
                    # Build point
                    point = {
                        "measurement": args.measurement,
                        "time": current_dt.strftime('%Y-%m-%dT%H:%M:%SZ'),
                        "tags": extra_tags.copy(),
                        "fields": {}
                    }
                    
                    if args.esdl_id: point["tags"]["esdl_id"] = args.esdl_id
                    
                    for col, field in mapping.items():
                        val = row[col].replace(',', '.') # Handle European decimals
                        try:
                            point["fields"][field] = float(val)
                        except ValueError:
                            LOGGER.warning(f"Row {i}: Could not convert value '{val}' in column '{col}' to float. Skipping field.")

                    if point["fields"]:
                        data_points.append(point)

        # 4. Write Data
        LOGGER.info(f"Prepared {len(data_points)} points. Writing to InfluxDB in batches...")
        client.write_points(data_points, batch_size=1000)
        LOGGER.info("✅ Data seeding complete!")

    except Exception as e:
        LOGGER.error(f"Failed to seed data: {e}")

if __name__ == "__main__":
    main()
