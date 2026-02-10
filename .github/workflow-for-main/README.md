# GitHub Workflow for Documentation Deployment

This folder contains a **reference copy** of the GitHub Action workflow used for deploying versioned documentation. The actual workflow lives on source branches at `.github/workflows/docs-versioned.yaml`.

## Installation

If you need to set up the workflow on a new branch:

1. Switch to the target branch (e.g. `main`)
2. Commit and push

```bash
git checkout main
mkdir -p .github/workflows
cp .github/workflow-for-main/docs-deploy.yaml .github/workflows/docs-versioned.yaml
git add .github/workflows/docs-versioned.yaml
git commit -m "Add versioned documentation deployment workflow"
git push origin main
```

## What It Does

### Job 1: Generate Documentation (`generate-docs`)

1. Checks out the source branch/tag
2. Installs dependencies (Python, Java 11, Graphviz)
3. Downloads SHACL Play CLI
4. Generates HTML documentation from `ontology-combined.ttl`
5. Generates an SVG ontology diagram
6. Fixes SVG namespace issues
7. Injects enumeration values into the HTML
8. Uploads the generated docs as an artifact

### Job 2: Deploy to Docs Branch (`deploy-docs`)

1. Checks out the `docs` branch
2. Downloads the generated docs artifact
3. Determines the target folder:
   - Tags → `versions/{tag}/`
   - Branches → `branches/{name}/{commit}/`
4. **Renames** the generated `index.html` to `doc.html`
5. **Copies** `assets/index-header.html` as the new `index.html` (wrapper)
6. Updates `versions.json` with the new version entry
7. Commits and pushes to the `docs` branch

### Triggers

| Trigger | Condition |
|---------|-----------|
| Push | Any branch except `docs`, when ontology files change |
| Tag | Creation of `v*` tags |
| Manual | `workflow_dispatch` with optional branch/tag input |

## The Wrapper Pattern

The deploy step does **not** inject CSS/JS into the generated HTML. Instead it uses a wrapper:

```bash
# In the "Copy docs to target folder" step:
mv "$TARGET_PATH/index.html" "$TARGET_PATH/doc.html"
cp assets/index-header.html "$TARGET_PATH/index.html"
```

This produces the following structure in each version/branch folder:

```
{commit-hash}/
├── index.html      ← wrapper (from assets/index-header.html)
├── doc.html        ← generated documentation (renamed from index.html)
└── ontology.svg
```

### Why a wrapper instead of `sed` injection?

Branch names can contain slashes (e.g. `feat/docks-workflow`), which creates extra directory levels on the `docs` branch. The old approach used `sed` to inject `<link>` and `<script>` tags with relative paths (e.g. `../../../assets/`), but the number of `../` needed varies with the branch name depth:

| Branch | Path | Relative depth |
|--------|------|---------------|
| `main` | `branches/main/{hash}/` | `../../../assets/` |
| `feat/foo` | `branches/feat/foo/{hash}/` | `../../../../assets/` |

The wrapper eliminates this by using JavaScript to compute the correct absolute path at runtime from `window.location.pathname`.

### How the wrapper works

The wrapper `index.html`:

1. Extracts the site base path from the URL (e.g. `/open-pulse-ontology`)
2. Dynamically creates `<link>` and `<script>` elements for `version-header.css` and `version-header.js`
3. Embeds the documentation via `<iframe src="doc.html">`
4. Uses a fixed `margin-top: 92px` to sit below the version header bar

### Safety guard

`version-header.js` won't render inside the iframe thanks to:

```javascript
if (window.self !== window.top) return;
```

## Required Files on the Docs Branch

For the workflow to function, the `docs` branch must have:

| File | Purpose |
|------|---------|
| `assets/index-header.html` | Wrapper template copied into each folder |
| `assets/version-header.css` | Header component styles |
| `assets/version-header.js` | Header component logic (with iframe guard) |
| `config.json` | Site configuration |
| `versions.json` | Version manifest (created automatically if missing) |
| `.nojekyll` | Prevents GitHub Pages from running Jekyll |

## Keeping This Reference in Sync

When updating the actual workflow on source branches, remember to update this reference copy as well so the docs branch stays current. The source of truth is `.github/workflows/docs-versioned.yaml` on the active source branches.
