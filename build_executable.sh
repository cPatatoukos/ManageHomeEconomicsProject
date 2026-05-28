#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"

if [ ! -x .venv/bin/python ]; then
  echo "Δημιουργία virtual environment..."
  python3 -m venv .venv
  .venv/bin/pip install -r requirements.txt
fi

echo "Εγκατάσταση PyInstaller..."
.venv/bin/pip install -q pyinstaller

echo "Δημιουργία executable..."
export MPLCONFIGDIR="${MPLCONFIGDIR:-$(pwd)/.mplconfig}"
mkdir -p "$MPLCONFIGDIR"
.venv/bin/pyinstaller --noconfirm --clean finance_app.spec

echo ""
echo "Έτοιμο:"
echo "  macOS app:  dist/FamilyFinance.app"
echo "  CLI binary: dist/FamilyFinance/FamilyFinance"
echo ""
echo "Η βάση δεδομένων αποθηκεύεται στο:"
echo "  ~/Library/Application Support/FamilyFinance/finance.db"
