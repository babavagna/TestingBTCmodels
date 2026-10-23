#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
if [[ ! -x .venv/bin/python ]]; then
  echo 'First run: bash setup.sh'
  exit 1
fi
exec .venv/bin/python -m streamlit run app.py --server.headless=true --browser.gatherUsageStats=false "$@"
