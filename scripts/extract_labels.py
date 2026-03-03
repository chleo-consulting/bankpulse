"""
extract_labels.py — Extraction des labels/marchands depuis les exports CSV Boursorama.

Usage:
    uv run python scripts/extract_labels.py <csv_file_or_dir> [--output PATH] [--include-uncategorized]

Produit un fichier JSON avec les labels nettoyés groupés par catégorie Boursorama,
à valider manuellement avant de générer les règles avec generate_rules.py.
"""

import argparse
import csv
import io
import json
import re
import sys
from datetime import datetime
from pathlib import Path

# ── Patterns bruit appliqués séquentiellement ────────────────────────────────
# Ordre important : préfixes d'abord, puis suffixes
NOISE_PATTERNS: list[tuple[str, re.Pattern]] = [
    # Préfixes
    ("carte_date", re.compile(r"^CARTE\s+\d{2}/\d{2}/\d{2,4}\s+", re.IGNORECASE)),
    ("prlv_sepa", re.compile(r"^PRLV\s+SEPA\s+", re.IGNORECASE)),
    ("vir_sepa", re.compile(r"^VIR\s+SEPA\s+", re.IGNORECASE)),
    ("vir_inst", re.compile(r"^VIR\s+INST\s+", re.IGNORECASE)),
    ("vir_generic", re.compile(r"^VIR\s+", re.IGNORECASE)),
    ("avoir_date", re.compile(r"^AVOIR\s+\d{2}/\d{2}/\d{2,4}\s+", re.IGNORECASE)),
    ("retrait_dab", re.compile(r"^RETRAIT\s+DAB\s+\d{2}/\d{2}/\d{2,4}\s+", re.IGNORECASE)),
    ("star_prefix", re.compile(r"^\*")),
    # Suffixes
    ("cb_id", re.compile(r"\s+CB\*\w+$", re.IGNORECASE)),
    ("ref_num", re.compile(r"\s+\d{5,}$")),
]

# Catégories toujours exclues (mouvements internes, en attente)
ALWAYS_EXCLUDED_CATEGORIES: set[str] = {
    "Autorisation paiement / retrait en cours",
    "Prélèvements cartes débit différé et cartes crédit conso",
    "Virements émis de comptes à comptes",
    "Virements reçus de comptes à comptes",
    "Mouvements internes débiteurs",
    "Mouvements internes créditeurs",
}

# Catégories exclues par défaut (option --include-uncategorized pour override)
DEFAULT_EXCLUDED_CATEGORIES: set[str] = {
    "Non catégorisé",
}

REQUIRED_COLUMNS: set[str] = {"label", "category", "categoryParent", "supplierFound"}

BANKPULSE_CATEGORIES_REFERENCE: dict = {
    "parents": [
        "Alimentation",
        "Transport",
        "Logement",
        "Loisirs & Culture",
        "Sante",
        "Shopping",
        "Services & Abonnements",
        "Revenus",
    ],
    "children": {
        "Alimentation": ["Supermarche", "Restaurant", "Fast food"],
        "Transport": ["Essence", "Transports en commun", "Taxi & VTC"],
        "Logement": ["Loyer", "Charges"],
        "Loisirs & Culture": ["Sport & Fitness", "Streaming & Jeux", "Cinema"],
        "Sante": ["Medecin", "Pharmacie"],
        "Shopping": ["Vetements", "High-tech"],
        "Services & Abonnements": ["Telephonie", "Assurances", "Banque & Frais"],
        "Revenus": ["Salaire", "Remboursements"],
    },
}


def _decode_content(raw: bytes) -> str:
    for encoding in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("latin-1", errors="replace")


def extract_raw_label(label_field: str) -> str:
    """Extrait le label brut depuis le format 'Titre Friendly | LABEL BRUT'."""
    if " | " in label_field:
        return label_field.split(" | ", maxsplit=1)[1].strip()
    return label_field.strip()


def clean_label(label: str) -> tuple[str, list[str]]:
    """Applique les patterns bruit séquentiellement. Retourne (cleaned, patterns_appliqués)."""
    cleaned = label
    applied: list[str] = []
    for name, pattern in NOISE_PATTERNS:
        result = pattern.sub("", cleaned).strip()
        if result != cleaned:
            applied.append(name)
            cleaned = result
    return cleaned, applied


def validate_columns(fieldnames: list[str] | None, filepath: str) -> None:
    if not fieldnames:
        raise ValueError(f"{filepath}: fichier vide ou sans en-tête")
    missing = REQUIRED_COLUMNS - set(fieldnames)
    if missing:
        raise ValueError(f"{filepath}: colonnes manquantes {missing}")


def parse_csv_file(
    filepath: Path, include_uncategorized: bool
) -> list[dict]:
    text = _decode_content(filepath.read_bytes())

    reader = csv.DictReader(io.StringIO(text), delimiter=";")
    validate_columns(reader.fieldnames, str(filepath))

    excluded = ALWAYS_EXCLUDED_CATEGORIES.copy()
    if not include_uncategorized:
        excluded |= DEFAULT_EXCLUDED_CATEGORIES

    rows: list[dict] = []
    for row in reader:
        label_field = (row.get("label") or "").strip()
        category = (row.get("category") or "").strip()
        category_parent = (row.get("categoryParent") or "").strip()
        supplier = (row.get("supplierFound") or "").strip()

        if not label_field or not category:
            continue
        if category in excluded:
            continue

        raw_label = extract_raw_label(label_field)
        if not raw_label:
            continue

        cleaned, patterns_applied = clean_label(raw_label)

        rows.append(
            {
                "raw_label": raw_label,
                "cleaned_label": cleaned,
                "patterns_applied": patterns_applied,
                "supplier_found": supplier,
                "category": category,
                "category_parent": category_parent,
            }
        )

    return rows


def deduplicate(rows: list[dict]) -> list[dict]:
    """Déduplique par (category, category_parent, supplier/cleaned_label), agrège occurrence_count."""
    seen: dict[tuple, dict] = {}

    for row in rows:
        dedup_key = row["supplier_found"].lower() if row["supplier_found"] else row["cleaned_label"].lower()
        key = (row["category"], row["category_parent"], dedup_key)
        if key not in seen:
            seen[key] = {
                "category": row["category"],
                "category_parent": row["category_parent"],
                "cleaned_label": row["cleaned_label"],
                "supplier_found": row["supplier_found"],
                "patterns_applied": row["patterns_applied"],
                "occurrence_count": 1,
                "raw_label_examples": [row["raw_label"]],
                "suggested_bankpulse_category": None,
            }
        else:
            entry = seen[key]
            entry["occurrence_count"] += 1
            if (
                len(entry["raw_label_examples"]) < 3
                and row["raw_label"] not in entry["raw_label_examples"]
            ):
                entry["raw_label_examples"].append(row["raw_label"])

    return list(seen.values())


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extrait les labels/marchands des exports CSV Boursorama pour enrichir les règles de catégorisation."
    )
    parser.add_argument("path", type=Path, help="Fichier CSV ou répertoire de fichiers CSV")
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Chemin du fichier JSON de sortie (défaut: scripts/output/labels_YYYYMMDD_HHMMSS.json)",
    )
    parser.add_argument(
        "--include-uncategorized",
        action="store_true",
        help="Inclure les transactions 'Non catégorisé'",
    )
    args = parser.parse_args()

    # Collecte des fichiers CSV
    csv_files: list[Path] = []
    if args.path.is_dir():
        csv_files = sorted(args.path.glob("*.csv")) + sorted(args.path.glob("*.CSV"))
    elif args.path.is_file():
        csv_files = [args.path]
    else:
        sys.exit(f"Erreur: {args.path} n'est ni un fichier ni un répertoire")

    if not csv_files:
        sys.exit(f"Erreur: aucun fichier CSV trouvé dans {args.path}")

    # Parsing
    all_rows: list[dict] = []
    source_files: list[str] = []
    for f in csv_files:
        print(f"[extract_labels] Traitement de {f.name}...")
        try:
            rows = parse_csv_file(f, args.include_uncategorized)
            all_rows.extend(rows)
            source_files.append(str(f))
            print(f"  → {len(rows)} lignes après filtrage")
        except ValueError as e:
            print(f"  AVERTISSEMENT: {e}. Fichier ignoré.")

    if not all_rows:
        sys.exit("Aucune ligne extraite. Vérifiez les fichiers CSV.")

    # Déduplication + tri
    unique_entries = deduplicate(all_rows)
    unique_entries.sort(
        key=lambda e: (
            e["category_parent"],
            e["category"],
            e["cleaned_label"].lower(),
        )
    )
    print(
        f"[extract_labels] {len(all_rows)} lignes → {len(unique_entries)} entrées uniques"
    )

    # Construction de la sortie
    now = datetime.now()
    output = {
        "metadata": {
            "generated_at": now.isoformat(),
            "script_version": "1.0.0",
            "source_files": source_files,
            "total_rows_processed": len(all_rows),
            "total_unique_entries": len(unique_entries),
            "noise_patterns_applied": [name for name, _ in NOISE_PATTERNS],
            "bankpulse_categories_reference": BANKPULSE_CATEGORIES_REFERENCE,
        },
        "instructions": (
            "Remplir 'suggested_bankpulse_category' avec le nom exact d'une catégorie "
            "de 'bankpulse_categories_reference' pour inclure cette entrée dans les règles. "
            "Laisser null ou ajouter '\"skip\": true' pour ignorer."
        ),
        "entries": unique_entries,
    }

    # Chemin de sortie
    if args.output is None:
        ts = now.strftime("%Y%m%d_%H%M%S")
        out_path = Path(__file__).parent / "output" / f"labels_{ts}.json"
    else:
        out_path = args.output
    out_path.parent.mkdir(parents=True, exist_ok=True)

    out_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[extract_labels] Résultat écrit dans {out_path}")
    print(f"[extract_labels] {len(unique_entries)} entrées uniques sur {len(csv_files)} fichier(s)")


if __name__ == "__main__":
    main()
