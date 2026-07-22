"""Regenerate the combined ontology files (canonical, raw, provenance) from the split source files.

ontology-combined*.ttl are generated artifacts kept for tools and CI that expect a single
file per ontology (SHACL validation, releases). Never edit by hand.
"""

from pathlib import Path

ONTOLOGY_DIR = Path("src/ontology")

SHARED_FILES = [
    "ontology-definitions-canonical.ttl",
    "ontology-enumerations-canonical.ttl",
]

# Vocabulary only (no shapes) — safe to pull into raw alongside its own shapes,
# since ontology-shapes-raw.ttl's RawPersonShape/RawOrganizationShape/etc.
# reference pulse:ExtractionRun/pulse:partOfRun as sh:path/sh:class values.
PROVENANCE_VOCAB = [
    "ontology-definitions-provenance.ttl",
]

CANONICAL_FILES = SHARED_FILES + [
    "ontology-shapes-canonical.ttl",
]

RAW_FILES = SHARED_FILES + PROVENANCE_VOCAB + [
    "ontology-definitions-raw.ttl",
    "ontology-enumerations-raw.ttl",
    "ontology-shapes-raw.ttl",
]

PROVENANCE_FILES = SHARED_FILES + PROVENANCE_VOCAB

VARIANTS = {
    "ontology-combined-canonical.ttl": CANONICAL_FILES,
    "ontology-combined-raw.ttl": RAW_FILES,
    "ontology-combined-provenance.ttl": PROVENANCE_FILES,
}


def split_prefixes(text: str) -> tuple[list[str], str]:
    lines = text.splitlines()
    prefixes = []
    rest_start = 0
    for i, line in enumerate(lines):
        if line.startswith("@prefix"):
            prefixes.append(line)
            rest_start = i + 1
        elif line.strip() == "":
            continue
        else:
            break
    rest = "\n".join(lines[rest_start:]).strip("\n")
    return prefixes, rest


def combine(ontology_dir: Path, source_files: list[str]) -> str:
    seen_prefixes: list[str] = []
    bodies: list[str] = []

    for name in source_files:
        text = (ontology_dir / name).read_text()
        prefixes, body = split_prefixes(text)
        for prefix in prefixes:
            if prefix not in seen_prefixes:
                seen_prefixes.append(prefix)
        bodies.append(body)

    return "\n".join(seen_prefixes) + "\n\n" + "\n\n".join(bodies) + "\n"


def main() -> None:
    root = Path(__file__).resolve().parents[3]
    ontology_dir = root / ONTOLOGY_DIR

    for output_file, source_files in VARIANTS.items():
        combined = combine(ontology_dir, source_files)
        (ontology_dir / output_file).write_text(combined)
        print(f"Wrote {ONTOLOGY_DIR / output_file} from {len(source_files)} source files.")


if __name__ == "__main__":
    main()
