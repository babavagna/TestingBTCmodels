#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
python3 -m venv .venv
.venv/bin/python -m pip install --disable-pip-version-check -r requirements.txt
.venv/bin/python -m pip check
if command -v node >/dev/null && command -v npm >/dev/null; then
  (cd sources/full100/zenbot && npm_config_devdir="${TMPDIR:-/tmp}/btc-node-gyp" npm ci --cache "${TMPDIR:-/tmp}/btc-npm-cache" --no-audit --no-fund)
else
  echo 'Node.js and npm are needed only to rerun the Zenbot strategies. Saved reports still open.'
fi

.venv/bin/python -m pytest -q
