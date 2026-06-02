# Sweep automation for the thesis results chapter

This folder turns the parametric sweep design in `methods.tex` §scenario_definitions
into runnable Python and into `pgfplots` figure snippets that `zthesis/results.tex`
already `\input`s.

## Layout

| File | Purpose |
|---|---|
| `sweep_plans.py` | Declarative list of every run per axis (label + ESDL overrides). |
| `esdl_mutator.py` | Loads the base ESDL, applies overrides, writes a variant file + base64. |
| `live_runner.py` | Drives the DOTS orchestrator one axis at a time and pulls cumulative metrics from InfluxDB. |
| `synthesize_sweep.py` | Produces deterministic, plausible CSVs without running the federation — for figure pipeline development. |
| `make_figures.py` | Reads CSVs → writes `zthesis/figures/fig_axis*.tex` (pgfplots snippets). |
| `results/` | Per-axis CSV (one row per run). Live and synthetic backends share the schema. |
| `runs/` | One ESDL variant per live run (provenance). |

## Workflow

### 1. Build the figure pipeline today (synthetic backend)

```powershell
venv\Scripts\Activate.ps1
cd dots-services\dots-dc-simulation\sweep
python synthesize_sweep.py     # writes results/axis*.csv
python make_figures.py         # writes ..\..\..\zthesis\figures\fig_axis*.tex
```

`results.tex` already `\input`s the five figures. Build the thesis and verify
they render. The synthetic data follows the qualitative claims (convex Pareto,
saturating BESS marginal, scope-shift backup, etc.).

### 2. Replace synthetic with live data, one axis at a time

```powershell
# Prereqs: dots-kind cluster up, services pushed/loaded, InfluxDB seeded.
python live_runner.py axis1_pareto --days 14
python live_runner.py axis2_bess   --days 14
python live_runner.py axis3_pv     --days 14
python live_runner.py axis4_backup --days 14
python live_runner.py axis5_mpc    --days 14
python make_figures.py             # regenerate figures from live CSVs
```

The CSV schema (`label, <annotations>, Cumulative_Carbon_g, Cumulative_Cost_EUR,
Cumulative_Unserved_kWh, Cumulative_Baseline_Carbon_g, Cumulative_Baseline_Cost_EUR,
…`) is identical between the synthetic and live backends, so `make_figures.py`
does not need to know which produced the data.

### 3. LaTeX preamble

`results.tex` uses `\input{figures/fig_axis*.tex}`; those snippets use
`pgfplots` (axes 1–4) and the TikZ `patterns` library (axis 5 missing-data
hatching). Add this once to the document preamble (the `.cls` lives outside
this repo so it has to be done in the parent project):

```latex
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}
\usetikzlibrary{patterns}
```

## Adding a new sweep axis

1. Add the `RunSpec` list to `sweep_plans.py` and register it in `ALL_AXES`.
2. Add a synthesizer function in `synthesize_sweep.py` (only needed for
   pipeline development; live runs do not).
3. Add a renderer function in `make_figures.py` and call it from `make_all`.
4. Add `\input{figures/fig_axisN_<name>.tex}` to the relevant section of
   `results.tex`.
