# Open Pulse Ontology - Documentation Site

This branch (`docs`) contains the static documentation site for the Open Pulse Ontology, hosted on GitHub Pages.

## Branch Purpose

This is a **deployment-only branch**. It contains:
- Generated HTML documentation for all versions
- The version header component (CSS/JS)
- The wrapper template for embedding documentation
- Site configuration files

**Do not commit ontology source files here.** Source files (`ontology.ttl`, `shapes.ttl`, etc.) live in the source branches (`main`, `develop`, feature branches).

## Folder Structure

```
docs/
├── index.html                          # Root redirect (to latest release)
├── config.json                         # Site configuration
├── versions.json                       # Version manifest (auto-updated by CI)
├── .nojekyll                           # Prevents Jekyll processing on GitHub Pages
├── README.md                           # This file
├── assets/
│   ├── index-header.html               # Wrapper template (copied into each version folder)
│   ├── version-header.css              # Header styles
│   └── version-header.js               # Header component logic
├── branches/
│   ├── main/
│   │   └── {commit-hash}/
│   │       ├── index.html              # Wrapper (loads header + embeds doc.html)
│   │       ├── doc.html                # Generated documentation
│   │       └── ontology.svg
│   ├── develop/
│   │   └── {commit-hash}/
│   │       └── ...
│   └── {feature-branch}/
│       └── {commit-hash}/
│           └── ...
├── versions/
│   ├── v0.1.0/
│   │   ├── index.html                  # Wrapper
│   │   ├── doc.html                    # Generated documentation
│   │   └── ontology.svg
│   └── ...
└── .github/
    └── workflow-for-main/
        ├── docs-deploy.yaml            # Reference copy of the GitHub Action
        └── README.md                   # Workflow documentation
```

### Path Structure

- **Releases/Tags**: `/versions/{tag}/index.html`
  - Example: `/versions/v0.1.0/index.html`
  
- **Branch Commits**: `/branches/{branch-name}/{commit-hash}/index.html`
  - Example: `/branches/main/abc1234/index.html`
  - Example: `/branches/feat/docks-workflow/def5678/index.html`

## How Documentation Pages Work

Each documentation page uses a **wrapper pattern** with two files:

| File | Role |
|------|------|
| `index.html` | Lightweight wrapper that loads the version header and embeds `doc.html` |
| `doc.html` | The actual generated documentation (from SHACL Play) |

### Wrapper (`index.html`)

The wrapper is a copy of `assets/index-header.html`. It does three things:

1. **Resolves the base path** from `window.location.pathname` using a regex (e.g. extracts `/open-pulse-ontology` from the full URL)
2. **Dynamically loads** `version-header.css` and `version-header.js` using that base path — no hardcoded relative paths
3. **Embeds** the generated documentation via `<iframe src="doc.html">`

```html
<!-- Simplified view of the wrapper -->
<script>
  var path = window.location.pathname;
  var match = path.match(/^(.*?)\/(branches|versions)\//);
  var basePath = match ? match[1] : '';
  // Creates <link> and <script> elements pointing to {basePath}/assets/...
</script>
<iframe id="doc-frame" src="doc.html"></iframe>
```

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
  "maxDropdownBranches": 5,
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

Auto-maintained version manifest (updated by CI on every deploy):

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

## GitHub Action Workflow

The documentation is deployed automatically by the `docs-versioned.yaml` workflow on source branches. A reference copy is kept at `.github/workflow-for-main/docs-deploy.yaml`.

### Triggers
- Push to any branch (except `docs`) when ontology files change
- Tag creation (`v*`)
- Manual dispatch

### What It Does
1. Generates HTML documentation from ontology files using SHACL Play CLI
2. Creates target folder based on trigger:
   - Tags → `versions/{tag}/`
   - Branches → `branches/{name}/{commit}/`
3. Renames generated `index.html` to `doc.html` and places the wrapper `index.html` (from `assets/index-header.html`)
4. Updates `versions.json` with new entry
5. Commits and pushes to `docs` branch

### Cleanup Job
Optionally removes documentation for deleted branches while preserving all tagged releases.

## Key Files on This Branch

| File | Purpose | Modified by |
|------|---------|-------------|
| `assets/index-header.html` | Wrapper template copied into each version/branch folder | Manual edits only |
| `assets/version-header.css` | Header styles | Manual edits only |
| `assets/version-header.js` | Header component (dropdown, search, commit nav, modal) | Manual edits only |
| `config.json` | Site configuration | Manual edits only |
| `versions.json` | Version manifest | CI (auto-updated on every deploy) |
| `index.html` | Root redirect page | Manual edits only |
| `.nojekyll` | Prevents GitHub Pages Jekyll processing | Should not be removed |

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
