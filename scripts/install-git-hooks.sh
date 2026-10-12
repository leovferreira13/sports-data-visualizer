#!/bin/sh
set -eu

if ! command -v git >/dev/null 2>&1 || ! git rev-parse --git-dir >/dev/null 2>&1; then
  exit 0
fi

git config core.hooksPath .githooks
chmod +x .githooks/pre-commit
