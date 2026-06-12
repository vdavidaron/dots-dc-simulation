"""Declarative configuration of every sweep run.

Each axis is a list of ``RunSpec`` instances. ``RunSpec.overrides`` is the dict
passed verbatim to ``esdl_mutator.mutate_esdl``. Anything else (label, the
column it occupies in the output CSV) is metadata used by the synthesizer and
the figure generator.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class RunSpec:
    label: str
    overrides: dict[str, Any] = field(default_factory=dict)
    # Free-form annotations, used by the synthesizer and the plot generator.
    annotations: dict[str, Any] = field(default_factory=dict)
    # Optional per-run start date (YYYY-MM-DD HH:MM:SS); overrides the CLI
    # --start-date flag when set.  Used by AXIS6_SEASONAL.
    start_date: str | None = None


# ── Axis 1: objective-weight Pareto sweep ──────────────────────────────────
# Carbon vs price trade-off at fixed w_unserved. Held: BESS 4 MWh, full EMS.
AXIS1_PARETO: list[RunSpec] = [
    RunSpec("cost_only",  {"w_carbon": 0.0,  "w_price": 1.0},   {"omega_ratio": 0.0}),
    RunSpec("p_dominant", {"w_carbon": 0.1,  "w_price": 1.0},   {"omega_ratio": 0.1}),
    RunSpec("p_strong",   {"w_carbon": 0.33, "w_price": 1.0},   {"omega_ratio": 0.33}),
    RunSpec("balanced",   {"w_carbon": 1.0,  "w_price": 1.0},   {"omega_ratio": 1.0}),
    RunSpec("c_strong",   {"w_carbon": 1.0,  "w_price": 0.33},  {"omega_ratio": 3.0}),
    RunSpec("c_dominant", {"w_carbon": 1.0,  "w_price": 0.1},   {"omega_ratio": 10.0}),
    RunSpec("carbon_only",{"w_carbon": 1.0,  "w_price": 0.0},   {"omega_ratio": float("inf")}),
]

# ── Axis 2: BESS sizing sweep (RQ2) ────────────────────────────────────────
AXIS2_BESS: list[RunSpec] = [
    RunSpec(f"bess_{mwh}MWh", {
        "battery_capacity_wh": mwh * 1e6,
        "battery_max_rate_w":  mwh * 1e6,            # 1C rating
        "enable_battery":      0.0 if mwh == 0 else 1.0,
        # Carbon-anchored objective per methods.tex §scenario_definitions
        "w_carbon": 1.0, "w_price": 0.0,
    }, {"capacity_mwh": float(mwh)})
    for mwh in (0, 1, 2, 4, 8, 16)
]

# ── Axis 3 & 4: PV × backup grid (RQ3) ─────────────────────────────────────
AXIS3_PV: list[RunSpec] = [
    RunSpec(f"pv_{int(mw*1000)}kW", {
        "pv_power_w":              mw * 1e6,
        "enable_renewable_service": 0.0 if mw == 0 else 1.0,
        "w_carbon": 1.0, "w_price": 0.0,
    }, {"pv_mw": mw})
    for mw in (0.0, 0.5, 1.0, 2.0, 5.0)
]

AXIS4_BACKUP: list[RunSpec] = [
    RunSpec(f"bk_{mw}MW", {
        "backup_power_w":          mw * 1e6,
        "enable_backup_generator": 0.0 if mw == 0 else 1.0,
        "w_carbon": 1.0, "w_price": 0.0,
    }, {"backup_mw": float(mw)})
    for mw in (0, 2, 5, 10)
]

# ── Axis 5: MPC deviation-threshold sweep (RQ4) ────────────────────────────
AXIS5_MPC: list[RunSpec] = []
for drift in (1.0, 5.0, 10.0, 20.0):
    for spike in (0.05, 0.10, 0.20, 0.50):
        AXIS5_MPC.append(RunSpec(
            f"mpc_d{drift:g}_s{spike:g}",
            {
                "enable_change_management":   1.0,
                "mpc_soc_drift_threshold":    drift,
                "mpc_demand_spike_threshold": spike,
                "w_carbon": 1.0, "w_price": 1.0,
            },
            {"drift_pct": drift, "spike_frac": spike},
        ))

# Static-plan baseline counterpoint for RQ4
AXIS5_STATIC = RunSpec(
    "mpc_static",
    {"enable_change_management": 0.0, "w_carbon": 1.0, "w_price": 1.0},
    {"drift_pct": None, "spike_frac": None, "is_static": True},
)


# ── Axis 6: Seasonal sensitivity (reference config, four 60-day windows) ──────
# All overrides are empty — the base ESDL reference scenario is used unchanged.
# Only the simulation start date shifts so the live InfluxDB signals (CI, price,
# PV irradiance, demand trace) reflect the correct season.
AXIS6_SEASONAL: list[RunSpec] = [
    RunSpec("winter", {}, {"season": "winter", "month_label": "Jan–Feb"},
            start_date="2024-01-01 00:00:00"),
    RunSpec("spring", {}, {"season": "spring", "month_label": "Apr–May"},
            start_date="2024-04-01 00:00:00"),
    RunSpec("summer", {}, {"season": "summer", "month_label": "Jul–Aug"},
            start_date="2024-07-01 00:00:00"),
    RunSpec("autumn", {}, {"season": "autumn", "month_label": "Oct–Nov"},
            start_date="2024-10-01 00:00:00"),
]


# ── Axis 7: Seasonal × weight-ratio cross-product (supplementary) ─────────────
# Each of the 7 AXIS1 weight configurations is run across all 4 seasonal windows,
# producing 28 runs that characterise how the optimal objective weighting varies
# by season (PV availability, CI spread, electricity-price spread).
_WEIGHT_CONFIGS = [
    ("cost_only",    {"w_carbon": 0.0,  "w_price": 1.0},  0.0),
    ("p_dominant",   {"w_carbon": 0.1,  "w_price": 1.0},  0.1),
    ("p_strong",     {"w_carbon": 0.33, "w_price": 1.0},  0.33),
    ("balanced",     {"w_carbon": 1.0,  "w_price": 1.0},  1.0),
    ("c_strong",     {"w_carbon": 1.0,  "w_price": 0.33}, 3.0),
    ("c_dominant",   {"w_carbon": 1.0,  "w_price": 0.1},  10.0),
    ("carbon_only",  {"w_carbon": 1.0,  "w_price": 0.0},  float("inf")),
]
_SEASONAL_CONFIGS = [
    ("winter", "Jan–Feb", "2024-01-01 00:00:00"),
    ("spring", "Apr–May", "2024-04-01 00:00:00"),
    ("summer", "Jul–Aug", "2024-07-01 00:00:00"),
    ("autumn", "Oct–Nov", "2024-10-01 00:00:00"),
]

AXIS7_SEASONAL_PARETO: list[RunSpec] = [
    RunSpec(
        label=f"{season}__{wlabel}",
        overrides=overrides,
        annotations={
            "season": season,
            "month_label": month_label,
            "omega_ratio": ratio,
            "weight_label": wlabel,
        },
        start_date=start_date,
    )
    for season, month_label, start_date in _SEASONAL_CONFIGS
    for wlabel, overrides, ratio in _WEIGHT_CONFIGS
]


# ── Axis 8: Transformer (grid connection) capacity sweep — curtailment severity ──
# Reduces the firm grid limit toward/below the 4 MW DC load to force curtailment,
# drive the battery to depletion, and dispatch the backup generator. This is the
# scenario that finally exercises the Scope-1/Scope-2 shift of RQ3, which the
# reference 10 MW connection never triggers. Carbon-anchored, backup enabled.
AXIS8_GRIDLIMIT: list[RunSpec] = [
    RunSpec(f"grid_{mw}MW", {
        "grid_power_w":            mw * 1e6,
        "enable_backup_generator": 1.0,
        "w_carbon": 1.0, "w_price": 0.0,
    }, {"grid_mw": float(mw)})
    for mw in (2, 3, 4, 6, 10)
]

# ── Axis 9: Multi-seed Monte Carlo — single-seed robustness (RQ4) ──
# Repeats the MPC reference configuration and the static-plan baseline across
# several seeds. With real recorded input traces the sim_seed only perturbs the
# synthetic fallbacks, so the effective per-run variation comes from
# forecast_seed (the forecast-error realisation that drives replanning); both are
# varied together so each run is one independent realisation. Lets the MPC
# unserved-load gain be reported as a distribution with a significance check
# rather than a single-seed point estimate.
_SEED_VALUES = [42, 7, 123, 2024, 99]
AXIS9_SEED: list[RunSpec] = []
for _sd in _SEED_VALUES:
    _common = {"sim_seed": float(_sd), "forecast_seed": float(_sd),
               "w_carbon": 1.0, "w_price": 1.0}
    AXIS9_SEED.append(RunSpec(
        f"mpc_seed{_sd}",
        {**_common, "enable_change_management": 1.0,
         "mpc_soc_drift_threshold": 5.0, "mpc_demand_spike_threshold": 0.10},
        {"seed": _sd, "variant": "mpc"}))
    AXIS9_SEED.append(RunSpec(
        f"static_seed{_sd}",
        {**_common, "enable_change_management": 0.0},
        {"seed": _sd, "variant": "static"}))


# ── Axis 10: SOC-baseline penalty × weight ratio — does w_soc_low flatten RQ1? ──
# The weak weight sensitivity of Axis 1 has two candidate causes: carbon/price
# co-directionality, and the SOC-baseline penalty w_soc_low (default 1e6)
# dominating the externality terms so the LP has little freedom left to express
# the weight ratio. This axis crosses three w_soc_low levels (default, relaxed,
# off) with the two extreme weight settings (cost-only vs carbon-only). If the
# carbon spread between cost-only and carbon-only widens as w_soc_low falls, the
# pinning is a genuine co-cause; if it stays flat, co-directionality alone
# explains the insensitivity. Reference physical config, 4 MWh BESS.
AXIS10_SOCBASE: list[RunSpec] = [
    RunSpec(f"soc{_wsl:g}_{_wl}", {
        "w_soc_low": _wsl,
        "w_carbon": _wc, "w_price": _wp,
    }, {"w_soc_low": _wsl, "weight_label": _wl})
    for _wsl in (1e6, 1e2, 0.0)
    for _wl, _wc, _wp in (("cost_only", 0.0, 1.0), ("carbon_only", 1.0, 0.0))
]


ALL_AXES = {
    "axis1_pareto":          AXIS1_PARETO,
    "axis2_bess":            AXIS2_BESS,
    "axis3_pv":              AXIS3_PV,
    "axis4_backup":          AXIS4_BACKUP,
    "axis5_mpc":             AXIS5_MPC + [AXIS5_STATIC],
    "axis10_socbase":        AXIS10_SOCBASE,
    "axis6_seasonal":        AXIS6_SEASONAL,
    "axis7_seasonal_pareto": AXIS7_SEASONAL_PARETO,
    "axis8_gridlimit":       AXIS8_GRIDLIMIT,
    "axis9_seed":            AXIS9_SEED,
}
