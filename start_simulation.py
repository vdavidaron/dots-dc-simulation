import base64
import requests
import json
import math
import re
import sys
import os
from dotenv import load_dotenv
from esdl.esdl_handler import EnergySystemHandler

# =============================================================================
# 1. Configuration (UPDATE THESE VALUES)
# =============================================================================
DOTS_BASE_URL = "http://localhost:8011"
SIMULATION_URL = f"{DOTS_BASE_URL}/api/v1/simulation/start" 

# Load environment variables from the .env file
load_dotenv()


GITHUB_ORG = os.getenv("GITHUB_USERNAME")
ESDL_FILE_PATH = "datacenter_bess_scenario.esdl"
SIMULATION_DURATION_IN_DAYS = 60



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
calculation_services = [
    {
        "esdl_type": "ElectricityDemand",
        "calc_service_name": "datacenter_demand_service",
        "service_image_url": f"ghcr.io/{GITHUB_ORG}/datacenter-demand-service:v0.0.17.2",
        "nr_of_models": 0
    },
    {
        "esdl_type": "Battery",
        "calc_service_name": "battery_service",
        "service_image_url": f"ghcr.io/{GITHUB_ORG}/battery-service:v0.0.17.2",
        "nr_of_models": 0
    },
    {
        "esdl_type": "PowerPlant",
        "calc_service_name": "power_plant_service",
        "service_image_url": f"ghcr.io/{GITHUB_ORG}/power-plant-service:v0.0.17.2",
        "nr_of_models": 0
    },
    {
        "esdl_type": "ElectricityNetwork",
        "calc_service_name": "network_solver_service",
        "service_image_url": f"ghcr.io/{GITHUB_ORG}/network-balancer-service:v0.0.17.2",
        "nr_of_models": 0
    },
    {
        "esdl_type": "PVInstallation",
        "calc_service_name": "local_renewable_service",
        "service_image_url": f"ghcr.io/{GITHUB_ORG}/local-renewable-service:v0.0.17.2",
        "nr_of_models": 0
    },
    {
        "esdl_type": "GasProducer",
        "calc_service_name": "backup_generator_service",
        "service_image_url": f"ghcr.io/{GITHUB_ORG}/backup-generator-service:v0.0.17.2",
        "nr_of_models": 0
    }
]

def sanitize_string(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9- ]", "", s)
    s = re.sub(r"[^a-z0-9]+$", "", s)
    s = s.replace(" ", "-")
    return s


def get_model_ids(esdl_file_path: str, calculation_services: list[dict]) -> list[str]:
    esh = EnergySystemHandler()
    esh.load_file(esdl_file_path)
    energy_system = esh.get_energy_system()

    service_esdl_ids: dict[str, list[str]] = {}
    for obj in energy_system.eAllContents():
        if not hasattr(obj, "id"):
            continue
        type_name = type(obj).__name__
        for service in calculation_services:
            if type_name == service["esdl_type"]:
                service_esdl_ids.setdefault(service["calc_service_name"], []).append(obj.id)

    model_ids = []
    for service in calculation_services:
        esdl_ids = service_esdl_ids.get(service["calc_service_name"], [])
        nr_of_models = service.get("nr_of_models", 0)
        if nr_of_models == 0:
            nr_of_objects_in_model = 1
        else:
            nr_of_objects_in_model = math.ceil(len(esdl_ids) / nr_of_models)

        model_index = 0
        while model_index * nr_of_objects_in_model < len(esdl_ids):
            model_index += 1
            model_id = f"{sanitize_string(service['calc_service_name'])}-{model_index}"
            model_ids.append(model_id)

    return model_ids

simulation_duration_in_seconds = SIMULATION_DURATION_IN_DAYS * 86400

print(f"Simulation duration in seconds: {simulation_duration_in_seconds}")

payload = {
    "name": "Datacenter BESS Peak Shaving Simulation",
    "start_date": "2023-03-01 00:00:00",
    "simulation_duration_in_seconds": f"{simulation_duration_in_seconds}",
    "keep_logs_hours": 24,
    "log_level": "debug",
    "calculation_services": calculation_services,
    "esdl_base64string": esdl_base64string
}

print("Parsing ESDL to determine expected model IDs...")
model_ids = get_model_ids(ESDL_FILE_PATH, calculation_services)
broker_env_federate_count = len(model_ids) + 1
broker_wrapper_expected_federate_count = broker_env_federate_count + 1
print(f"Expected model federates: {len(model_ids)}")
for model_id in model_ids:
    print(f"  - {model_id}")
print(f"Broker env value AMOUNT_OF_INITIALIZATION_MESSAGE_FEDERATES: {broker_env_federate_count}")
print("  (models + 1 ESDL sender federate created by the orchestrator)")
print(f"Broker wrapper total expected federates: {broker_wrapper_expected_federate_count}")
print("  (broker initialization federate + models + orchestrator ESDL sender)")
print("  If the broker log shows one more than the env value, that is expected.")

# =============================================================================
# 5. Send the POST Request with the Bearer Token
# =============================================================================
print(f"Sending simulation request to {SIMULATION_URL}...")

# Here is where the magic happens: we attach the token to the Authorization header
headers = {
    "Content-Type": "application/json"
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