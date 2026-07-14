"""Regenerate ontology-combined.ttl from the split source files.

ontology-classes.ttl, ontology-enumerations.ttl and ontology-shapes.ttl are the
source of truth. ontology-combined.ttl is a generated artifact kept for tools
and CI that expect a single file (SHACL validation, releases).
"""

from pathlib import Path

ONTOLOGY_DIR = Path("src/ontology")

SOURCE_FILES = [
    "ontology-classes.ttl",
    "ontology-enumerations.ttl",
    "ontology-shapes.ttl",
]

OUTPUT_FILE = "ontology-combined.ttl"


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


def main() -> None:
    root = Path(__file__).resolve().parents[3]
    ontology_dir = root / ONTOLOGY_DIR
    seen_prefixes: list[str] = []
    bodies: list[str] = []

    for name in SOURCE_FILES:
        text = (ontology_dir / name).read_text()
        prefixes, body = split_prefixes(text)
        for prefix in prefixes:
            if prefix not in seen_prefixes:
                seen_prefixes.append(prefix)
        bodies.append(body)

    combined = "\n".join(seen_prefixes) + "\n\n" + "\n\n".join(bodies) + "\n"
    (ontology_dir / OUTPUT_FILE).write_text(combined)
    print(f"Wrote {ONTOLOGY_DIR / OUTPUT_FILE} from {len(SOURCE_FILES)} source files.")


if __name__ == "__main__":
    main()
