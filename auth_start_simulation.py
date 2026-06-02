import base64
import requests
import json
import sys
import os
from dotenv import load_dotenv

# =============================================================================
# 1. Configuration (UPDATE THESE VALUES)
# =============================================================================
DOTS_BASE_URL = "http://localhost:8011"  # Change to your actual server IP/domain
TOKEN_URL = f"{DOTS_BASE_URL}/api/v1/simulation/token"
SIMULATION_URL = f"{DOTS_BASE_URL}/api/v1/simulation/start" 

# Load environment variables from the .env file
load_dotenv()

# Fetch the credentials safely
USERNAME = os.getenv("DOTS_USERNAME")
PASSWORD = os.getenv("DOTS_PASSWORD")

if not USERNAME or not PASSWORD:
    raise ValueError("Missing DOTS credentials! Please check your .env file.")

GITHUB_ORG = os.getenv("GITHUB_USERNAME")
ESDL_FILE_PATH = "datacenter_bess_scenario.esdl"

# =============================================================================
# 2. Authenticate and Get Token
# =============================================================================
print(f"Authenticating with {TOKEN_URL}...")

auth_data = {
    "grant_type": "password",
    "username": USERNAME,
    "password": PASSWORD,
    # If your specific setup strictly requires client_id/secret, uncomment below:
    # "client_id": "your_client_id",
    # "client_secret": "your_client_secret"
}

try:
    # Note: OAuth2 expects form-encoded data, so we use 'data=' instead of 'json='
    token_response = requests.post(TOKEN_URL, data=auth_data)
    
    if token_response.status_code != 200:
        print(f"❌ Authentication failed! Status Code: {token_response.status_code}")
        print(token_response.text)
        sys.exit(1)
        
    access_token = token_response.json().get("access_token")
    print("✅ Authentication successful! Token acquired.\n")
    
except requests.exceptions.ConnectionError:
    print(f"❌ Connection Error: Could not connect to {TOKEN_URL}.")
    sys.exit(1)

# =============================================================================
# 3. Encode the ESDL file to Base64
# =============================================================================
print(f"Reading and encoding {ESDL_FILE_PATH}...")
try:
    with open(ESDL_FILE_PATH, "rb") as esdl_file:
        esdl_bytes = esdl_file.read()
    esdl_base64string = base64.b64encode(esdl_bytes).decode('utf-8')
except FileNotFoundError:
    print(f"❌ Error: Could not find {ESDL_FILE_PATH}.")
    sys.exit(1)

print(GITHUB_ORG)

# =============================================================================
# 4. Build the DOTS JSON Payload
# =============================================================================
print("Building simulation payload...")
payload = {
    "name": "Datacenter BESS Peak Shaving Simulation",
    "start_date": "2023-01-25 00:00:00",
    "simulation_duration_in_seconds": "86400",
    "keep_logs_hours": 1,
    "log_level": "warning",
    "calculation_services": [
        {
            "esdl_type": "ElectricityDemand",
            "calc_service_name": "datacenter_demand_service",
            "service_image_url": f"ghcr.io/{GITHUB_ORG}/datacenter-demand-service:v2",
            "nr_of_models": 0,
            "amount_of_calculations": 1
        },
        {
            "esdl_type": "Battery",
            "calc_service_name": "battery_service",
            "service_image_url": f"ghcr.io/{GITHUB_ORG}/battery-service:v2",
            "nr_of_models": 0,
            "amount_of_calculations": 1
        },
        {
            "esdl_type": "PowerPlant",
            "calc_service_name": "power_plant_service",
            "service_image_url": f"ghcr.io/{GITHUB_ORG}/power-plant-service:v2",
            "nr_of_models": 0,
            "amount_of_calculations": 1
        },
        {
            "esdl_type": "ElectricityNetwork",
            "calc_service_name": "network_solver_service",
            "service_image_url": f"ghcr.io/{GITHUB_ORG}/network-balancer-service:v2",
            "nr_of_models": 0,
            "amount_of_calculations": 1
        }
    ],
    "esdl_base64string": esdl_base64string
}

# =============================================================================
# 5. Send the POST Request with the Bearer Token
# =============================================================================
print(f"Sending simulation request to {SIMULATION_URL}...")

# Here is where the magic happens: we attach the token to the Authorization header
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {access_token}"
}

response = requests.post(SIMULATION_URL, headers=headers, json=payload)

if response.status_code in [200, 201, 202]:
    print("\n✅ Simulation successfully submitted!")
    response_data = response.json()
    print("Response from DOTS:")
    print(json.dumps(response_data, indent=2))
    
    if "id" in response_data:
        sim_id = response_data['id']
        print(f"\nTo check logs later, use endpoint: {DOTS_BASE_URL}/api/v1/simulation/logs/{sim_id}")
        print(f"(Don't forget to pass the Bearer token in the headers!)")
        
else:
    print(f"\n❌ Failed to start simulation. Status code: {response.status_code}")
    print(response.text)