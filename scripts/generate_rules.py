"""
generate_rules.py — Génère des propositions de règles regex depuis le JSON validé.

Usage:
    uv run python scripts/generate_rules.py <validated_json> [--output PATH]
                                             [--priority INT] [--match-field supplier|cleaned_label]

Prérequis: avoir d'abord exécuté extract_labels.py et rempli 'suggested_bankpulse_category'
dans le JSON résultant.

# Vérifier le pattern généré manuellement
python -c "import re; print(re.search('(?i)pharmavance\\ marc', 'pharmavance marc'))"
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Literal

MatchField = Literal["supplier", "cleaned_label", "both"]

# ── UUIDs des catégories BankPulse (depuis la migration c7d8e3f1a234) ────────
BANKPULSE_CATEGORY_UUIDS: dict[str, str] = {
    # Parents
    "Alimentation": "a1000000-0000-0000-0000-000000000001",
    "Transport": "a1000000-0000-0000-0000-000000000002",
    "Logement": "a1000000-0000-0000-0000-000000000003",
    "Loisirs & Culture": "a1000000-0000-0000-0000-000000000004",
    "Sante": "a1000000-0000-0000-0000-000000000005",
    "Shopping": "a1000000-0000-0000-0000-000000000006",
    "Services & Abonnements": "a1000000-0000-0000-0000-000000000007",
    "Revenus": "a1000000-0000-0000-0000-000000000008",
    # Enfants
    "Supermarche": "c1000000-0000-0000-0000-000000000001",
    "Restaurant": "c1000000-0000-0000-0000-000000000002",
    "Fast food": "c1000000-0000-0000-0000-000000000003",
    "Essence": "c1000000-0000-0000-0000-000000000004",
    "Transports en commun": "c1000000-0000-0000-0000-000000000005",
    "Taxi & VTC": "c1000000-0000-0000-0000-000000000006",
    "Loyer": "c1000000-0000-0000-0000-000000000007",
    "Charges": "c1000000-0000-0000-0000-000000000008",
    "Sport & Fitness": "c1000000-0000-0000-0000-000000000009",
    "Streaming & Jeux": "c1000000-0000-0000-0000-000000000010",
    "Cinema": "c1000000-0000-0000-0000-000000000011",
    "Medecin": "c1000000-0000-0000-0000-000000000012",
    "Pharmacie": "c1000000-0000-0000-0000-000000000013",
    "Vetements": "c1000000-0000-0000-0000-000000000014",
    "High-tech": "c1000000-0000-0000-0000-000000000015",
    "Telephonie": "c1000000-0000-0000-0000-000000000016",
    "Assurances": "c1000000-0000-0000-0000-000000000017",
    "Banque & Frais": "c1000000-0000-0000-0000-000000000018",
    "Salaire": "c1000000-0000-0000-0000-000000000019",
    "Remboursements": "c1000000-0000-0000-0000-000000000020",
}


def load_validated_json(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if "entries" not in data:
        raise ValueError(f"JSON invalide : clé 'entries' manquante dans {path}")
    return data


def build_token(entry: dict, match_field: MatchField) -> str | None:
    """Retourne le token regex échappé pour une entrée."""
    supplier = (entry.get("supplier_found") or "").strip()
    cleaned = (entry.get("cleaned_label") or "").strip()

    if match_field == "supplier":
        return re.escape(supplier) if supplier else None
    elif match_field == "cleaned_label":
        return re.escape(cleaned) if cleaned else None
    else:  # "both" : supplier en priorité
        token = supplier if supplier else cleaned
        return re.escape(token) if token else None


def group_by_bankpulse_category(entries: list[dict]) -> dict[str, list[dict]]:
    """Groupe les entrées par suggested_bankpulse_category, triées par occurrence_count desc."""
    groups: dict[str, list[dict]] = {}
    for entry in entries:
        bp_cat = entry.get("suggested_bankpulse_category")
        if bp_cat is None or entry.get("skip", False):
            continue
        groups.setdefault(bp_cat, []).append(entry)

    for cat in groups:
        groups[cat].sort(key=lambda e: e.get("occurrence_count", 0), reverse=True)

    return groups


def generate_rule(
    bp_category: str,
    entries: list[dict],
    match_field: MatchField,
    priority: int,
) -> dict:
    tokens: list[str] = []
    source_entries: list[dict] = []
    warnings: list[str] = []

    seen_tokens: set[str] = set()
    for entry in entries:
        token = build_token(entry, match_field)
        if token is None:
            warnings.append(
                f"Pas de valeur '{match_field}' pour '{entry.get('cleaned_label', '?')}' "
                f"(boursorama: {entry.get('category', '?')})"
            )
            continue
        # Dédup case-insensitive
        token_key = token.lower()
        if token_key in seen_tokens:
            continue
        seen_tokens.add(token_key)
        tokens.append(token)
        source_entries.append(
            {
                "cleaned_label": entry.get("cleaned_label", ""),
                "supplier_found": entry.get("supplier_found", ""),
                "boursorama_category": entry.get("category", ""),
                "boursorama_category_parent": entry.get("category_parent", ""),
                "occurrence_count": entry.get("occurrence_count", 0),
                "token_used": token,
            }
        )

    pattern = ("(?i)" + "|".join(tokens)) if tokens else ""
    if not pattern:
        warnings.append(f"Aucun token généré pour '{bp_category}'")

    category_uuid = BANKPULSE_CATEGORY_UUIDS.get(bp_category)
    if category_uuid is None:
        warnings.append(
            f"UUID introuvable pour la catégorie BankPulse '{bp_category}'. "
            f"Catégories disponibles : {sorted(BANKPULSE_CATEGORY_UUIDS.keys())}"
        )

    return {
        "bankpulse_category": bp_category,
        "category_uuid": category_uuid,
        "suggested_pattern": pattern,
        "priority": priority,
        "match_field": match_field,
        "source_entry_count": len(source_entries),
        "source_entries": source_entries,
        "warnings": warnings,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Génère des propositions de règles regex depuis un JSON de labels validé."
    )
    parser.add_argument("validated_json", type=Path, help="Chemin vers le JSON validé")
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Chemin du JSON de sortie (défaut: scripts/output/rules_YYYYMMDD_HHMMSS.json)",
    )
    parser.add_argument(
        "--priority",
        type=int,
        default=5,
        help="Priorité assignée aux règles générées (les règles seed utilisent 9-10, défaut: 5)",
    )
    parser.add_argument(
        "--match-field",
        choices=["supplier", "cleaned_label", "both"],
        default="supplier",
        help="Champ utilisé pour générer le token regex (défaut: supplier)",
    )
    args = parser.parse_args()

    if not args.validated_json.exists():
        sys.exit(f"Erreur: fichier introuvable {args.validated_json}")

    data = load_validated_json(args.validated_json)
    entries = data["entries"]

    groups = group_by_bankpulse_category(entries)
    filled = sum(len(v) for v in groups.values())
    total = len(entries)
    skipped = total - filled
    if filled == 0:
        print(
            "AVERTISSEMENT: aucune entrée avec 'suggested_bankpulse_category' rempli. "
            "Rien à générer."
        )
    else:
        print(f"[generate_rules] {filled}/{total} entrées avec catégorie BankPulse remplie")

    if not groups:
        sys.exit("Aucune catégorie BankPulse remplie. Rien à générer.")

    rules: list[dict] = []
    for bp_category in sorted(groups):
        rule = generate_rule(
            bp_category, groups[bp_category], args.match_field, args.priority
        )
        rules.append(rule)
        for w in rule["warnings"]:
            print(f"  AVERTISSEMENT [{bp_category}]: {w}")

    now = datetime.now()
    output = {
        "metadata": {
            "generated_at": now.isoformat(),
            "script_version": "1.0.0",
            "source_file": str(args.validated_json),
            "total_rules_generated": len(rules),
            "total_entries_used": sum(r["source_entry_count"] for r in rules),
            "total_entries_skipped": skipped,
            "priority": args.priority,
            "match_field": args.match_field,
        },
        "instructions": (
            "Revoir chaque 'suggested_pattern' avant de l'ajouter dans une migration Alembic. "
            "Éditer les patterns pour éviter les faux positifs. "
            "Le 'category_uuid' correspond directement aux UUIDs seedés en base. "
            "Note: re.escape() produit des backslashes — dans la migration Python, "
            "utiliser le pattern tel quel (les doubles backslashes du JSON sont normaux)."
        ),
        "rules": rules,
    }

    if args.output is None:
        ts = now.strftime("%Y%m%d_%H%M%S")
        out_path = Path(__file__).parent / "output" / f"rules_{ts}.json"
    else:
        out_path = args.output
    out_path.parent.mkdir(parents=True, exist_ok=True)

    out_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[generate_rules] Résultat écrit dans {out_path}")
    print(f"[generate_rules] {len(rules)} règles générées, {skipped} entrées ignorées")


if __name__ == "__main__":
    main()
