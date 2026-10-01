"""Regenerate the combined ontology files (canonical, raw, provenance) from the split source files.

ontology-combined*.ttl are generated artifacts kept for tools and CI that expect a single
file per ontology (SHACL validation, releases). Never edit by hand.
"""

import re
from pathlib import Path

ONTOLOGY_DIR = Path("src/ontology")

PREFIX_RE = re.compile(r"^@prefix\s+([\w-]*):\s*<([^>]*)>\s*\.\s*$")

SHARED_FILES = [
    "ontology-definitions-canonical.ttl",
    "ontology-enumerations-canonical.ttl",
]

# Vocabulary only (no shapes) — safe to pull into raw alongside its own shapes,
# since ontology-shapes-raw.ttl's RawPersonShape/RawOrganizationShape/etc.
# reference pulse:ExtractionOutput/pulse:partOfRun as sh:path/sh:class values.
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

PROVENANCE_FILES = SHARED_FILES + PROVENANCE_VOCAB + [
    "ontology-shapes-provenance.ttl",
]

VARIANTS = {
    "ontology-combined-canonical.ttl": CANONICAL_FILES,
    "ontology-combined-raw.ttl": RAW_FILES,
    "ontology-combined-provenance.ttl": PROVENANCE_FILES,
}


def split_prefixes(text: str) -> tuple[list[tuple[str, str, str]], str]:
    """Split leading @prefix lines from the rest of the file.

    Returns a list of (name, uri, raw_line) triples and the remaining body text.
    """
    lines = text.splitlines()
    prefixes = []
    rest_start = 0
    for i, line in enumerate(lines):
        if line.startswith("@prefix"):
            match = PREFIX_RE.match(line)
            if not match:
                raise ValueError(f"Malformed @prefix line: {line!r}")
            prefixes.append((match.group(1), match.group(2), line))
            rest_start = i + 1
        elif line.strip() == "":
            continue
        else:
            break
    rest = "\n".join(lines[rest_start:]).strip("\n")
    return prefixes, rest


def combine(ontology_dir: Path, source_files: list[str]) -> str:
    # Dedupe by prefix name, not by exact line text — two files binding the
    # same name with different whitespace must not produce two @prefix lines
    # for it. Binding the same name to two different URIs is a real conflict
    # and fails the build rather than silently picking one.
    seen: dict[str, tuple[str, str]] = {}
    bodies: list[str] = []

    for name in source_files:
        text = (ontology_dir / name).read_text()
        prefixes, body = split_prefixes(text)
        for prefix_name, uri, raw_line in prefixes:
            if prefix_name in seen and seen[prefix_name][0] != uri:
                raise ValueError(
                    f"Conflicting @prefix '{prefix_name}:' while combining {name}: "
                    f"<{uri}> vs already-seen <{seen[prefix_name][0]}>."
                )
            if prefix_name not in seen:
                seen[prefix_name] = (uri, raw_line)
        bodies.append(body)

    prefix_lines = [raw_line for _, raw_line in seen.values()]
    return "\n".join(prefix_lines) + "\n\n" + "\n\n".join(bodies) + "\n"


def main() -> None:
    root = Path(__file__).resolve().parents[3]
    ontology_dir = root / ONTOLOGY_DIR

    for output_file, source_files in VARIANTS.items():
        combined = combine(ontology_dir, source_files)
        (ontology_dir / output_file).write_text(combined)
        print(f"Wrote {ONTOLOGY_DIR / output_file} from {len(source_files)} source files.")


if __name__ == "__main__":
    main()
