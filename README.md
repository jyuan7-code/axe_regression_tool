# axe_regression_tool

Minimal regression helper for fulsim GSF tests.

## What it does

- discovers `.gsf` files under a test root
- runs a configurable fulsim command template for each test
- writes JSON baselines or compares against existing baselines
- optionally emits a JSON report for CI or local triage

## Usage

Write baselines:

```bash
python axe_regression_tool.py \
  --test-root /path/to/gsf-tests \
  --baseline-dir /path/to/baselines \
  --runner "fulsim {gsf}" \
  --write-baseline
```

Run regression comparison:

```bash
python axe_regression_tool.py \
  --test-root /path/to/gsf-tests \
  --baseline-dir /path/to/baselines \
  --runner "fulsim {gsf}" \
  --report-json /path/to/report.json
```