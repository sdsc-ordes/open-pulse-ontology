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
  value per functional property. Source files: `ontology-definitions.ttl`,
  `ontology-enumerations.ttl`, `ontology-shapes.ttl` → generated `ontology-combined.ttl`.
- **Raw** — data as extractors actually emit it, before unification: one `PlatformProfile`
  per source, provisional identity (no ORCID/ROR resolved yet), open shapes, plus every
  platform-specific field needed for full field-parity with GitHub, Hugging Face, Zenodo
  and ORCID. Source files: `ontology-definitions-raw.ttl`, `ontology-enumerations-raw.ttl`,
  `ontology-shapes-raw.ttl` (standalone — does not extend the canonical shapes) → generated
  `ontology-combined-raw.ttl`.
- **Provenance** — `graph:prov`: for a canonical triple, which `ExtractionRun` it was
  derived from. Lives in its own graph; canonical/raw entities never carry these properties
  directly. Recorded as RDF-star annotations on quoted triples, so it is **not
  SHACL-shaped** — no tool in this repo's stack can target a quoted triple as a focus node
  (rdflib can't parse Turtle-star; pySHACL has no RDF-star support). Source file:
  `ontology-definitions-provenance.ttl` (a plain RDFS/OWL vocabulary documenting the
  expected triple patterns via `rdfs:comment`, not enforcing them) → generated
  `ontology-combined-provenance.ttl`.

All three share the base classes/properties/enumerations declared in
`ontology-definitions.ttl` / `ontology-enumerations.ttl`.

## Validation

### Running Validation

```bash
# Validate test data against any one of the three ontologies
uv run python tools/python/checks/shacl.py example/test_dataset_large_example.ttl src/ontology/ontology-combined.ttl

# Run the full test suite (all three ontologies)
uv run python tools/python/checks/test_validation.py
```

### Example Test Cases

The `example/` directory contains test files demonstrating both valid and invalid data patterns:

- `test_valid_*.ttl` - Valid data conforming to the ontology
- `test_invalid_*.ttl` - Invalid data triggering specific validation errors

`example/` (canonical) and `example/raw/` each follow this same convention, validated
against their respective combined file. `test_validation.py` runs both and reports a
combined summary. There are no example fixtures for provenance — it isn't SHACL-shaped, so
there's nothing to validate against (see above).

## License

CC-BY-4.0

