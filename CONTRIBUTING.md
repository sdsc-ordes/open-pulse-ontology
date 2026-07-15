# Contributing to the Open Pulse Ontology

Welcome! To keep our ontology stable, our history clean, and our releases predictable, we use an automated Semantic Versioning and Changelog workflow.

Please read these guidelines before contributing.

## 0. Ontology Source Files

The ontology is split by semantic aspect into three source files:

- `src/ontology/ontology-definitions.ttl` — the ontology header (`owl:versionInfo` lives here) plus classes and properties.
- `src/ontology/ontology-enumerations.ttl` — enumeration classes and their instances (repository types, organization types, platforms, disciplines).
- `src/ontology/ontology-shapes.ttl` — reusable SHACL property shapes and node shapes.

`src/ontology/ontology-combined.ttl` is a **generated file**, kept for tools and CI that expect a single ontology file (SHACL validation, releases, docs generation). Never edit it by hand.

After editing any of the three source files, regenerate it:

```bash
uv run python tools/python/build/combine_ontology.py
```

Commit the regenerated `src/ontology/ontology-combined.ttl` together with your source changes.

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
2. Make your changes (edit `src/ontology/ontology-definitions.ttl`, `src/ontology/ontology-enumerations.ttl`, or `src/ontology/ontology-shapes.ttl`, add scripts, update `README`).
3. Regenerate `src/ontology/ontology-combined.ttl` (see [Section 0](#0-ontology-source-files)) and include it in your commit.
4. Open a Pull Request into `develop` and merge it.

🛑 **CRITICAL:** Do **NOT** remove the `-develop` suffix from `owl:versionInfo` in `src/ontology/ontology-definitions.ttl` during this phase. Just merge your code. The release bot will handle versions and collect your commits later.

## 4. Preparing the Next Version (In Develop)

After a production release is finished, or when starting a new milestone, ensure the `develop` branch reflects the *upcoming* version with a pre-release suffix.

1. Open `src/ontology/ontology-definitions.ttl` on the `develop` branch.
2. Update the `owl:versionInfo` triple to the next anticipated version with a development suffix (e.g., bump `v2.2.0` to `v2.3.0-develop`).
3. Regenerate `src/ontology/ontology-combined.ttl` (see [Section 0](#0-ontology-source-files)).
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