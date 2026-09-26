#!/usr/bin/env bash
set -euo pipefail

echo "Running pre-commit application checks..."

npm run lint
npm run typecheck
python3 scripts/check_markdown_language.py
bash -n scripts/check-localization.sh
bash -n scripts/install-git-hooks.sh
bash -n scripts/check-precommit.sh

echo "Pre-commit application checks passed."
