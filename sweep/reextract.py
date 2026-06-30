"""Recompute the sweep result CSVs from existing InfluxDB data WITHOUT re-running
the simulations.

Use this after changing a *post-processable* metric definition (here: switching
the counterfactual to the equal-service, naive-timing baseline (B)) so you do not
pay for a full 60-day federation re-run. For every completed run recorded in
``results/<axis>.csv`` it recovers the ``sim_id``, re-queries InfluxDB for that
simulation, recomputes the baseline and derived metrics, and rewrites the CSV in
place. All per-step series it needs (carbon intensity, price, PV, served load)
are already logged by the Network Balancer, so nothing has to be simulated again.

Run:
    python reextract.py                # every results/*.csv
    python reextract.py axis2_bess     # one or more named axes
"""
from __future__ import annotations

import sys
from pathlib import Path

from influxdb import InfluxDBClient

import live_runner as lr  # reuse InfluxDB config + query/derive/write helpers

DT_HOURS = 0.25  # 15-minute dispatch step
DAYS = 60        # simulation horizon used by the sweep (matches live_runner default)

# Columns that re-extraction regenerates. Every *other* column in the original
# row (label, sim_id, final_status, and the per-axis annotations such as
# omega_ratio / capacity_mwh / season) is preserved untouched.
_REGEN = set(lr.METRIC_FIELDS) | {
    "Replan_Count", "Min_SOC_Overall", "Min_SOC_During_Curtailment",
    "Grid_Compliance_Rate", "CFE_Score", "NPV_EUR", "LCOS_EUR_per_kWh",
    "Served_Energy_kWh", "CI_Served_gPerKWh", "EqualService_CI_Served_gPerKWh",
    "Cumulative_Grid_CFE_kWh", "Grid_CFE_Coverage", "Grid_CFE_Pct", "CFE_24x7_Score",
    # legacy single-baseline columns, dropped on rewrite
    "Cumulative_Baseline_Carbon_g", "Cumulative_Baseline_Cost_EUR",
    "Cumulative_Baseline_Unserved_kWh", "Baseline_CI_Served_gPerKWh",
}


def query_baselines(client: InfluxDBClient, sim_id: str) -> dict[str, float]:
    """Recompute both counterfactual baselines from the per-step series.

    EQUAL-SERVICE: serves exactly the load the EMS served
    (``served_datacenter_power_w``) from PV then grid at the spot CI/price, no
    battery. PASSIVE: same PV and grid limit but no battery, so it serves net
    load (demand - PV) up to the per-step grid limit and sheds the rest. The grid
    limit is read from the PowerPlant measurement and aligned by timestamp.
    Returns the six cumulative baseline metrics.
    """
    en = client.query(
        'SELECT "Carbon_Intensity" AS ci, "Electricity_Price_EUR_per_MWh" AS price, '
        '"PV_Generation_W" AS pv, "served_datacenter_power_w" AS served, '
        '"Total_Routed_Demand_W" AS demand '
        'FROM "ElectricityNetwork" '
        f"WHERE \"simulation_id\" = '{sim_id}'"
    )
    # Per-step grid import limit lives in the PowerPlant measurement.
    pp = client.query(
        'SELECT "Actual_Power_Limit_W" AS lim FROM "PowerPlant" '
        f"WHERE \"simulation_id\" = '{sim_id}'"
    )
    limit_by_time = {p["time"]: p.get("lim") for p in pp.get_points()}

    es_carbon = es_cost = es_uns = 0.0
    pa_carbon = pa_cost = pa_uns = 0.0
    n = 0
    for p in en.get_points():
        ci, served, demand = p.get("ci"), p.get("served"), p.get("demand")
        if ci is None or served is None or demand is None:
            continue
        price = p.get("price") or 0.0
        pv_kw = (p.get("pv") or 0.0) / 1000.0
        served_kw = served / 1000.0
        demand_kw = demand / 1000.0

        # Equal-service: serve the EMS-served load, naive timing, no battery.
        es_grid = max(0.0, served_kw - pv_kw)
        es_carbon += ci * es_grid * DT_HOURS
        es_cost   += price * es_grid * DT_HOURS / 1000.0
        es_uns    += max(0.0, demand_kw - served_kw) * DT_HOURS

        # Passive: serve net load up to the grid limit, shed the rest, no battery.
        lim_w = limit_by_time.get(p["time"])
        lim_kw = (lim_w / 1000.0) if lim_w is not None else float("inf")
        net_kw = max(0.0, demand_kw - pv_kw)
        pa_grid = min(net_kw, lim_kw)
        pa_carbon += ci * pa_grid * DT_HOURS
        pa_cost   += price * pa_grid * DT_HOURS / 1000.0
        pa_uns    += max(0.0, net_kw - lim_kw) * DT_HOURS
        n += 1

    if n == 0:
        nan = float("nan")
        return {k: nan for k in (
            "Cumulative_EqualService_Carbon_g", "Cumulative_EqualService_Cost_EUR",
            "Cumulative_EqualService_Unserved_kWh", "Cumulative_Passive_Carbon_g",
            "Cumulative_Passive_Cost_EUR", "Cumulative_Passive_Unserved_kWh")}
    return {
        "Cumulative_EqualService_Carbon_g": es_carbon,
        "Cumulative_EqualService_Cost_EUR": es_cost,
        "Cumulative_EqualService_Unserved_kWh": es_uns,
        "Cumulative_Passive_Carbon_g": pa_carbon,
        "Cumulative_Passive_Cost_EUR": pa_cost,
        "Cumulative_Passive_Unserved_kWh": pa_uns,
    }


def reextract_axis(client: InfluxDBClient, csv_path: Path) -> None:
    rows = lr._load_existing_rows(csv_path)
    if not rows:
        print(f"  [skip] {csv_path.name}: no rows")
        return
    new_rows: list[dict] = []
    for r in rows:
        sim_id = (r.get("sim_id") or "").strip()
        if not sim_id:
            new_rows.append(r)
            continue
        metrics = lr._query_cumulative(client, sim_id)
        # Recompute both counterfactual baselines from the per-step series.
        metrics.update(query_baselines(client, sim_id))
        # Grid carbon-free share from the seeded Electricity Maps CFE series.
        metrics.update(lr._query_grid_cfe(client, sim_id))
        # Derived metrics (CFE, NPV, LCOS, served-energy carbon intensity) use the
        # row itself as the annotation source (capacity_mwh etc.).
        metrics.update(lr._compute_derived_metrics(metrics, r, DAYS))
        merged = {k: v for k, v in r.items() if k not in _REGEN}
        merged.update(metrics)
        new_rows.append(merged)

        ems_c = metrics.get("Cumulative_Carbon_g", float("nan")) / 1e6
        nb_carbon = metrics.get("Cumulative_EqualService_Carbon_g", float("nan"))
        save_c = ((nb_carbon - metrics.get("Cumulative_Carbon_g", 0.0)) / nb_carbon * 100
                  if nb_carbon and nb_carbon == nb_carbon else float("nan"))
        print(f"  {csv_path.name:>26} {str(r.get('label')):>18}: "
              f"EMS={ems_c:6.1f} tCO2  baseline(B)={nb_carbon/1e6:6.1f} tCO2  "
              f"carbon saving={save_c:5.1f}%")
    lr._write_csv(csv_path, new_rows)
    print(f"  [ok] rewrote {csv_path.name} ({len(new_rows)} rows)")


def main() -> None:
    results = lr.HERE / "results"
    client = InfluxDBClient(
        host=lr.INFLUX_HOST, port=lr.INFLUX_PORT,
        username=lr.INFLUX_USER, password=lr.INFLUX_PASS,
        database=lr.INFLUX_DB,
    )
    if len(sys.argv) > 1:
        paths = [results / f"{a}.csv" for a in sys.argv[1:]]
    else:
        paths = sorted(results.glob("*.csv"))
    for p in paths:
        print(f"[reextract] {p.name}")
        reextract_axis(client, p)
    print("\nDone. Now regenerate figures:  python make_figures.py")


if __name__ == "__main__":
    main()
