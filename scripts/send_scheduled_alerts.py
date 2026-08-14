#!/usr/bin/env python3
"""Envía alertas de stock programadas (cron / GitHub Actions)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import utils.ssl_fix  # noqa: F401 — certificados SSL en Windows

from dotenv import load_dotenv

load_dotenv(ROOT / ".env", override=True)

from services.alert_scheduler import run_scheduled_alert_job  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Envío programado de alertas de stock.")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Ignora horario y envía ahora (no registra en historial).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Imprime el resultado como JSON.",
    )
    args = parser.parse_args()

    result = run_scheduled_alert_job(force=args.force)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif result.get("skipped"):
        print(result.get("reason", "Omitido."))
    elif result.get("ok"):
        print(
            f"OK: enviado a {len(result.get('recipients', []))} destinatario(s), "
            f"{result.get('products', 0)} producto(s) en alerta."
        )
    else:
        print(result.get("reason", "Error desconocido."), file=sys.stderr)

    if result.get("skipped"):
        return 0
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
