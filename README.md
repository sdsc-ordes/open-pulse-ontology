# Open Pulse Ontology

An RDF ontology for modeling contributions to open source scientific software and research articles from EPFL organizations and researchers.

## Overview

The Open Pulse Ontology provides a structured vocabulary and validation rules (SHACL shapes) for capturing metrics about:

- **People**: Researchers and contributors with GitHub usernames, ORCID identifiers, and institutional affiliations
- **Organizations**: Universities, research institutions, and companies with ROR identifiers and GitHub handles
- **Software Repositories**: GitHub repositories with metadata, ownership, and contribution tracking
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

## Validation

### Running Validation

```bash
# Validate test data
uv run python tools/python/checks/shacl.py example/test_dataset_large_example.ttl ontology-combined.ttl

# Run full test suite
uv run python tools/python/checks/test_validation.py
```

### Example Test Cases

The `example/` directory contains test files demonstrating both valid and invalid data patterns:

- `test_valid_*.ttl` - Valid data conforming to the ontology
- `test_invalid_*.ttl` - Invalid data triggering specific validation errors

## License

CC-BY-4.0

