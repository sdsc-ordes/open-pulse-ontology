"""Regenerate the combined ontology files from the split source files.

ontology-definitions.ttl, ontology-enumerations.ttl and ontology-shapes.ttl are the
core source of truth. ontology-definitions-verbose.ttl, ontology-enumerations-verbose.ttl
and ontology-shapes-verbose.ttl additively extend the core files (same shape/class/property
IRIs get more triples, never redefined ones) to reach full parity with the GitHub/Hugging
Face/Zenodo/ORCID field inventory. ontology-combined.ttl and ontology-combined-verbose.ttl
are generated artifacts kept for tools and CI that expect a single file (SHACL validation,
releases): the former from the core files only, the latter from core + verbose.
"""

from pathlib import Path

ONTOLOGY_DIR = Path("src/ontology")

CORE_FILES = [
    "ontology-definitions.ttl",
    "ontology-enumerations.ttl",
    "ontology-shapes.ttl",
]

VERBOSE_FILES = CORE_FILES + [
    "ontology-definitions-verbose.ttl",
    "ontology-enumerations-verbose.ttl",
    "ontology-shapes-verbose.ttl",
]

VARIANTS = {
    "ontology-combined.ttl": CORE_FILES,
    "ontology-combined-verbose.ttl": VERBOSE_FILES,
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
