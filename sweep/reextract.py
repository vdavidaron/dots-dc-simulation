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
    "Served_Energy_kWh", "CI_Served_gPerKWh", "Baseline_CI_Served_gPerKWh",
}


def query_naive_baseline(client: InfluxDBClient, sim_id: str) -> tuple[float, float]:
    """Baseline (B): equal-service, naive-timing counterfactual.

    Integrated from the per-step series. The baseline serves exactly the load the
    EMS served (``served_datacenter_power_w``), meeting it instantaneously from PV
    then grid at the spot carbon intensity / price of the step it is consumed,
    with no battery time-shifting. Returns (carbon_gCO2, cost_EUR).
    """
    q = (
        'SELECT "Carbon_Intensity" AS ci, '
        '"Electricity_Price_EUR_per_MWh" AS price, '
        '"PV_Generation_W" AS pv, '
        '"served_datacenter_power_w" AS served '
        'FROM "ElectricityNetwork" '
        f"WHERE \"simulation_id\" = '{sim_id}'"
    )
    rs = client.query(q)
    carbon_g = 0.0
    cost_eur = 0.0
    n = 0
    for p in rs.get_points():
        ci = p.get("ci")
        served = p.get("served")
        if ci is None or served is None:
            continue
        pv_kw = (p.get("pv") or 0.0) / 1000.0
        served_kw = served / 1000.0
        naive_grid_kw = max(0.0, served_kw - pv_kw)
        carbon_g += ci * naive_grid_kw * DT_HOURS
        price = p.get("price")
        if price is not None:
            cost_eur += price * naive_grid_kw * DT_HOURS / 1000.0
        n += 1
    if n == 0:
        return float("nan"), float("nan")
    return carbon_g, cost_eur


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
        # Switch to baseline (B): equal-service, naive-timing (post-processed).
        nb_carbon, nb_cost = query_naive_baseline(client, sim_id)
        metrics["Cumulative_Baseline_Carbon_g"] = nb_carbon
        metrics["Cumulative_Baseline_Cost_EUR"] = nb_cost
        # Derived metrics (CFE, NPV, LCOS, served-energy carbon intensity) use the
        # row itself as the annotation source (capacity_mwh etc.).
        metrics.update(lr._compute_derived_metrics(metrics, r, DAYS))
        merged = {k: v for k, v in r.items() if k not in _REGEN}
        merged.update(metrics)
        new_rows.append(merged)

        ems_c = metrics.get("Cumulative_Carbon_g", float("nan")) / 1e6
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
