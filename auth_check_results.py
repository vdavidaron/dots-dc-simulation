import os
import requests
import json
from dotenv import load_dotenv
import zipfile
import io

# =============================================================================
# 1. Configuration & Auth
# =============================================================================
load_dotenv()
USERNAME = os.getenv("DOTS_USERNAME")
PASSWORD = os.getenv("DOTS_PASSWORD")
SIMULATION_ID = "datacenter-bess-peak-fa878cd5" # Your specific simulation ID

DOTS_BASE_URL = "http://localhost:8011"
TOKEN_URL = f"{DOTS_BASE_URL}/api/v1/simulation/token"
STATUS_URL = f"{DOTS_BASE_URL}/api/v1/simulation/{SIMULATION_ID}"
LOGS_URL = f"{DOTS_BASE_URL}/api/v1/simulation/logs/{SIMULATION_ID}"

# Get the Token
auth_data = {"grant_type": "password", "username": USERNAME, "password": PASSWORD}
token_response = requests.post(TOKEN_URL, data=auth_data)

if token_response.status_code != 200:
    print("❌ Authentication failed!")
    exit(1)
    
access_token = token_response.json().get("access_token")
headers = {"Authorization": f"Bearer {access_token}"}

# =============================================================================
# 2. Check Simulation Status
# =============================================================================
print(f"Checking status for {SIMULATION_ID}...\n")
status_response = requests.get(STATUS_URL, headers=headers)

if status_response.status_code == 200:
    status_data = status_response.json()
    print(f"Current Status: {status_data.get('simulation_status')}")
    if status_data.get('calculation_end_datetime'):
        print(f"Finished at: {status_data.get('calculation_end_datetime')}")
else:
    print(f"Failed to get status. Code: {status_response.status_code}")

# =============================================================================
# 3. Fetch Execution Logs
# =============================================================================
print("\nFetching logs...\n" + "-"*40)
logs_response = requests.get(LOGS_URL, headers=headers)

if logs_response.status_code == 200:
    # Check if the raw bytes start with 'PK' (the ZIP magic number)
    if logs_response.content.startswith(b'PK'):
        print("Logs returned as a ZIP archive. Extracting in memory...\n")
        try:
            # Read the raw response bytes into a ZipFile object
            with zipfile.ZipFile(io.BytesIO(logs_response.content)) as z:
                # Loop through every file inside the ZIP
                for filename in z.namelist():
                    print(f"--- LOGS FOR: {filename.upper()} ---")
                    # Open the file, read the bytes, and decode to string
                    with z.open(filename) as f:
                        log_text = f.read().decode('utf-8')
                        print(log_text if log_text.strip() else "<Empty Log File>")
                    print("-" * 40 + "\n")
        except zipfile.BadZipFile:
            print("❌ Failed to read the ZIP file. The archive might be corrupted or incomplete.")
    else:
        # Fallback just in case it returns plain text error messages
        print("Logs returned as plain text:")
        print(logs_response.text)
else:
    print(f"❌ Failed to get logs. Code: {logs_response.status_code}")
    print(logs_response.text)