# Open Pulse Ontology

An RDF ontology for modeling contributions to open source scientific software and research articles from EPFL organizations and researchers.

## Overview

The Open Pulse Ontology provides a structured vocabulary and validation rules (SHACL shapes) for capturing metrics about:

- **People**: Researchers and contributors with GitHub usernames, ORCID identifiers, and institutional affiliations
- **Organizations**: Universities, research institutions, and companies with ROR identifiers and GitHub handles
- **Software Repositories**: Repositories hosted on GitHub, GitLab, or Bitbucket, with metadata, ownership, and contribution tracking
- **Research Articles**: Scholarly publications with DOI identifiers and author information
- **Contributions**: Individual commit-level contributions linking people to repositories
- **Memberships**: Affiliations between people and organizations with time periods and roles

## Setup

### Prerequisites

- Python 3.9 or higher
- [uv](https://docs.astral.sh/uv/) (fast Python package manager)

### Installation

```bash
# Install dependencies
uv sync

# Or for development (includes testing tools)
uv sync --extra dev
```

## Ontology Files

This repo models three separate ontologies under `src/ontology/`, one per stage of the
extract → unify → canonical pipeline (see [CONTRIBUTING.md](CONTRIBUTING.md) for how they
relate and how each is combined):

- **Canonical** — the deduplicated, query-friendly graph (`graph:canonical`): one
  `schema:Person`/`org:Organization`/etc. per real-world entity, closed shapes, a single
  value per functional property. Source files: `ontology-definitions-canonical.ttl`,
  `ontology-enumerations-canonical.ttl`, `ontology-shapes-canonical.ttl` → generated `ontology-combined-canonical.ttl`.
- **Raw** — data as extractors actually emit it, before unification: one `PlatformProfile`
  per source, provisional identity (no ORCID/ROR resolved yet), open shapes, plus every
  platform-specific field needed for full field-parity with GitHub, Hugging Face, Zenodo
  and ORCID. Source files: `ontology-definitions-raw.ttl`, `ontology-enumerations-raw.ttl`,
  `ontology-shapes-raw.ttl` (standalone — does not extend the canonical shapes) → generated
  `ontology-combined-raw.ttl`.
- **Provenance** — `graph:prov`: for a canonical triple, which platform-specific
  `pulse:ExtractionOutput` it was derived from (one `pulse:ExtractionRun` can span several
  platforms; each platform's raw output is its own `ExtractionOutput`, sharing the run via
  `prov:wasGeneratedBy`). Lives in its own graph; canonical/raw entities never carry these
  properties directly. The winner-links themselves are recorded as RDF-star annotations on
  quoted triples, which **can't be SHACL-shaped** — no tool in this repo's stack can target
  a quoted triple as a focus node (rdflib can't parse Turtle-star; pySHACL has no RDF-star
  support). `pulse:ExtractionRun` itself is a plain, ordinary-subject resource though, so
  it *is* shaped (`ontology-shapes-provenance.ttl`); `pulse:ExtractionOutput`'s shape lives
  in `ontology-shapes-raw.ttl` instead, since its self-describing header is asserted inside
  the raw substrate graph it names, not inside `graph:prov`. Source files:
  `ontology-definitions-provenance.ttl`, `ontology-shapes-provenance.ttl` → generated
  `ontology-combined-provenance.ttl`.

All three share the base classes/properties/enumerations declared in
`ontology-definitions-canonical.ttl` / `ontology-enumerations-canonical.ttl`.

## Validation

### Running Validation

```bash
# Validate test data against any one of the three ontologies
uv run python tools/python/checks/shacl.py example/test_dataset_large_example.ttl src/ontology/ontology-combined-canonical.ttl

# Run the full test suite (all three ontologies)
uv run python tools/python/checks/test_validation.py
```

### Example Test Cases

The `example/` directory contains test files demonstrating both valid and invalid data patterns:

- `test_valid_*.ttl` - Valid data conforming to the ontology
- `test_invalid_*.ttl` - Invalid data triggering specific validation errors

`example/` (canonical), `example/raw/`, and `example/provenance/` each follow this same
convention, validated against their respective combined file. `test_validation.py` runs all
three and reports a combined summary. The RDF-star winner-links in `graph:prov` have no
fixtures here — they can't be SHACL-validated (see above) — but `example/provenance/` does
cover the plain-RDF `pulse:ExtractionRun` shape, and there's a separate, explicitly
non-parseable illustrative file (`example_provenance_graph.ttl`) showing the full RDF-star
picture by eye.

## License

CC-BY-4.0

