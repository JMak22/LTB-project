import csv
import re

INPUT_CSV = "member_name_candidates.csv"
OUTPUT_CSV = "member_names_deduped.csv"

# Exact phrases to remove entirely
EXCLUDED_PHRASES = {
    "Ontario Rental Housing Tribunal",
    "Annual Report",
    "Ontario Rental Housing",
}

# ========= HELPERS =========

def normalize_name(name):
    """
    Normalize names for deduplication.
    Keeps output human-readable while reducing duplicates.
    """

    # Collapse whitespace
    name = re.sub(r"\s+", " ", name)

    # Repair likely OCR split words ONLY for single-character fragments
    # Example: "Elizabet h" -> "Elizabeth"
    name = re.sub(r"([A-Za-zÀ-ÿ]{2,})\s([a-zÀ-ÿ])\b", r"\1\2", name)

    # Remove academic/professional suffixes after the actual name
    # Example: "Dr. Lilian Yan Yan Ma, B.Sc., Ph.D., LL.B." -> "Dr. Lilian Yan Yan Ma"
    name = re.sub(r",\s*(B\.?Sc\.?|Ph\.?D\.?|LL\.?B\.?|M\.?A\.?|B\.?A\.?|M\.?B\.?A\.?).*$", "", name, flags=re.IGNORECASE)


    # Strip leading/trailing whitespace
    name = name.strip()

    # Normalize capitalization
    # Normalize ALL CAPS names only
    if name.isupper():
        name = name.title()

    return name


# ========= MAIN =========

seen = set()
deduped_rows = []

with open(INPUT_CSV, newline="", encoding="utf-8") as csvfile:

    reader = csv.DictReader(csvfile)

    for row in reader:

        raw_name = row["cleaned_name"].strip()

        # Skip excluded phrases
        if raw_name in EXCLUDED_PHRASES:
            continue

        normalized = normalize_name(raw_name)

        institution_words = [
            "Committee",
            "Planning",
            "Development",
            "Administration",
            "Finance",
            "Recreation",
            "Waste",
            "Management",
            "Tribunal",
            "Annual Report",
            "ORHT/LTB"
            "Orht/Ltb"
        ]


        if sum(word in normalized for word in institution_words) >= 2:
            continue

        # Skip empty names
        if not normalized:
            continue

        # Deduplicate
        if normalized not in seen:

            seen.add(normalized)

            deduped_rows.append({
                "normalized_name": normalized,
                "metadata": row["metadata"],
                "source_file": row["source_file"],
                "raw_line": row["raw_line"],
            })


# ========= WRITE OUTPUT =========

with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as outfile:

    fieldnames = [
        "normalized_name",
        "metadata",
        "source_file",
        "raw_line",
    ]

    writer = csv.DictWriter(outfile, fieldnames=fieldnames)

    writer.writeheader()

    writer.writerows(deduped_rows)

print(f"Done. Wrote {len(deduped_rows)} unique names to {OUTPUT_CSV}")
