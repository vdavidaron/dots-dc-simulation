import uuid
import base64
from esdl.esdl_handler import EnergySystemHandler
from esdl import esdl

# 1. Create empty EnergySystem
esh = EnergySystemHandler()
es = esh.create_empty_energy_system(
    name="Datacenter_BESS_Scenario",
    es_description="Datacenter with BESS and grid connection",
    inst_title="scenario_instance",
    area_title="Datacenter_Site"
)

area = es.instance[0].area

# -----------------------------------------------------------------------------
# 2. Define assets
# -----------------------------------------------------------------------------
# REQUIRED: The Balancer uses this to identify the network it is balancing
lv_network = esdl.ElectricityNetwork(id=str(uuid.uuid4()), name="Site Electricity Management System")
lv_network.KPIs = esdl.KPIs(id=str(uuid.uuid4()))
lv_network.KPIs.kpi.append(esdl.DoubleKPI(id=str(uuid.uuid4()), name="w_unserved", value=1e9))
lv_network.KPIs.kpi.append(esdl.DoubleKPI(id=str(uuid.uuid4()), name="w_carbon", value=1.0))
lv_network.KPIs.kpi.append(esdl.DoubleKPI(id=str(uuid.uuid4()), name="w_price", value=1.0))
lv_network.KPIs.kpi.append(esdl.DoubleKPI(id=str(uuid.uuid4()), name="w_effort", value=0.01))
lv_network.KPIs.kpi.append(esdl.DoubleKPI(id=str(uuid.uuid4()), name="w_soc_low", value=1e6))
lv_network.KPIs.kpi.append(esdl.DoubleKPI(id=str(uuid.uuid4()), name="soc_baseline", value=50.0))
# Carbon-free-energy (CFE) grid-draw constraint for the day-ahead LP.
#   cfe_constraint_mode: 0=off, 1=blended (horizon-mean grid CFE >= threshold),
#                        2=block (no grid draw on steps below threshold)
#   cfe_min_fraction:    threshold in [0,1] (e.g. 1.0 = 100% carbon-free grid only)
lv_network.KPIs.kpi.append(esdl.DoubleKPI(id=str(uuid.uuid4()), name="cfe_constraint_mode", value=0.0))
lv_network.KPIs.kpi.append(esdl.DoubleKPI(id=str(uuid.uuid4()), name="cfe_min_fraction",    value=0.0))
lv_network.KPIs.kpi.append(esdl.DoubleKPI(id=str(uuid.uuid4()), name="enable_battery", value=1.0))
lv_network.KPIs.kpi.append(esdl.DoubleKPI(id=str(uuid.uuid4()), name="enable_backup_generator", value=1.0))
lv_network.KPIs.kpi.append(esdl.DoubleKPI(id=str(uuid.uuid4()), name="enable_renewable_service", value=1.0))
lv_network.KPIs.kpi.append(esdl.DoubleKPI(id=str(uuid.uuid4()), name="enable_change_management", value=1.0))
lv_network.KPIs.kpi.append(esdl.DoubleKPI(id=str(uuid.uuid4()), name="enable_goal_management", value=1.0))
lv_network.KPIs.kpi.append(esdl.DoubleKPI(id=str(uuid.uuid4()), name="enable_mandate", value=1.0))
# Grid connection model: 1.0 = shared transformer (DC headroom = capacity − background),
# 0.0 = dedicated feeder (DC sees full nameplate capacity, no background, no surplus mandate).
lv_network.KPIs.kpi.append(esdl.DoubleKPI(id=str(uuid.uuid4()), name="enable_shared_transformer", value=1.0))

# Change Management (MPC) deviation thresholds — promoted from hard-coded constants to ESDL KPIs
# so each experimental run can sweep them independently for the RQ4 sensitivity study.
lv_network.KPIs.kpi.append(esdl.DoubleKPI(id=str(uuid.uuid4()), name="mpc_soc_drift_threshold",   value=5.0))   # [%]
lv_network.KPIs.kpi.append(esdl.DoubleKPI(id=str(uuid.uuid4()), name="mpc_demand_spike_threshold", value=0.10)) # [fraction]
lv_network.KPIs.kpi.append(esdl.DoubleKPI(id=str(uuid.uuid4()), name="mpc_horizon_steps",         value=24.0))  # [steps] 24 × 15min = 6h
lv_network.KPIs.kpi.append(esdl.DoubleKPI(id=str(uuid.uuid4()), name="mpc_replan_cooldown",       value=4.0))   # [steps] 4 × 15min = 1h

# Forecast-error model parameters — promoted from hard-coded constants in
# forecast_error.py to ESDL KPIs. The three sigmas encode literature-calibrated
# day-ahead forecast accuracy and may be swept to test the EMS under varying
# forecast quality. The seed is exposed for Monte-Carlo replication studies.
lv_network.KPIs.kpi.append(esdl.DoubleKPI(id=str(uuid.uuid4()), name="forecast_sigma_ci",    value=0.12))  # [fraction] Staffell & Pfenninger (2016)
lv_network.KPIs.kpi.append(esdl.DoubleKPI(id=str(uuid.uuid4()), name="forecast_sigma_p_dc",  value=0.05))  # [fraction] Pelley et al. (2009)
lv_network.KPIs.kpi.append(esdl.DoubleKPI(id=str(uuid.uuid4()), name="forecast_sigma_price", value=0.15))  # [fraction] Weron (2014)
lv_network.KPIs.kpi.append(esdl.DoubleKPI(id=str(uuid.uuid4()), name="forecast_seed",        value=42.0))  # [int] RNG seed

# Backup generator (Scope-1) accounting — diesel emission factor and fuel cost.
# Read by both the Network Balancer (cumulative scope split + cost) and the
# BackupGen federate (its own footprint telemetry). Exposed as KPIs so a
# scope-shift scenario can sweep the diesel emission factor and fuel price.
lv_network.KPIs.kpi.append(esdl.DoubleKPI(id=str(uuid.uuid4()), name="backup_co2_factor",       value=600.0))  # [gCO2/kWh] diesel combustion
lv_network.KPIs.kpi.append(esdl.DoubleKPI(id=str(uuid.uuid4()), name="backup_cost_eur_per_kwh", value=0.40))   # [EUR/kWh] diesel fuel

# Monte-Carlo seed for the demand-noise and transformer-background stochastic
# fallbacks. Read by the demand and grid federates; vary it for multi-seed runs.
lv_network.KPIs.kpi.append(esdl.DoubleKPI(id=str(uuid.uuid4()), name="sim_seed", value=42.0))  # [int] noise seed

# SERVICE 1: DatacenterDemandService - ~1 MW average load (4 MW nameplate ceiling)
# power is typically EDouble but minLoad is EInt in some ESDL versions
datacenter = esdl.ElectricityDemand(id=str(uuid.uuid4()), name="Datacenter Load", power=4000000.0)
datacenter.powerFactor = 0.95            

# SERVICE 2: BatteryService - Realistic 10MWh / 4MW BESS
bess = esdl.Battery(id=str(uuid.uuid4()), name="Datacenter BESS", capacity=4000000.0) 
bess.chargeEfficiency = 0.95
bess.dischargeEfficiency = 0.95
bess.maxChargeRate = 4000000.0
bess.maxDischargeRate = 4000000.0
bess.fillLevel = 0.0

# SERVICE 3: PowerPlantService - Realistic 5MW Grid connection
grid_connection = esdl.PowerPlant(id=str(uuid.uuid4()), name="Grid Connection", power=10000000.0)
grid_connection.efficiency = 1.0         
grid_connection.minLoad = -10000000      # Use int for minLoad

# SERVICE 4: LocalGenerator - Realistic 5MW Backup
backup_generator = esdl.GasProducer(id=str(uuid.uuid4()), name="Backup Generator", power=5000000.0)

# SERVICE 5: LocalRenewable - Realistic 1MW Solar array
local_renewable = esdl.PVInstallation(id=str(uuid.uuid4()), name="Local Renewable Energy Source", power=1000000.0)
local_renewable.panelEfficiency = 0.20       
local_renewable.inverterEfficiency = 0.98    
local_renewable.surfaceArea = 5000           # 1MW / (1kW/m2 * 0.2) = 5000 m2
local_renewable.angle = 35                 
local_renewable.orientation = 180          

# 3. Add assets to area
area.asset.extend([lv_network, datacenter, bess, grid_connection, backup_generator, local_renewable])

# -----------------------------------------------------------------------------
# 4. Create ports
# -----------------------------------------------------------------------------
net_to_dc = esdl.OutPort(id=str(uuid.uuid4()), name="net_to_datacenter")
net_to_bess = esdl.OutPort(id=str(uuid.uuid4()), name="net_to_bess")
net_from_bess = esdl.InPort(id=str(uuid.uuid4()), name="net_from_bess")
net_to_grid = esdl.OutPort(id=str(uuid.uuid4()), name="net_to_grid")
net_from_grid = esdl.InPort(id=str(uuid.uuid4()), name="net_from_grid")
net_from_gen = esdl.InPort(id=str(uuid.uuid4()), name="net_from_backup_generator")
net_from_res = esdl.InPort(id=str(uuid.uuid4()), name="net_from_local_res")

lv_network.port.extend([
    net_to_dc, net_to_bess, net_from_bess, net_to_grid, net_from_grid, net_from_gen, net_from_res
])

dc_in = esdl.InPort(id=str(uuid.uuid4()), name="dc_in")

# Attach InfluxDBProfile so the demand service reads config from ESDL
# instead of hard-coding measurement/field/database in the service code.
dc_demand_profile = esdl.InfluxDBProfile(
    id=str(uuid.uuid4()),
    host="influxdb",
    port=8086,
    database="GO-e",
    measurement="historical_datacenter_demand",
    field="Demand_W",
    filters="name='Datacenter Load'",
    multiplier=1.0,
)
dc_in.profile.append(dc_demand_profile)

datacenter.port.append(dc_in)

bess_in = esdl.InPort(id=str(uuid.uuid4()), name="bess_in")
bess_out = esdl.OutPort(id=str(uuid.uuid4()), name="bess_out")
bess.port.extend([bess_in, bess_out])

grid_in = esdl.InPort(id=str(uuid.uuid4()), name="grid_in")
grid_bg_profile = esdl.InfluxDBProfile(
    id=str(uuid.uuid4()), host="influxdb", port=8086, database="GO-e",
    measurement="transformer_background", field="background_w",
    filters="name='Grid Connection'", multiplier=1.0,
)
grid_carbon_profile = esdl.InfluxDBProfile(
    id=str(uuid.uuid4()), host="influxdb", port=8086, database="GO-e",
    measurement="carbon_intensity", field="carbon_intensity",
    filters="name='Grid Connection'", multiplier=1.0,
)
# Carbon-free energy share [%] of the grid mix (Electricity Maps). Lives on the
# same measurement/timestamps as carbon_intensity; parsed alongside it by the
# PowerPlant federate and published as a real-time + day-ahead signal.
grid_cfe_profile = esdl.InfluxDBProfile(
    id=str(uuid.uuid4()), host="influxdb", port=8086, database="GO-e",
    measurement="carbon_intensity", field="carbon_free_pct",
    filters="name='Grid Connection'", multiplier=1.0,
)
grid_price_profile = esdl.InfluxDBProfile(
    id=str(uuid.uuid4()), host="influxdb", port=8086, database="GO-e",
    measurement="price-day-ahead", field="price",
    filters="name='Grid Connection'", multiplier=1.0,
)
grid_in.profile.extend([grid_bg_profile, grid_carbon_profile, grid_cfe_profile, grid_price_profile])
grid_out = esdl.OutPort(id=str(uuid.uuid4()), name="grid_out")
grid_connection.port.extend([grid_in, grid_out])

gen_out = esdl.OutPort(id=str(uuid.uuid4()), name="gen_out")
backup_generator.port.append(gen_out)

res_out = esdl.OutPort(id=str(uuid.uuid4()), name="res_out")
res_profile = esdl.InfluxDBProfile(
    id=str(uuid.uuid4()), host="influxdb", port=8086, database="GO-e",
    measurement="historical_solar_irradiance", field="Irradiance_W_m2",
    filters="name='Local RES'", multiplier=1.0,
)
res_out.profile.append(res_profile)
local_renewable.port.append(res_out)

# -----------------------------------------------------------------------------
# 5. Create connections
# -----------------------------------------------------------------------------
net_to_dc.connectedTo.append(dc_in)
net_to_bess.connectedTo.append(bess_in)
bess_out.connectedTo.append(net_from_bess)
net_to_grid.connectedTo.append(grid_in)
grid_out.connectedTo.append(net_from_grid)
net_from_gen.connectedTo.append(gen_out)
net_from_res.connectedTo.append(res_out)

# -----------------------------------------------------------------------------
# 6. Save and Encode
# -----------------------------------------------------------------------------
file_name = "datacenter_bess_scenario.esdl"
esh.save(filename=file_name)

with open(file_name, "rb") as esdl_file:
    esdl_base64string = base64.b64encode(esdl_file.read()).decode('utf-8')

with open("esdl_base64_payload.txt", "w") as b64_file:
    b64_file.write(esdl_base64string)

print(f"[OK] ESDL file generated.")
