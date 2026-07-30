# Contributing to the Open Pulse Ontology

Welcome! To keep our ontology stable, our history clean, and our releases predictable, we use an automated Semantic Versioning and Changelog workflow.

Please read these guidelines before contributing.

## 0. Ontology Source Files

This repo models **three separate ontologies**, one per stage of the extract → unify →
canonical pipeline. They share a common base (`ontology-definitions-canonical.ttl` /
`ontology-enumerations-canonical.ttl`) but are combined and validated independently — never load two
of them into the same SHACL shapes graph (see "Why raw is standalone" below).

### Shared base files

- `src/ontology/ontology-definitions-canonical.ttl` — the canonical ontology's own `owl:Ontology`
  header (`<https://open-pulse.epfl.ch/ontology#>`) plus the base classes and properties reused
  by all three ontologies.
- `src/ontology/ontology-enumerations-canonical.ttl` — the base enumeration classes and their instances (repository types, organization types, platforms, disciplines).

Raw and provenance each declare their **own** `owl:Ontology` header, in their own definitions
file (`<https://open-pulse.epfl.ch/ontology/raw#>`, `<https://open-pulse.epfl.ch/ontology/provenance#>`)
rather than inheriting the canonical one — they're combined and released together, but they
aren't the same ontology document. All three headers carry the same `owl:versionInfo`, bumped
together in lockstep (see "Preparing the Next Version" below); the canonical header remains the
source of truth the release bot reads.

### Canonical ontology

The deduplicated, query-friendly graph (`graph:canonical`): one value per functional
property, closed shapes, one node per real-world entity.

- `src/ontology/ontology-shapes-canonical.ttl` — reusable SHACL property shapes and node shapes.

`src/ontology/ontology-combined-canonical.ttl` is a **generated file** (shared base + the above), kept for tools and CI that expect a single ontology file (SHACL validation, releases, docs generation). Never edit it by hand.

### Raw ontology

Data exactly as extractors emit it, pre-unification: one `PlatformProfile`/`OrganizationProfile` per source, provisional identity (no ORCID/ROR required), open shapes, plus every platform-specific field needed for full field-parity with GitHub, Hugging Face, Zenodo and ORCID (internal/node IDs, repository file artifacts, Hugging Face Model/Dataset/Space fields, Zenodo Records/Communities, ORCID Employment/Education/Funding, etc).

- `src/ontology/ontology-definitions-raw.ttl` — includes raw's own `owl:Ontology` header.
- `src/ontology/ontology-enumerations-raw.ttl`
- `src/ontology/ontology-shapes-raw.ttl`

`src/ontology/ontology-combined-raw.ttl` is generated from the shared base + these three files.

**Why raw is standalone, not additive-to-canonical:** `sh:targetClass` applies to *every* node of that class across the whole loaded shapes graph. A looser raw shape (`sh:closed false`, no ORCID required) cannot coexist with the closed canonical `PersonShape`/`OrganizationShape` in the same shapes graph — SHACL would enforce both, and the closed one wins. So `ontology-shapes-raw.ttl` declares its own complete node shapes (`RawPersonShape`, `RawOrganizationShape`, `RawRepositoryShape`, etc.) rather than extending the canonical ones. New classes with no canonical counterpart (`Collection`, `Community`, `Funding`, `ExternalIdentifier`) keep their plain names, since there's no name collision to avoid.

### Provenance ontology

`graph:prov`: for a canonical triple, which platform-specific extraction it was derived
from. Recorded as RDF-star annotations directly on the quoted triple they explain (`<< s p
o >> prov:wasDerivedFrom <output> ; pulse:observationKind …`), not as a separately reified
node. This lives in its own graph — a canonical or raw entity never carries these
properties itself.

One `pulse:ExtractionRun` (a `prov:Activity`) can span several platforms in one batch; each
platform's raw output is its own `pulse:ExtractionOutput` (a `prov:Entity`) whose IRI *is*
the named-graph IRI of that platform's substrate graph. Sibling outputs from the same run
are connected by sharing the same `prov:wasGeneratedBy` target — not by nesting
`prov:Bundle` (PROV bundles can't nest, and base PROV-O has no native bundle-to-bundle
link). `graph:prov` itself is the one graph in this ontology correctly typed `prov:Bundle`,
since its content genuinely is provenance descriptions — self-describing, the same pattern
as this repo's `owl:Ontology` header.

- `src/ontology/ontology-definitions-provenance.ttl` — the vocabulary, plus provenance's own `owl:Ontology` header.
- `src/ontology/ontology-shapes-provenance.ttl` — shapes for the plain-RDF parts only
  (`pulse:ExtractionRun`). **The RDF-star winner-links themselves can't be SHACL-shaped** —
  no tool in this repo's stack can target a quoted triple as a focus node (rdflib can't
  parse Turtle-star; pySHACL has no RDF-star support) — so there's no shape and no example
  fixture for those, just the `rdfs:comment` patterns in the definitions file and a
  non-parseable illustrative fixture (`example/provenance/example_provenance_graph.ttl`).
  `pulse:ExtractionOutput` is shaped in `ontology-shapes-raw.ttl` instead, since its
  self-describing header is asserted inside the raw substrate graph it names, not inside
  `graph:prov`.

`src/ontology/ontology-combined-provenance.ttl` is generated from the shared base + these two files.

### Regenerating

After editing any source file, regenerate all three combined outputs in one step:

```bash
uv run python tools/python/build/combine_ontology.py
```

Commit the regenerated `ontology-combined-canonical.ttl`, `ontology-combined-raw.ttl`, and `ontology-combined-provenance.ttl` together with your source changes.

## 1. Branching Strategy

We use a two-branch model to protect production data:

- **`main`**: The stable, production-ready ontology. Never push or merge directly to `main`.
- **`develop`**: The active development branch. All new features and fixes are merged here first.
- **`feature/*`, `fix/*`, `docs/*`**: Temporary branches you create off `develop` for your day-to-day work.

## 2. Commit Message Conventions

We use **Conventional Commits**. Our CI/CD pipeline reads your commit messages to automatically generate `CHANGELOG.md` and GitHub Release notes.

**Format:** `<type>(<optional scope>): <description>`

- **`feat`**: A new class, property, or tool. (Appears under "Features")
- **`fix`**: Correcting logic, cardinalities, or bugs. (Appears under "Bug Fixes")
- **`docs`**: Updates to documentation. (Appears under "Documentation")
- **`chore`**: CI updates, formatting, or minor tasks. (Ignored in the changelog)

**Example:**

`feat(scope): add feature XYZ`

## 3. Everyday Development (How to Contribute)

During normal development, you are just adding work to the `develop` bucket.

1. Create a branch off `develop` (e.g., `git checkout -b feature/new-logic`).
2. Make your changes (edit the shared base files, or the canonical/raw/provenance source files for the ontology you're changing — see [Section 0](#0-ontology-source-files) — add scripts, update `README`).
3. Regenerate all three `ontology-combined*.ttl` files (see [Section 0](#0-ontology-source-files)) and include them in your commit.
4. Open a Pull Request into `develop` and merge it.

🛑 **CRITICAL:** Do **NOT** remove the `-develop` suffix from `owl:versionInfo` in
`src/ontology/ontology-definitions-canonical.ttl`, `ontology-definitions-raw.ttl`, or
`ontology-definitions-provenance.ttl` during this phase. Just merge your code. The release bot
will handle versions and collect your commits later.

## 4. Preparing the Next Version (In Develop)

After a production release is finished, or when starting a new milestone, ensure the `develop` branch reflects the *upcoming* version with a pre-release suffix.

1. On the `develop` branch, open `src/ontology/ontology-definitions-canonical.ttl`,
   `ontology-definitions-raw.ttl`, and `ontology-definitions-provenance.ttl`.
2. Update the `owl:versionInfo` triple in **all three** files to the same next anticipated
   version with a development suffix (e.g., bump `v2.2.0` to `v2.3.0-develop`). The canonical
   file is the source of truth the release bot reads, but all three must match.
3. Regenerate all three `ontology-combined*.ttl` files (see [Section 0](#0-ontology-source-files)).
4. Commit these changes directly or via a quick PR to `develop`.

## 5. Promoting to Production (Stable Release)

When enough features have accumulated in `develop` and you are ready to cut an official production release, we use GitHub Actions to automate the process.

**Step A: Generate the Release PR**
1. Go to the **Actions** tab in GitHub.
2. Select the **Prepare Production Release** workflow.
3. Click **Run workflow** (ensure the branch is set to `develop`).

*The bot will automatically strip the `-develop` suffix, generate the `CHANGELOG.md` using your commit history, and open a Pull Request into `main`.*

**Step B: Merge and Publish**
4. Review the automated PR to ensure the changelog and version look correct.
5. Click **Merge**.

*Merging this PR automatically triggers the **Publish Stable Release** workflow in the background. It will read the merged files, create the official Git Tag, and publish the "Latest Release" badge and notes to the GitHub repository.*