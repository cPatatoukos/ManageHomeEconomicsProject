from __future__ import annotations

import sys


def _check_deps() -> None:
    missing: list[str] = []
    for pkg, pip_name in (("matplotlib", "matplotlib"), ("openpyxl", "openpyxl")):
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pip_name)
    if not missing:
        return
    in_venv = hasattr(sys, "base_prefix") and sys.prefix != sys.base_prefix
    print("Λείπουν βιβλιοθήκες:", ", ".join(missing))
    if in_venv:
        print("\nΕγκατάσταση:\n  pip install -r requirements.txt")
    else:
        print(
            "\nΧρησιμοποιείς system Python χωρίς τα packages του project.\n"
            "Τρέξε με virtual environment:\n\n"
            "  python3 -m venv .venv\n"
            "  source .venv/bin/activate\n"
            "  pip install -r requirements.txt\n"
            "  python main.py\n\n"
            "Ή απευθείας:\n"
            "  .venv/bin/python main.py"
        )
    sys.exit(1)


def main() -> None:
    _check_deps()
    from database import DEFAULT_DB_PATH, FinanceDB
    from gui import run_app

    db = FinanceDB(DEFAULT_DB_PATH)
    db.initialize()
    db.seed_default_categories()
    run_app(db)


if __name__ == "__main__":
    main()
