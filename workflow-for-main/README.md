# GitHub Workflow for Main Branch

This folder contains the GitHub Action workflow that should be placed in the **main branch** (not the docs branch).

## Installation

1. Switch to the `main` branch
2. Copy `docs-deploy.yaml` to `.github/workflows/docs-deploy.yaml`
3. Commit and push

```bash
git checkout main
mkdir -p .github/workflows
cp /path/to/docs-deploy.yaml .github/workflows/
git add .github/workflows/docs-deploy.yaml
git commit -m "Add multi-version documentation deployment workflow"
git push origin main
```

## What It Does

1. **Triggers** on:
   - Push to any branch (except `docs`) when ontology files change
   - Creation of version tags (e.g., `v1.0.0`)
   - Manual workflow dispatch

2. **Generates** documentation:
   - Uses SHACL Play CLI to generate HTML documentation
   - Creates ontology diagram (SVG)
   - Injects enumeration tables
   - Adds version header references

3. **Deploys** to docs branch:
   - Creates a version folder (e.g., `/main/`, `/v1.0.0/`)
   - Updates `versions.json` with the new version
   - Commits and pushes to the `docs` branch

## Optional: Modify Existing Workflows

After adding this workflow, you may want to modify the existing `docs.yaml` workflow in main to prevent it from committing docs directly. Options:

1. **Remove it** - Let this new workflow handle everything
2. **Keep it for PR previews** - Modify it to only upload artifacts without committing

## Workflow File

See `docs-deploy.yaml` in this folder.
