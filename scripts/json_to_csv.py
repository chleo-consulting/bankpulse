"""
json_to_csv.py — Convertit le JSON d'extract_labels.py en CSV.

Usage:
    uv run python scripts/json_to_csv.py <labels_json> [--output PATH]
"""

import argparse
import csv
import json
import sys
from pathlib import Path

COLUMNS = [
    "category_parent",
    "category",
    "cleaned_label",
    "supplier_found",
    "occurrence_count",
    "suggested_bankpulse_category",
    "raw_label_examples",
    "patterns_applied",
]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convertit le JSON d'extract_labels.py en CSV (sans patterns_applied)."
    )
    parser.add_argument("labels_json", type=Path, help="Fichier JSON produit par extract_labels.py")
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Chemin du CSV de sortie (défaut: même nom que le JSON avec extension .csv)",
    )
    args = parser.parse_args()

    if not args.labels_json.exists():
        sys.exit(f"Erreur: fichier introuvable {args.labels_json}")

    data = json.loads(args.labels_json.read_text(encoding="utf-8"))
    entries = data.get("entries")
    if not entries:
        sys.exit("Erreur: clé 'entries' absente ou vide dans le JSON.")

    out_path = args.output or args.labels_json.with_suffix(".csv")

    with out_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction="ignore")
        writer.writeheader()
        for entry in entries:
            row = {k: entry.get(k, "") for k in COLUMNS}
            row["raw_label_examples"] = " | ".join(entry.get("raw_label_examples") or [])
            row["patterns_applied"] = " | ".join(entry.get("patterns_applied") or [])
            writer.writerow(row)

    print(f"[json_to_csv] {len(entries)} entrées écrites dans {out_path}")


if __name__ == "__main__":
    main()
