import csv
import re
from pathlib import Path

# ========= CONFIG =========

TEXT_FOLDER = "."
CANONICAL_CSV = "canonical_names.csv"
OUTPUT_CSV = "member_counts_by_file.csv"

PART_TIME_PATTERNS = [
    "part-time",
    "part time",
    "parttime",
]

# ========= HELPERS =========

def normalize_text(text):
    """
    Light normalization for OCR text.
    """

    text = text.lower()

    # collapse whitespace
    text = re.sub(r"\s+", " ", text)

    # repair obvious OCR split words
    # text = re.sub(r"([a-z])\s([a-z])", r"\1\2", text) -- too aggressive, majority of names not counted

    return text


def build_name_patterns(name):
    """
    Create regex patterns tolerant of OCR spacing weirdness.
    Example:
    Mary Lee -> M\s*a\s*r\s*y\s+L\s*e\s*e
    """

    tokens = name.split()

    token_patterns = []

    for token in tokens:

        chars = list(token)

        char_pattern = r"\s*".join(map(re.escape, chars))

        token_patterns.append(char_pattern)

    return r"\s+".join(token_patterns)


# ========= LOAD CANONICAL NAMES =========

canonical_map = {}

with open(CANONICAL_CSV, newline="", encoding="utf-8") as csvfile:

    reader = csv.DictReader(csvfile)

    for row in reader:

        canonical = row["canonical_name"].strip()

        variants = row["variants"].split(";")

        all_names = [canonical] + variants

        canonical_map[canonical] = [
            v.strip()
            for v in all_names
            if v.strip()
        ]


# ========= PROCESS FILES =========

results = []

for txt_file in Path(TEXT_FOLDER).glob("*.txt"):

    with open(txt_file, "r", encoding="utf-8", errors="ignore") as f:

        raw_text = f.read()

    text = normalize_text(raw_text)

    found_names = set()
    found_part_time = set()

    for canonical_name, variants in canonical_map.items():

        matched = False

        for variant in variants:

            pattern = build_name_patterns(variant.lower())

            if re.search(pattern, text):

                found_names.add(canonical_name)
                matched = True

                # Look for explicit metadata immediately after name
                part_time_pattern = (
                    pattern +
                    r"\s*\(\s*(part[\s-]*time(?:\s+member)?)"
                )

                if re.search(part_time_pattern, text):
                    found_part_time.add(canonical_name)

                break

    results.append({
        "file": txt_file.name,
        "canonical_names_found": len(found_names),
        "part_time_names_found": len(found_part_time),
        "names_found": "; ".join(sorted(found_names)),
    })


# ========= WRITE OUTPUT =========

with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as outfile:

    fieldnames = [
        "file",
        "canonical_names_found",
        "part_time_names_found",
        "names_found",
    ]

    writer = csv.DictWriter(outfile, fieldnames=fieldnames)

    writer.writeheader()

    writer.writerows(results)

print(f"Done. Wrote results to {OUTPUT_CSV}")
