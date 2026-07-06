"""Drive the DOTS orchestrator across every run in an axis and pull metrics.

Workflow per run:
    1. mutate the base ESDL → produce a variant file under sweep/runs/
    2. POST to the orchestrator's /api/v1/simulation/start endpoint
    3. poll /api/v1/simulation/{id} until the status reaches TERMINATED_*
    4. query InfluxDB for the network cumulative metrics tagged with that
       simulation_id and append a single row to the axis CSV.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import requests
from influxdb import InfluxDBClient

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))

from esdl_mutator import mutate_esdl  # noqa: E402
from sweep_plans import ALL_AXES       # noqa: E402

ORCH_URL  = "http://localhost:8011/api/v1/simulation/start"
STATUS_URL_FMT = "http://localhost:8011/api/v1/simulation/{sid}"
INFLUX_HOST = "localhost"
INFLUX_PORT = 8096                       
INFLUX_DB   = "GO-e"
INFLUX_USER = "admin"
INFLUX_PASS = "admin"


def cleanup_pods() -> None:
    """Delete completed/failed/pending federate + broker pods from previous runs.
    Mirrors start_simulation.cleanup_old_simulations(): leaves Running pods alone.
    """
    for phase in ("Failed", "Succeeded", "Pending"):
        try:
            subprocess.run(
                ["kubectl", "delete", "pods", "-n", "dots",
                 "--field-selector", f"status.phase={phase}",
                 "--force", "--grace-period=0"],
                capture_output=True, text=True, timeout=60,
            )
        except Exception as e:
            print(f"  [cleanup warn] phase={phase}: {e}")

GITHUB_ORG = "vdavidaron"
SERVICES = [
    ("ElectricityDemand",   "datacenter_demand_service",  "datacenter-demand-service:v0.0.20"),
    ("Battery",             "battery_service",            "battery-service:v0.0.23"),
    ("PowerPlant",          "power_plant_service",        "power-plant-service:v0.0.20"),
    ("ElectricityNetwork",  "network_solver_service",     "network-balancer-service:v0.0.23"),
    ("PVInstallation",      "local_renewable_service",    "local-renewable-service:v0.0.20"),
    ("GasProducer",         "backup_generator_service",   "backup-generator-service:v0.0.20"),
]

METRIC_FIELDS = [
    "Cumulative_Carbon_g",
    "Cumulative_Scope2_Carbon_g",
    "Cumulative_Scope1_Carbon_g",
    "Cumulative_Cost_EUR",
    "Cumulative_Unserved_kWh",
    "Cumulative_EqualService_Carbon_g",
    "Cumulative_EqualService_Cost_EUR",
    "Cumulative_EqualService_Unserved_kWh",
    "Cumulative_Passive_Carbon_g",
    "Cumulative_Passive_Cost_EUR",
    "Cumulative_Passive_Unserved_kWh",
    "Cumulative_Backup_Energy_kWh",
    "Cumulative_Backup_Fuel_Cost_EUR",
    "Cumulative_Grid_Energy_kWh",
    "Cumulative_PV_Energy_kWh",
    "Cumulative_DC_Energy_kWh",
    "Cumulative_BESS_Throughput_kWh",
    "Cumulative_BESS_Discharge_kWh",
    "Cumulative_Congestion_Served_kWh",
]

DT_HOURS = 0.25  # 15-minute dispatch step (matches reextract.DT_HOURS)

# Economic assumptions for NPV / LCOS post-processing
BESS_CAPEX_EUR_PER_KWH  = 200.0   # EUR/kWh, BNEF 2024 median for utility-scale LFP in NL
BESS_OPEX_EUR_PER_KW_YR = 10.0    # EUR/kW/year O&M
NPV_DISCOUNT_RATE        = 0.05    # 5 % real discount rate
NPV_LIFETIME_YR          = 10      # 10-year asset lifetime


def _build_payload(esdl_b64: str, name: str, days: int, start_date: str) -> dict[str, Any]:
    calc = [
        {
            "esdl_type": t,
            "calc_service_name": svc,
            "service_image_url": f"ghcr.io/{GITHUB_ORG}/{img}",
            "nr_of_models": 0,
        }
        for t, svc, img in SERVICES
    ]
    return {
        "name": name,
        "start_date": start_date,
        "simulation_duration_in_seconds": str(days * 86400),
        "keep_logs_hours": 24,
        "log_level": "warning",
        "calculation_services": calc,
        "esdl_base64string": esdl_b64,
    }


TERMINAL_PATTERNS = ("terminated", "deployment(s) failed", "pods are deleted",
                     "podds are deleted")


def _is_terminal(status: str) -> bool:
    return any(pat in status for pat in TERMINAL_PATTERNS)


def _terminate(sim_id: str) -> None:
    try:
        requests.delete(f"http://localhost:8011/api/v1/simulation/terminate/{sim_id}",
                        timeout=20)
    except requests.RequestException as e:
        print(f"  [{sim_id}] terminate request failed: {e}")


def _poll_until_done(sim_id: str, poll_s: int = 15, timeout_s: int = 900,
                     stuck_deployed_s: int = 360) -> str:
    """Poll until the orchestrator reports a terminal status.

    Stuck-detection: a healthy 60-day run finishes in ~5 min after reaching
    "all models deployed". If the simulation has been in "all models deployed"
    for more than ``stuck_deployed_s`` seconds without progressing further,
    we trigger a graceful terminate via the orchestrator so the runner can
    move on. ``timeout_s`` is the absolute ceiling.
    """
    deadline = time.time() + timeout_s
    last_status = ""
    deployed_since: float | None = None
    while time.time() < deadline:
        try:
            r = requests.get(STATUS_URL_FMT.format(sid=sim_id), timeout=20)
            if r.status_code == 200:
                status = r.json().get("simulation_status", "")
                if status != last_status:
                    print(f"  [{sim_id}] status: {status}")
                    last_status = status
                    if "deployed" in status and "terminated" not in status:
                        deployed_since = time.time()
                if _is_terminal(status):
                    return status
                if (deployed_since is not None
                        and time.time() - deployed_since > stuck_deployed_s):
                    print(f"  [{sim_id}] stuck in 'deployed' for "
                          f"{int(time.time() - deployed_since)}s — terminating")
                    _terminate(sim_id)
                    deployed_since = None  # don't double-fire
        except requests.RequestException as e:
            print(f"  [{sim_id}] poll error: {e}")
        time.sleep(poll_s)
    print(f"  [{sim_id}] absolute timeout — terminating")
    _terminate(sim_id)
    return "timeout (terminated by runner)"


def _query_cumulative(client: InfluxDBClient, sim_id: str) -> dict[str, float]:
    """Pull the last cumulative point per metric for this simulation."""
    out: dict[str, float] = {}
    for f in METRIC_FIELDS:
        q = (
            f'SELECT last("{f}") AS v '
            f'FROM "ElectricityNetwork" '
            f"WHERE \"simulation_id\" = '{sim_id}'"
        )
        rs = client.query(q)
        pts = list(rs.get_points())
        out[f] = float(pts[0]["v"]) if pts else float("nan")

    # Replan count = sum of Triggered_Replan_Flag (per-step 0/1)
    q = (
        'SELECT sum("Triggered_Replan_Flag") AS v '
        'FROM "ElectricityNetwork" '
        f"WHERE \"simulation_id\" = '{sim_id}'"
    )
    rs = client.query(q)
    pts = list(rs.get_points())
    out["Replan_Count"] = float(pts[0]["v"]) if pts and pts[0]["v"] is not None else 0.0

    # Minimum SoC reached over the entire run (SoC Depletion Depth)
    q = (
        'SELECT min("Actual_SOC_from_Battery") AS v '
        'FROM "ElectricityNetwork" '
        f"WHERE \"simulation_id\" = '{sim_id}'"
    )
    rs = client.query(q)
    pts = list(rs.get_points())
    out["Min_SOC_Overall"] = float(pts[0]["v"]) if pts else float("nan")

    # Minimum SoC reached during curtailment events specifically
    q = (
        'SELECT min("Actual_SOC_from_Battery") AS v '
        'FROM "ElectricityNetwork" '
        f"WHERE \"simulation_id\" = '{sim_id}' AND \"Curtailment_Active_Flag\" = 1.0"
    )
    rs = client.query(q)
    pts = list(rs.get_points())
    out["Min_SOC_During_Curtailment"] = float(pts[0]["v"]) if pts else float("nan")

    # Grid compliance rate = fraction of steps where grid import was within limit
    q = (
        'SELECT mean("Grid_Compliance_Flag") AS v '
        'FROM "ElectricityNetwork" '
        f"WHERE \"simulation_id\" = '{sim_id}'"
    )
    rs = client.query(q)
    pts = list(rs.get_points())
    out["Grid_Compliance_Rate"] = float(pts[0]["v"]) if pts else float("nan")

    return out


def _query_grid_cfe(client: InfluxDBClient, sim_id: str) -> dict[str, float]:
    """Carbon-free energy [kWh] imported from the grid over the run.

    Joins the per-step grid draw (``Routed_to_Grid_W``, logged by the Network
    Balancer for this sim) with the exogenous grid carbon-free share
    (``carbon_free_pct``, seeded into the ``carbon_intensity`` measurement from
    Electricity Maps' /carbon-free-energy endpoint) by timestamp, and weights
    each step's grid energy by that step's carbon-free fraction.

    Because the weighting is on grid energy *actually drawn*, unserved load never
    enters the numerator or the denominator — the carbon-free percentage is a
    pure property of the grid imports, exactly as requested.

    Returns ``Cumulative_Grid_CFE_kWh`` and ``Grid_CFE_Coverage`` (fraction of
    steps that had a matching CFE sample; a low value means the seed data did not
    cover the simulated window and ``Grid_CFE_Pct`` should be treated as partial).
    """
    en = client.query(
        'SELECT "Routed_to_Grid_W" AS g FROM "ElectricityNetwork" '
        f"WHERE \"simulation_id\" = '{sim_id}'"
    )
    rows = [(p["time"], p["g"]) for p in en.get_points() if p.get("g") is not None]
    if not rows:
        return {"Cumulative_Grid_CFE_kWh": float("nan"), "Grid_CFE_Coverage": 0.0}

    times = [t for t, _ in rows]
    t_lo, t_hi = min(times), max(times)
    cfe = client.query(
        'SELECT "carbon_free_pct" AS c FROM "carbon_intensity" '
        f"WHERE time >= '{t_lo}' AND time <= '{t_hi}'"
    )
    cfe_by_time = {p["time"]: p["c"] for p in cfe.get_points() if p.get("c") is not None}

    grid_cf_kwh = 0.0
    matched = 0
    for t, g_w in rows:
        c_pct = cfe_by_time.get(t)
        if c_pct is None:
            continue
        grid_cf_kwh += (g_w / 1000.0) * DT_HOURS * (float(c_pct) / 100.0)
        matched += 1

    return {
        "Cumulative_Grid_CFE_kWh": grid_cf_kwh,
        "Grid_CFE_Coverage": matched / len(rows),
    }


def _compute_derived_metrics(raw: dict[str, float], annotations: dict, days: int) -> dict[str, float]:
    """Compute CFE score, NPV, and LCOS from raw cumulative metrics and run parameters."""
    derived: dict[str, float] = {}

    # 24/7 CFE score: fraction of DC consumption matched by on-site carbon-free generation
    pv_kwh = raw.get("Cumulative_PV_Energy_kWh") or 0.0
    dc_kwh = raw.get("Cumulative_DC_Energy_kWh") or 0.0
    derived["CFE_Score"] = min(pv_kwh, dc_kwh) / dc_kwh if dc_kwh > 0 else 0.0

    # Grid carbon-free share (Electricity Maps): energy-weighted % of grid imports
    # that were carbon-free. Weighted by grid energy actually drawn, so unserved
    # load does not affect it — this is the "percentage from the grid".
    grid_kwh    = raw.get("Cumulative_Grid_Energy_kWh") or 0.0
    grid_cf_kwh = raw.get("Cumulative_Grid_CFE_kWh") or 0.0
    derived["Grid_CFE_Pct"] = (grid_cf_kwh / grid_kwh * 100.0) if grid_kwh > 0 else float("nan")

    # 24/7 CFE including the grid mix: on-site PV plus the carbon-free portion of
    # grid imports, matched against DC consumption (capped at 100%). Extends
    # CFE_Score, which credited PV only. Approximate: grid CF energy includes
    # imports that charged the battery, so this is an upper estimate of the
    # carbon-free energy reaching the DC; Grid_CFE_Pct is the exact grid figure.
    cfe_matched = min(pv_kwh, dc_kwh) + grid_cf_kwh
    derived["CFE_24x7_Score"] = min(1.0, cfe_matched / dc_kwh) if dc_kwh > 0 else 0.0

    # Carbon intensity per kWh served [gCO2/kWh]. The equal-service baseline
    # serves exactly the load the EMS served, so BOTH intensities use the same
    # served-energy denominator (DC - EMS unserved); this gives a clean per-kWh
    # comparison of dispatch timing and of the Scope-2 -> Scope-1 shift.
    uns_kwh       = raw.get("Cumulative_Unserved_kWh") or 0.0
    served_kwh    = max(0.0, dc_kwh - uns_kwh)
    carbon_g      = raw.get("Cumulative_Carbon_g") or 0.0
    es_carbon_g   = raw.get("Cumulative_EqualService_Carbon_g") or 0.0
    derived["Served_Energy_kWh"]          = served_kwh
    derived["CI_Served_gPerKWh"]          = carbon_g / served_kwh if served_kwh > 0 else float("nan")
    derived["EqualService_CI_Served_gPerKWh"] = es_carbon_g / served_kwh if served_kwh > 0 else float("nan")

    # BESS capacity from annotations (axis 2 provides capacity_mwh; default = reference 4 MWh)
    bess_mwh    = float(annotations.get("capacity_mwh", 4.0))
    bess_kwh    = bess_mwh * 1000.0
    bess_kw     = bess_kwh  # 1C nameplate

    capex       = bess_kwh * BESS_CAPEX_EUR_PER_KWH
    opex_yr     = bess_kw  * BESS_OPEX_EUR_PER_KW_YR

    # NPV uses the equal-service arbitrage saving (timing value at equal service),
    # which is the conservative "operational savings" figure. The reliability
    # value of the rescued load against the passive baseline is reported
    # separately as unserved-energy reduction, not monetised here.
    baseline_cost = raw.get("Cumulative_EqualService_Cost_EUR") or 0.0
    actual_cost   = raw.get("Cumulative_Cost_EUR") or 0.0
    savings_sim   = baseline_cost - actual_cost
    annual_savings = savings_sim * (365.0 / days)

    # Net Present Value over asset lifetime
    npv = -capex
    for t in range(1, NPV_LIFETIME_YR + 1):
        npv += (annual_savings - opex_yr) / (1.0 + NPV_DISCOUNT_RATE) ** t
    derived["NPV_EUR"] = npv

    # Levelized Cost of Storage: all-in cost per kWh discharged over lifetime
    discharge_sim      = raw.get("Cumulative_BESS_Discharge_kWh") or 0.0
    annual_discharge   = discharge_sim * (365.0 / days)
    lifetime_discharge = annual_discharge * NPV_LIFETIME_YR
    derived["LCOS_EUR_per_kWh"] = (
        (capex + NPV_LIFETIME_YR * opex_yr) / lifetime_discharge
        if lifetime_discharge > 0 else float("nan")
    )

    return derived


def _load_existing_rows(csv_path: Path) -> list[dict[str, Any]]:
    if not csv_path.exists():
        return []
    import csv as _csv
    with csv_path.open(newline="", encoding="utf-8") as fh:
        return list(_csv.DictReader(fh))


def run_axis(axis_key: str, base_esdl: Path, runs_dir: Path,
             results_csv: Path, days: int, start_date: str) -> None:
    specs = ALL_AXES[axis_key]
    influx = InfluxDBClient(host=INFLUX_HOST, port=INFLUX_PORT,
                            username=INFLUX_USER, password=INFLUX_PASS,
                            database=INFLUX_DB)

    runs_dir.mkdir(parents=True, exist_ok=True)
    results_csv.parent.mkdir(parents=True, exist_ok=True)

    # Resume support: pre-load any rows the CSV already has, then skip
    # specs whose label is already present. The skipped runs are not re-run
    # even if the previous run finished with an error — re-running is the
    # operator's job: delete the bad row from the CSV and rerun.
    rows: list[dict[str, Any]] = _load_existing_rows(results_csv)
    done_labels = {r.get("label") for r in rows}
    if done_labels:
        print(f"[{axis_key}] resume: skipping {len(done_labels)} already-recorded "
              f"runs ({sorted(done_labels)})")

    for i, spec in enumerate(specs, 1):
        if spec.label in done_labels:
            print(f"\n[{axis_key}] -- skip {i}/{len(specs)}: {spec.label} (already done) --")
            continue
        print(f"\n[{axis_key}] == run {i}/{len(specs)}: {spec.label} ==")
        cleanup_pods()

        variant = runs_dir / f"{axis_key}__{spec.label}.esdl"
        b64 = mutate_esdl(base_esdl, spec.overrides, variant)

        run_start = spec.start_date if spec.start_date is not None else start_date
        payload = _build_payload(b64, name=f"sw-{axis_key}-{spec.label}",
                                 days=days, start_date=run_start)
        try:
            r = requests.post(ORCH_URL, json=payload, timeout=60)
            r.raise_for_status()
        except requests.RequestException as e:
            print(f"  POST failed: {e} — skipping")
            continue
        sim_id = r.json()["simulation_id"]
        print(f"  -> simulation_id={sim_id}")

        try:
            final = _poll_until_done(sim_id)
        except TimeoutError as e:
            print(f"  {e} — skipping result collection")
            continue

        if "terminated successfully" not in final:
            print(f"  Run did not succeed (final='{final}') — still collecting any metrics")

        metrics = _query_cumulative(influx, sim_id)
        metrics.update(_query_grid_cfe(influx, sim_id))
        metrics.update(_compute_derived_metrics(metrics, spec.annotations, days))
        row: dict[str, Any] = {"label": spec.label, "sim_id": sim_id,
                               "final_status": final}
        row.update(spec.annotations)
        row.update(metrics)
        rows.append(row)

        # Persist incrementally so a mid-sweep crash doesn't lose work.
        _write_csv(results_csv, rows)

    print(f"\n[{axis_key}] done — wrote {len(rows)} rows to {results_csv}")


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    """Write rows to a CSV with proper quoting.

    Some fields (notably ``final_status``) embed commas, so we must use the
    csv module to quote them, otherwise the columns shift on read.
    """
    if not rows:
        return
    import csv as _csv
    cols: list[str] = []
    seen: set[str] = set()
    for r in rows:
        for k in r.keys():
            if k not in seen:
                cols.append(k)
                seen.add(k)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = _csv.DictWriter(fh, fieldnames=cols, quoting=_csv.QUOTE_MINIMAL,
                                 extrasaction="ignore")
        writer.writeheader()
        for r in rows:
            writer.writerow({c: ("" if r.get(c) is None else r.get(c)) for c in cols})


def main() -> None:
    ap = argparse.ArgumentParser(description="Run a sweep against the live DOTS orchestrator")
    ap.add_argument("axis", nargs="+", choices=list(ALL_AXES.keys()) + ["all"],
                    help="Which sweep axis/axes to execute (or 'all' for every axis)")
    ap.add_argument("--base-esdl",   default=str(HERE.parent / "datacenter_bess_scenario.esdl"))
    ap.add_argument("--runs-dir",    default=str(HERE / "runs"))
    ap.add_argument("--results-dir", default=str(HERE / "results"),
                    help="Per-axis CSV is written to <results-dir>/<axis>.csv")
    ap.add_argument("--days", type=int, default=60,
                    help="Simulation horizon in days (default 60 ≈ 2 months)")
    ap.add_argument("--start-date", default="2024-01-01 00:00:00",
                    help="Start of simulation horizon (YYYY-MM-DD HH:MM:SS)")
    args = ap.parse_args()

    axes = list(ALL_AXES.keys()) if "all" in args.axis else args.axis
    for ax in axes:
        out = Path(args.results_dir) / f"{ax}.csv"
        run_axis(ax, Path(args.base_esdl), Path(args.runs_dir), out,
                 args.days, args.start_date)


if __name__ == "__main__":
    main()
