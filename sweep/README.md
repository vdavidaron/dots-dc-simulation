# Sweep automation for the thesis results chapter

This folder turns the parametric sweep design in `methods.tex` into runnable
Python and into `pgfplots` figure snippets that `zthesis/results.tex` already
`\input`s. Every figure and table in the results chapter is generated from the
CSVs here.

## Layout

| File | Purpose |
|---|---|
| `sweep_plans.py` | Declarative list of every run per axis (label + ESDL overrides + annotations). `ALL_AXES` registers them. |
| `esdl_mutator.py` | Loads the base ESDL, applies a run's overrides, writes a variant file and returns base64. The override allow-list also defines which KPIs/assets a sweep may touch. |
| `live_runner.py` | Drives the DOTS orchestrator one axis at a time, polls until each run terminates, and pulls cumulative metrics from InfluxDB into `results/<axis>.csv`. Also computes the derived metrics (CFE, NPV, LCOS, served-energy CI). |
| `reextract.py` | Recomputes the CSVs from **existing** InfluxDB data without re-running the federation. Use after changing a post-processable metric definition (e.g. a baseline). |
| `make_figures.py` | Reads `results/*.csv` and writes `zthesis/figures/fig_axis*.tex` and the `tab_*.tex` tables. |
| `results/` | One CSV per axis (one row per run). |
| `runs/` | One ESDL variant per live run (provenance). |

## Axes

| Axis | RQ | Varies |
|---|---|---|
| `axis1_pareto` | RQ1 | objective weight ratio `w_carbon/w_price` |
| `axis2_bess` | RQ2 | BESS nameplate capacity (0–16 MWh) |
| `axis3_pv` | RQ3 | PV nameplate capacity (0–5 MW) |
| `axis4_backup` | RQ3 | backup generator capacity (0–10 MW) |
| `axis5_mpc` | RQ4 | MPC SOC-drift × demand-spike thresholds (+ static-plan) |
| `axis6_seasonal` | — | reference config across four seasonal windows |
| `axis7_seasonal_pareto` | — | weight ratio × season (28 runs) |
| `axis8_gridlimit` | RQ3 | grid connection capacity (2–10 MW); exercises the Scope-2→Scope-1 shift |
| `axis9_seed` | RQ4 | 5 seeds × {MPC, static}; multi-seed robustness |
| `axis10_socbase` | RQ1 | SOC-baseline penalty `w_soc_low` × {cost-only, carbon-only} |

## Two counterfactual baselines

Each run logs two fully-specified baselines, each with the carbon / cost /
unserved triple, so the comparison is never ambiguous:

- **Equal-service** (`Cumulative_EqualService_*`): serves exactly the load the
  EMS served, met from PV then grid at the spot CI/price of the moment, with no
  battery. Isolates the carbon/cost value of dispatch *timing* at equal service;
  its unserved equals the EMS's by construction. Used for the carbon/cost
  savings and the NPV.
- **Passive** (`Cumulative_Passive_*`): same PV and grid limit but no battery,
  shedding whatever net load exceeds the limit. The "do nothing" deployment
  reference; the gap to the EMS on unserved is the load the battery rescues.
  Used for the reliability comparison.

## Workflow

```powershell
venv\Scripts\Activate.ps1
cd dots-services\dots-dc-simulation\sweep

# run one or more axes (orchestrator + seeded InfluxDB must be up)
python live_runner.py axis1_pareto axis2_bess --days 60

# regenerate all figures and tables from the CSVs
python make_figures.py
```

### Re-extract instead of re-running

If you only changed a post-processable metric (a baseline definition, a derived
metric) and the runs are still in InfluxDB, recompute the CSVs in place rather
than paying for a fresh 60-day federation:

```powershell
python reextract.py                 # all axes
python reextract.py axis2_bess      # one or more
python make_figures.py
```

`reextract.py` re-queries each run by `sim_id` and rebuilds both baselines from
the per-step series, so it only works while the run's data is still present.
Genuine simulation changes (anything the federates compute, e.g. the PV mapping
or backup dispatch) require a real re-run on a rebuilt image.

## LaTeX preamble

`results.tex` uses `\input{figures/fig_axis*.tex}`; those snippets use
`pgfplots` and the TikZ `patterns` library. Add once to the parent document's
preamble:

```latex
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}
\usetikzlibrary{patterns}
```

## Adding a new sweep axis

1. Add the `RunSpec` list to `sweep_plans.py` and register it in `ALL_AXES`.
2. If it varies an ESDL KPI or asset attribute not already handled, add the key
   to `esdl_mutator.py` (`NETWORK_KPI_KEYS` or a new `_set_asset_attr` branch),
   and add the KPI to `datacenter_bess_scenario.py` so the base ESDL carries it.
3. Add a renderer function in `make_figures.py` and call it from `make_all`.
4. Add `\input{figures/fig_axisN_<name>.tex}` to the relevant section of
   `results.tex` and a row to `tab_sweep_axes`.
