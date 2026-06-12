# dots-dc-simulation

Orchestration, data seeding, and the thesis sweep/figure pipeline for the
grid-constrained data-center co-simulation. This repo does not implement a
HELICS calculation service itself; it stands up the federation of the six
service repos (PowerPlant, Battery, Datacenter Demand, Local Renewable, Backup
Generator, Network Balancer) and drives the parametric experiments behind the
thesis results chapter.

## Prerequisites

- `kubectl` and `kind` (the services run as pods in a local `kind` cluster).
- The DOTS simulation orchestrator: https://github.com/dots-energy/dots-simulation-orchestrator
- An InfluxDB instance reachable on the configured host/port (default
  `localhost:8096`, database `GO-e`, `admin/admin`), seeded with the input data.
- A Python environment with `influxdb`, `requests`, `esdl`, and `pandas`
  (the repo-root `venv` covers this).

## What's here

| Path | Purpose |
|---|---|
| `datacenter_bess_scenario.py` | Builds the base ESDL (`datacenter_bess_scenario.esdl`): the data center, BESS, grid connection, PV, backup generator, and the `ElectricityNetwork` KPIs (objective weights, MPC thresholds, forecast sigmas, backup factors, `sim_seed`). Re-run after changing any default. |
| `load_data/` | Seed scripts that load the recorded input traces into InfluxDB. |
| `start_simulation.py` / `local_start_simulation.py` | Submit a single simulation run to the orchestrator. |
| `check_results.py` / `auth_*` | Query helpers for a finished run. |
| `clean_influxdb.py` | Drop the six simulation-output measurements (keeps the seeded inputs). |
| `sweep/` | The parametric sweep + figure pipeline (see `sweep/README.md`). |

## Input data provenance

The simulation replays recorded Dutch data at 15-minute resolution; a synthetic
generator is used for a signal only when a real sample is missing for that step.

| Signal | Source | Seed script |
|---|---|---|
| Datacenter demand | TNO research data-center profile, scaled to 4 MW | `load_data/seed_from_csv.py` (`Rack-total-data.csv`) |
| Solar irradiance | KNMI meteorological station | `load_data/seed_solar_data.py` (`ClimateGroningen.csv`) |
| Transformer background / limit | Liander open data, Lelystad substation | `load_data/powerplant/seed_transformer_data_15m.py` (`OSLelystad.csv`) |
| Grid carbon intensity | Electricity Maps (NL zone) | `load_data/seed_carbon_intensity_data.py` |
| Day-ahead price | EPEX SPOT (NL), via Electricity Maps | `load_data/seed_price_data.py` |

## Transformer constraint

With background demand `B_t` and datacenter load `D_t` at quarter-hour `t`, and
a contracted capacity `C` (the ESDL `PowerPlant.power`):

- **Upper limit:** `B_t + D_t <= C`. The maximum datacenter import is `C - B_t`;
  exceeding it trips the connection. The thesis grid-limit sweep lowers `C`
  toward and below the 4 MW load to force curtailment.
- **Lower limit (mandate):** `B_t + D_t >= -C`. A large upstream renewable
  surplus pushing the background below `-C` obliges the datacenter to absorb the
  excess (the more it soaks up, the lower the price). Toggled by `enable_mandate`.

## Typical workflow

```powershell
venv\Scripts\Activate.ps1

# 1. (once) seed the input data into InfluxDB
cd dots-services\dots-dc-simulation\load_data
python seed_from_csv.py; python seed_solar_data.py
python seed_carbon_intensity_data.py; python seed_price_data.py
cd powerplant; python seed_transformer_data_15m.py

# 2. (re)generate the base ESDL
cd ..\..
python datacenter_bess_scenario.py

# 3. run the parametric sweep and build the thesis figures
cd sweep
python live_runner.py axis1_pareto axis2_bess axis3_pv axis4_backup axis5_mpc
python live_runner.py axis6_seasonal axis7_seasonal_pareto axis8_gridlimit axis9_seed axis10_socbase
python make_figures.py
```

To wipe old run output between sweeps (keeps the seeded inputs):

```powershell
python clean_influxdb.py --force
```

See `sweep/README.md` for the full axis list, the two-baseline accounting, and
the `reextract.py` shortcut that recomputes metrics from existing InfluxDB data
without re-running the 60-day federation.
