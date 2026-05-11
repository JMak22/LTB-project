import re
import csv
from pathlib import Path

# ========= CONFIG =========

INPUT_FOLDER = "."
OUTPUT_CSV = "member_name_candidates.csv"

# Section headers / junk lines to ignore
EXCLUDED_LINES = {
    "BIOGRAPHIES",
    "CHAIR",
    "VICE CHAIRS",
    "ADJUDICATORS",
    "INTERIM CHAIR",
    "PAGE",
}

# ========= HELPERS =========

def normalize_spaces(text):
    """
    Collapse repeated whitespace.
    """
    return re.sub(r"\s+", " ", text).strip()


def extract_metadata(line):
    """
    Extract text in brackets, if present.
    Example:
    'John Nolan (Part-Time Member)'
    """
    metadata_match = re.search(r"\((.*?)\)", line)

    metadata = metadata_match.group(1).strip() if metadata_match else ""

    cleaned_name = re.sub(r"\(.*?\)", "", line).strip()

    return cleaned_name, metadata


def looks_like_name(line):
    """
    Heuristic test for likely name lines.
    """

    line = line.strip()

    if not line:
        return False

    # Ignore obvious section headings
    if line.upper() in EXCLUDED_LINES:
        return False

    # Too long -> probably biography text
    if len(line.split()) > 12:
        return False

    # Biography sentences usually end with punctuation
    if line.endswith("."):
        return False

    # Must contain at least 2 alphabetic chunks
    word_count = len(re.findall(r"[A-Za-zÀ-ÿ]+", line))
    if word_count < 2:
        return False

    # Reject obvious prose lines
    prose_starters = (
        "Before ",
        "Prior ",
        "After ",
        "He ",
        "She ",
        "Mr ",
        "Ms ",
        "Dr ",
        "In ",
        "From ",
    )

    if line.startswith(prose_starters):
        return False

    # Name-like capitalization ratio
    tokens = line.split()

    capitalized = 0

    for token in tokens:
        stripped = re.sub(r"[^A-Za-zÀ-ÿ]", "", token)

        if not stripped:
            continue

        if stripped.isupper() or stripped[0].isupper():
            capitalized += 1

    if capitalized / max(len(tokens), 1) < 0.6:
        return False

    # Reject lines with years
    if re.search(r"\b(19|20)\d{2}\b", line):
        return False

    if line.count(",") > 2:
        return False

    # Reject obvious prose indicators
    prose_words = [
        "the", "and", "of", "for", "with",
        "from", "before", "after", "including",
        "received", "served", "worked",
        "graduated", "appointed", "committee",
        "commission", "tribunal", "university",
        "society", "government", "community",
        "association", "college", "Annual", "Report", "Ontario", "Rental", "Housing", "Tribunal", "ORHT/LTB"
    ]

    lower_line = line.lower()

    prose_hits = sum(word in lower_line for word in prose_words)

    if prose_hits >= 2:
        return False


    return True


# ========= MAIN =========

rows = []

input_path = Path(INPUT_FOLDER)

for txt_file in input_path.glob("*.txt"):

    with open(txt_file, "r", encoding="utf-8", errors="ignore") as f:

        for line_number, raw_line in enumerate(f, start=1):

            line = normalize_spaces(raw_line)

            if looks_like_name(line):

                cleaned_name, metadata = extract_metadata(line)

                rows.append({
                    "source_file": txt_file.name,
                    "line_number": line_number,
                    "raw_line": raw_line.strip(),
                    "cleaned_name": cleaned_name,
                    "metadata": metadata,
                })


# ========= WRITE CSV =========

with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as csvfile:

    fieldnames = [
        "source_file",
        "line_number",
        "raw_line",
        "cleaned_name",
        "metadata",
    ]

    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()

    writer.writerows(rows)

print(f"Done. Wrote {len(rows)} candidate lines to {OUTPUT_CSV}")
