"""
sync_application_names.py

Synchronize application names/descriptions throughout the LTB Project
against the canonical app_type_dictionary.csv.

The dictionary is treated as the sole authority for:

    application code -> public-facing application description

The script searches recursively through CSV files in the project and updates
description/name fields only when the same row contains an application code
that can be matched unambiguously to app_type_dictionary.csv.

Usage:
    python sync_application_names.py . --apply

"""

from __future__ import annotations

import argparse
import csv
import sys
import tempfile
from collections import Counter
from pathlib import Path


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

CODE_COLUMNS = (
    "app_code",
    "application_code",
    "application_family",
    "family",
    "app_type",
)

# These are fields that may contain a public-facing application name.
NAME_COLUMNS = (
    "description",
    "application_name",
    "app_name",
    "application_description",
    "app_description",
)

DEFAULT_EXCLUDED_DIRS = {
    ".git",
    ".github",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
}

DICTIONARY_FILENAME = "app_type_dictionary.csv"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def clean(value: str | None) -> str:
    """Return a stripped string, safely handling None."""
    return "" if value is None else str(value).strip()


def find_dictionary(project_root: Path) -> Path:
    """
    Locate the canonical app_type_dictionary.csv.

    Prefer a dictionary in the project root. If it isn't there, search
    recursively and require exactly one match.
    """
    root_candidate = project_root / DICTIONARY_FILENAME

    if root_candidate.is_file():
        return root_candidate

    matches = [
        p for p in project_root.rglob(DICTIONARY_FILENAME)
        if ".git" not in p.parts
    ]

    if not matches:
        raise FileNotFoundError(
            f"Could not find {DICTIONARY_FILENAME} under {project_root}"
        )

    if len(matches) > 1:
        print(
            "\nERROR: More than one app_type_dictionary.csv was found:\n",
            file=sys.stderr,
        )
        for path in matches:
            print(f"  {path}", file=sys.stderr)

        raise RuntimeError(
            "Dictionary is ambiguous. Put the authoritative dictionary in "
            "the project root or remove/rename obsolete copies."
        )

    return matches[0]


def load_dictionary(dictionary_path: Path) -> dict[str, str]:
    """
    Read app_type_dictionary.csv and return:

        {app_code: canonical_description}

    Refuse duplicate codes with conflicting descriptions because that would
    make the supposed source of authority ambiguous.
    """
    lookup: dict[str, str] = {}

    with dictionary_path.open(
        "r", encoding="utf-8-sig", newline=""
    ) as f:
        reader = csv.DictReader(f)

        required = {"app_code", "description"}

        if reader.fieldnames is None:
            raise ValueError("Dictionary has no header row.")

        missing = required - set(reader.fieldnames)
        if missing:
            raise ValueError(
                "Dictionary is missing required column(s): "
                + ", ".join(sorted(missing))
            )

        for line_number, row in enumerate(reader, start=2):
            code = clean(row.get("app_code"))
            description = clean(row.get("description"))

            if not code:
                continue

            if not description:
                raise ValueError(
                    f"{dictionary_path.name}, row {line_number}: "
                    f"{code!r} has no description."
                )

            if code in lookup and lookup[code] != description:
                raise ValueError(
                    f"Conflicting dictionary entries for {code!r}:\n"
                    f"  {lookup[code]!r}\n"
                    f"  {description!r}"
                )

            lookup[code] = description

    if not lookup:
        raise ValueError("Dictionary contains no usable application codes.")

    return lookup


def should_skip(path: Path, project_root: Path, excluded_dirs: set[str]) -> bool:
    """Return True when a CSV is inside an excluded directory."""
    try:
        relative = path.relative_to(project_root)
    except ValueError:
        return True

    return any(part in excluded_dirs for part in relative.parts[:-1])


def detect_columns(fieldnames: list[str]) -> tuple[str | None, list[str]]:
    """
    Find the most suitable application-code column and any application-name
    columns in a CSV.
    """
    code_column = next(
        (column for column in CODE_COLUMNS if column in fieldnames),
        None,
    )

    name_columns = [
        column for column in NAME_COLUMNS
        if column in fieldnames
    ]

    return code_column, name_columns


# ---------------------------------------------------------------------------
# CSV inspection
# ---------------------------------------------------------------------------

def inspect_csv(
    csv_path: Path,
    canonical_names: dict[str, str],
) -> tuple[list[dict[str, str]], list[str], list[dict], Counter]:
    """
    Read one CSV and identify required changes.

    Returns:
      rows
      fieldnames
      changes
      unknown_codes

    A change record describes one individual cell replacement.
    """
    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)

        if reader.fieldnames is None:
            return [], [], [], Counter()

        fieldnames = list(reader.fieldnames)
        rows = list(reader)

    code_column, name_columns = detect_columns(fieldnames)

    # A file needs both:
    #   - an identifiable single application code
    #   - at least one name/description field
    if not code_column or not name_columns:
        return rows, fieldnames, [], Counter()

    changes = []
    unknown_codes = Counter()

    for row_number, row in enumerate(rows, start=2):
        code = clean(row.get(code_column))

        if not code:
            continue

        # Do not try to invent descriptions for combinations such as L1/L2.
        if "/" in code or "+" in code:
            continue

        canonical = canonical_names.get(code)

        if canonical is None:
            unknown_codes[code] += 1
            continue

        for name_column in name_columns:
            old_value = clean(row.get(name_column))

            if old_value != canonical:
                changes.append(
                    {
                        "row_number": row_number,
                        "code_column": code_column,
                        "app_code": code,
                        "name_column": name_column,
                        "old_value": old_value,
                        "new_value": canonical,
                    }
                )

    return rows, fieldnames, changes, unknown_codes


def apply_changes_to_rows(
    rows: list[dict[str, str]],
    changes: list[dict],
) -> None:
    """Apply previously audited cell changes to rows in memory."""
    for change in changes:
        # CSV row 2 is rows[0], hence the -2.
        row_index = change["row_number"] - 2
        rows[row_index][change["name_column"]] = change["new_value"]


def write_csv_atomically(
    csv_path: Path,
    rows: list[dict[str, str]],
    fieldnames: list[str],
) -> None:
    """
    Write to a temporary file in the same directory and replace the original
    only after the new CSV has been successfully written.
    """
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        newline="",
        delete=False,
        dir=csv_path.parent,
        prefix=csv_path.stem + "_",
        suffix=".tmp",
    ) as tmp:
        writer = csv.DictWriter(
            tmp,
            fieldnames=fieldnames,
            extrasaction="raise",
            lineterminator="\n",
        )

        writer.writeheader()
        writer.writerows(rows)

        temp_path = Path(tmp.name)

    temp_path.replace(csv_path)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Synchronize application names in project CSVs against "
            "app_type_dictionary.csv."
        )
    )

    parser.add_argument(
        "project_root",
        nargs="?",
        default=".",
        help="Root of the LTB project. Default: current directory.",
    )

    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually modify files. Without this option the script is dry-run only.",
    )

    parser.add_argument(
        "--exclude-dir",
        action="append",
        default=[],
        help=(
            "Additional directory name to exclude. "
            "May be supplied more than once."
        ),
    )

    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()

    if not project_root.is_dir():
        print(f"ERROR: Not a directory: {project_root}", file=sys.stderr)
        return 1

    excluded_dirs = DEFAULT_EXCLUDED_DIRS | set(args.exclude_dir)

    # -----------------------------------------------------------------------
    # Load the authoritative dictionary.
    # -----------------------------------------------------------------------

    try:
        dictionary_path = find_dictionary(project_root)
        canonical_names = load_dictionary(dictionary_path)
    except (FileNotFoundError, RuntimeError, ValueError) as exc:
        print(f"\nERROR: {exc}", file=sys.stderr)
        return 1

    print("=" * 72)
    print("LTB APPLICATION NAME SYNCHRONIZATION")
    print("=" * 72)
    print(f"Project:     {project_root}")
    print(f"Dictionary:  {dictionary_path}")
    print(f"App codes:   {len(canonical_names):,}")
    print(f"Mode:        {'APPLY CHANGES' if args.apply else 'DRY RUN'}")

    if excluded_dirs:
        print("Excluded:    " + ", ".join(sorted(excluded_dirs)))

    print()

    # -----------------------------------------------------------------------
    # Scan CSV files.
    # -----------------------------------------------------------------------

    csv_files = sorted(project_root.rglob("*.csv"))

    audit_results = []
    all_unknown_codes = Counter()
    total_changes = 0

    for csv_path in csv_files:

        if csv_path.resolve() == dictionary_path.resolve():
            continue

        if should_skip(csv_path, project_root, excluded_dirs):
            continue

        try:
            rows, fieldnames, changes, unknown = inspect_csv(
                csv_path,
                canonical_names,
            )
        except (UnicodeDecodeError, csv.Error) as exc:
            print(
                f"WARNING: Could not read {csv_path.relative_to(project_root)}: "
                f"{exc}"
            )
            continue

        all_unknown_codes.update(unknown)

        if changes:
            audit_results.append(
                {
                    "path": csv_path,
                    "rows": rows,
                    "fieldnames": fieldnames,
                    "changes": changes,
                }
            )

            total_changes += len(changes)

            relative = csv_path.relative_to(project_root)

            print(f"{relative}")
            print(f"  {len(changes):,} name field(s) need synchronization")

            # Show a few examples so the dry run is actually useful.
            for change in changes[:5]:
                print(
                    f"    row {change['row_number']}: "
                    f"{change['app_code']} | "
                    f"{change['old_value']!r} -> "
                    f"{change['new_value']!r}"
                )

            if len(changes) > 5:
                print(f"    ... plus {len(changes) - 5:,} more")

            print()

    # -----------------------------------------------------------------------
    # Summary
    # -----------------------------------------------------------------------

    print("-" * 72)
    print(f"CSV files scanned:       {len(csv_files):,}")
    print(f"CSV files needing fixes: {len(audit_results):,}")
    print(f"Name fields to replace:  {total_changes:,}")

    if all_unknown_codes:
        print("\nApplication codes found in relevant CSVs but NOT in dictionary:")

        for code, count in sorted(all_unknown_codes.items()):
            print(f"  {code:<12} {count:>6,} row(s)")

        print(
            "\nThese were NOT changed. Check whether they belong in "
            "app_type_dictionary.csv."
        )

    # Nothing to do.
    if total_changes == 0:
        print("\nEverything is already synchronized.")
        return 0

    # Dry run stops here.
    if not args.apply:
        print(
            "\nDRY RUN ONLY — no files were changed.\n"
            "Review the output above. If it looks correct, run again with:\n\n"
            "    python sync_application_names.py . --apply"
        )
        return 0

    # -----------------------------------------------------------------------
    # Apply changes.
    # -----------------------------------------------------------------------

    for result in audit_results:
        csv_path = result["path"]
        relative = csv_path.relative_to(project_root)

        apply_changes_to_rows(
            result["rows"],
            result["changes"],
        )

        write_csv_atomically(
            csv_path,
            result["rows"],
            result["fieldnames"],
        )

        print(
            f"UPDATED: {relative} "
            f"({len(result['changes']):,} replacement(s))"
        )

    print("\n" + "=" * 72)
    print("COMPLETE")
    print("=" * 72)
    print(f"Files updated: {len(audit_results):,}")
    print(f"Cells updated: {total_changes:,}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())