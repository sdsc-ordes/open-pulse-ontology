# Open Pulse Ontology - Documentation Site

This branch (`docs`) contains the static documentation site for the Open Pulse Ontology, hosted on GitHub Pages.

## Branch Purpose

This is a **deployment-only branch**. It contains:
- Generated HTML documentation for all versions
- The version header component (CSS/JS)
- Site configuration files

**Do not commit ontology source files here.** Source files (`ontology.ttl`, `shapes.ttl`, etc.) live in the source branches (`main`, `develop`, feature branches).

## Folder Structure

```
docs/
├── index.html                          # Root redirect (to latest release)
├── config.json                         # Site configuration
├── versions.json                       # Version manifest (auto-updated by CI)
├── DOCS-README.md                      # This file
├── assets/
│   ├── version-header.css              # Header styles
│   └── version-header.js               # Header component logic
├── branches/
│   ├── main/
│   │   ├── {commit-hash}/              # One folder per commit
│   │   │   ├── index.html
│   │   │   └── ontology.svg
│   │   └── ...
│   ├── develop/
│   │   └── {commit-hash}/
│   │       └── ...
│   └── {feature-branch}/
│       └── {commit-hash}/
│           └── ...
├── versions/
│   ├── v0.1.0/
│   │   ├── index.html
│   │   └── ontology.svg
│   └── v0.2.0/
│       └── ...
└── workflow-for-main/
    ├── docs-deploy.yaml                # GitHub Action (copy to main branch)
    └── README.md
```

### Path Structure

- **Releases/Tags**: `/versions/{tag}/index.html`
  - Example: `/versions/v0.1.0/index.html`
  
- **Branch Commits**: `/branches/{branch-name}/{commit-hash}/index.html`
  - Example: `/branches/main/abc1234/index.html`
  - Example: `/branches/feature-auth/def5678/index.html`

## Configuration Files

### config.json

Site-wide settings:

```json
{
  "title": "Open Pulse Ontology",
  "repository": "https://github.com/open-pulse/open-pulse-ontology",
  "defaultVersion": "latest-release",
  "priorityBranches": ["main", "develop"],
  "maxDropdownReleases": 3,
  "maxDropdownBranches": 2,
  "commitHistoryLimit": 50
}
```

| Field | Description |
|-------|-------------|
| `title` | Site title shown in header |
| `repository` | GitHub repository URL |
| `defaultVersion` | Where root `/` redirects: `"latest-release"` or a specific tag/branch |
| `priorityBranches` | Branches shown in quick dropdown (ordered) |
| `maxDropdownReleases` | Max releases in quick dropdown |
| `maxDropdownBranches` | Max branches in quick dropdown |
| `commitHistoryLimit` | Max commits stored per branch |

### versions.json

Auto-maintained version manifest:

```json
{
  "releases": [
    {
      "tag": "v0.1.0",
      "path": "/versions/v0.1.0/",
      "date": "2026-01-15",
      "commit": "abc1234",
      "author": "username",
      "message": "Initial release"
    }
  ],
  "branches": {
    "main": {
      "commits": [
        {
          "hash": "def5678",
          "date": "2026-01-29",
          "author": "username",
          "message": "Update ontology..."
        }
      ]
    }
  },
  "latestRelease": "v0.1.0",
  "priorityBranches": ["main", "develop"]
}
```

## Header Features

The version header provides:

### 1. Version Selector Dropdown
- Quick access to latest releases and priority branches
- "View all versions..." button opens full modal

### 2. Commit Navigator (Branch Views Only)
- Left/right arrows to navigate commit history
- Shows: commit hash (links to GitHub), date, author, message
- Position indicator (e.g., "3/15")

### 3. Search Bar
- Click search icon to expand
- Searches across: tags, branch names, commit hashes, messages
- Supports regex patterns (e.g., `v0\.\d+` matches all v0.x)
- Shows categorized suggestions

### 4. Version Modal
- Full list of all releases and branches
- Filter/search functionality
- Expandable branch sections showing all commits

## Files Removed from This Branch

These files exist in source branches but were intentionally excluded from the docs branch:

| Removed | Reason |
|---------|--------|
| `ontology.ttl`, `shapes.ttl`, `ontology-combined.ttl` | Source files live in source branches |
| `openpulse_subset.ttl` | Source file |
| `main.py`, `gen.sh` | Development utilities |
| `src/`, `tools/`, `test/` | Source code and tooling |
| `.github/workflows/` | CI workflows live in main branch |
| `test-docs-workflow.sh` | Development script |
| `LICENSE`, `README.md` | Kept in source branches |

## GitHub Action Workflow

The `docs-deploy.yaml` workflow (located in `workflow-for-main/`) should be copied to the main branch at `.github/workflows/docs-deploy.yaml`.

### Triggers
- Push to any branch (except `docs`)
- Tag creation (`v*`)
- Manual dispatch

### What It Does
1. Generates HTML documentation from ontology files
2. Creates target folder based on trigger:
   - Tags → `versions/{tag}/`
   - Branches → `branches/{name}/{commit}/`
3. Injects header CSS/JS into generated HTML
4. Updates `versions.json` with new entry
5. Commits and pushes to `docs` branch

### Cleanup Job
Optionally removes documentation for deleted branches while preserving all tagged releases.

## Local Development

To test the site locally:

```bash
cd /path/to/docs-branch
python -m http.server 8000
```

Then open http://localhost:8000 in your browser.

## GitHub Pages Setup

1. Go to repository **Settings** → **Pages**
2. Source: **Deploy from a branch**
3. Branch: `docs` / `/ (root)`
4. Save

The site will be available at: `https://{org}.github.io/{repo}/`
