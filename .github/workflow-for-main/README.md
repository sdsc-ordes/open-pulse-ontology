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

3. **Deploys** to docs branch:
   - Creates a version folder (e.g., `/main/`, `/v1.0.0/`)
   - Updates `versions.json` with the new version
   - Commits and pushes to the `docs` branch

## Important: Header Wrapper Pattern

The workflow uses a **wrapper `index.html`** instead of injecting CSS/JS into the generated documentation. This is required to support branch names with slashes (e.g. `feat/docks-workflow`).

### How it works

Each documentation folder ends up with this structure:

```
branches/feat/docks-workflow/0130a09/
├── index.html      ← wrapper (copied from assets/index-header.html)
├── doc.html        ← actual generated documentation (renamed from index.html)
└── ontology.svg
```

The wrapper `index.html`:
- Dynamically calculates the base path from `window.location.pathname`
- Loads `version-header.css` and `version-header.js` using **absolute paths** (no relative `../` needed)
- Displays the documentation content via `<iframe src="doc.html">`

### What the workflow does in the deploy step

```yaml
# Rename generated index.html to doc.html and use the header wrapper as index.html
if [ -f "$TARGET_PATH/index.html" ]; then
  mv "$TARGET_PATH/index.html" "$TARGET_PATH/doc.html"
  cp assets/index-header.html "$TARGET_PATH/index.html"
fi
```

### Required changes to your existing GitHub Action

If you already have a docs deployment workflow (`.github/workflows/docs.yaml` or similar) in the main branch, you need to update the deploy step. Look for any `sed` command that injects `version-header.css` / `version-header.js` into the generated HTML, such as:

```bash
# OLD approach (remove this) ❌
sed -i 's|<meta content="text/html; charset=utf-8"...|...\n<link rel="stylesheet" href="../../assets/version-header.css">...|'
```

Replace it with the rename + copy pattern:

```bash
# NEW approach ✅
if [ -f "$TARGET_PATH/index.html" ]; then
  mv "$TARGET_PATH/index.html" "$TARGET_PATH/doc.html"
  cp assets/index-header.html "$TARGET_PATH/index.html"
fi
```

### Why this was needed

The previous approach used `sed` to inject `<link>` and `<script>` tags with **relative paths** (e.g. `../../../assets/version-header.css`) into each generated `index.html`. This broke for branch names containing slashes:

| Branch | Directory depth | Required relative path |
|--------|----------------|----------------------|
| `main` | `branches/main/{commit}/` (3 levels) | `../../../assets/` |
| `feat/docks-workflow` | `branches/feat/docks-workflow/{commit}/` (4 levels) | `../../../../assets/` |

The wrapper approach eliminates this problem entirely since it uses JavaScript to compute the correct absolute path at runtime.

### Safety guard

`version-header.js` includes an iframe detection guard:

```javascript
if (window.self !== window.top) return;
```

This prevents the header from rendering inside the iframe if any old `doc.html` files still contain injected CSS/JS references from before this change.

## Optional: Modify Existing Workflows

After adding this workflow, you may want to modify the existing `docs.yaml` workflow in main to prevent it from committing docs directly. Options:

1. **Remove it** - Let this new workflow handle everything
2. **Keep it for PR previews** - Modify it to only upload artifacts without committing

## Workflow File

See `docs-deploy.yaml` in this folder.
