# Contributing to the Open Pulse Ontology

Welcome! To keep our ontology stable, our history clean, and our releases predictable, we use an automated Semantic Versioning and Changelog workflow.

Please read these guidelines before contributing.

## 1. Branching Strategy

We use a two-branch model to protect production data:

- **`main`**: The stable, production-ready ontology. Never push or merge directly to `main`.
- **`develop`**: The active development branch. All new features and fixes are merged here first.
- **`feature/*`, `fix/*`, `docs/*`**: Temporary branches you create off `develop` for your day-to-day work.

## 2. Commit Message Conventions

We use **Conventional Commits**. Our CI/CD pipeline reads your commit messages to automatically generate `CHANGELOG.md`.

**Format:** `<type>(<optional scope>): <description>`

- **`feat`**: A new class, property, or tool. (Appears under "Features")
- **`fix`**: Correcting logic, cardinalities, or bugs. (Appears under "Bug Fixes")
- **`docs`**: Updates to documentation. (Appears under "Documentation")
- **`chore`**: CI updates, formatting, or minor tasks. (Ignored in the changelog)

**Example:**

```
feat(sensor): add temperature sensor class
```

## 3. Everyday Development (How to Contribute)

During normal development, you are just adding work to the `develop` bucket.

1. Create a branch off `develop` (e.g., `git checkout -b feature/new-logic`).
2. Make your changes (edit the ontology, add scripts, update `README`).
3. Open a Pull Request into `develop` and merge it.

🛑 **CRITICAL:** Do **NOT** change the `owl:versionInfo` in `ontology-combined.ttl` during this phase. Just merge your code. The release bot will collect your commits later.

## 4. Creating a Pre-Release (Cutting a Snapshot)

When enough features have accumulated in `develop` and you want to generate a testable snapshot:

1. Pull the latest `develop` branch to your local machine.
2. Open `ontology-combined.ttl` and update the `owl:versionInfo` triple with a development suffix (e.g., bump `v2.2.0` to `v2.3.0-develop`).
3. Commit this single change and push to `develop`:

```bash
git commit -am "chore: bump version to v2.3.0-develop"
git push origin develop
```

> **Note:** This automatically triggers a GitHub Action that groups all recent commits, updates the changelog, and creates a hidden Pre-release on GitHub.

## 5. Promoting to Production (Stable Release)

Once a `develop` pre-release has been validated, we promote it to `main`. You do not need to touch any code locally to do this.

1. Go to the **Actions** tab in GitHub.
2. Select the **Prepare Production Release** workflow.
3. Click **Run workflow** (leave the branch as `develop`).

The bot will automatically strip the `-develop` suffix, create a release branch, and open a Pull Request into `main`.

4. Review the automated PR and click **Merge**.

> **Note:** Merging this PR triggers the final pipeline, creating the official production release and updating the live documentation.