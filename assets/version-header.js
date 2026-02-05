/**
 * Open Pulse Ontology - Enhanced Version Header Component
 * 
 * Features:
 * - Version selector dropdown with simplified view
 * - Commit navigator row with left/right navigation
 * - Full-screen modal for all versions/commits
 * - Regex-capable search bar
 */

(function() {
  'use strict';

  // Configuration paths
  const CONFIG_PATH = '/config.json';
  const VERSIONS_PATH = '/versions.json';

  // State
  let config = null;
  let versionsData = null;
  let currentBranch = null;
  let currentCommit = null;
  let currentRelease = null;
  let isSearchOpen = false;
  let isModalOpen = false;
  let activeModalTab = 'releases';

  // ============================================
  // Utility Functions
  // ============================================

  function getBasePath() {
    const path = window.location.pathname;
    // Handle GitHub Pages subdirectory deployment
    const match = path.match(/^(\/[^/]+)?\/(branches|versions)\//);
    if (match && match[1]) {
      return match[1];
    }
    return '';
  }

  function parseCurrentLocation() {
    const path = window.location.pathname;
    const basePath = getBasePath();
    const relativePath = basePath ? path.replace(basePath, '') : path;

    // Check if viewing a branch: /branches/{name}/{commit}/
    const branchMatch = relativePath.match(/^\/branches\/([^/]+)\/([^/]+)\//);
    if (branchMatch) {
      return { type: 'branch', branch: branchMatch[1], commit: branchMatch[2] };
    }

    // Check if viewing a release: /versions/{tag}/
    const releaseMatch = relativePath.match(/^\/versions\/([^/]+)\//);
    if (releaseMatch) {
      return { type: 'release', tag: releaseMatch[1] };
    }

    return { type: 'unknown' };
  }

  async function fetchJSON(url) {
    try {
      const response = await fetch(url);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } catch (error) {
      console.warn(`Failed to fetch ${url}:`, error);
      return null;
    }
  }

  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  function formatDate(dateStr) {
    try {
      const date = new Date(dateStr);
      return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
      });
    } catch {
      return dateStr;
    }
  }

  // ============================================
  // Path Builders
  // ============================================

  function getBranchCommitPath(branch, commit) {
    const basePath = getBasePath();
    return `${basePath}/branches/${branch}/${commit}/index.html`;
  }

  function getReleasePath(tag) {
    const basePath = getBasePath();
    return `${basePath}/versions/${tag}/index.html`;
  }

  function getGitHubCommitUrl(commit) {
    return `${config.repository}/commit/${commit}`;
  }

  function getGitHubUserUrl(username) {
    return `https://github.com/${username}`;
  }

  // ============================================
  // Sorting Functions
  // ============================================

  function sortReleasesBySemver(releases) {
    return [...releases].sort((a, b) => {
      const aParts = a.tag.replace(/^v/, '').split('.').map(Number);
      const bParts = b.tag.replace(/^v/, '').split('.').map(Number);
      for (let i = 0; i < Math.max(aParts.length, bParts.length); i++) {
        const diff = (bParts[i] || 0) - (aParts[i] || 0);
        if (diff !== 0) return diff;
      }
      return 0;
    });
  }

  function sortBranchesByPriority(branchNames) {
    const priority = config.priorityBranches || ['main', 'develop'];
    return [...branchNames].sort((a, b) => {
      const aIdx = priority.indexOf(a);
      const bIdx = priority.indexOf(b);
      if (aIdx !== -1 && bIdx !== -1) return aIdx - bIdx;
      if (aIdx !== -1) return -1;
      if (bIdx !== -1) return 1;
      return a.localeCompare(b);
    });
  }

  function sortBranchesByLatestCommit(branchNames) {
    // Sort branches by their most recent commit date (newest first)
    return [...branchNames].sort((a, b) => {
      const aCommits = versionsData.branches[a]?.commits || [];
      const bCommits = versionsData.branches[b]?.commits || [];
      const aDate = aCommits[0]?.date || '1970-01-01';
      const bDate = bCommits[0]?.date || '1970-01-01';
      return bDate.localeCompare(aDate); // Descending order (newest first)
    });
  }

  // ============================================
  // Search Functions
  // ============================================

  function searchVersions(query) {
    const results = { releases: [], branches: [], commits: [] };
    if (!query.trim()) return results;

    let regex;
    try {
      regex = new RegExp(query, 'i');
    } catch {
      // Invalid regex, use simple includes
      regex = { test: (str) => str.toLowerCase().includes(query.toLowerCase()) };
    }

    // Search releases
    versionsData.releases.forEach(release => {
      if (regex.test(release.tag) || regex.test(release.message || '')) {
        results.releases.push(release);
      }
    });

    // Search branches and commits
    Object.entries(versionsData.branches).forEach(([branchName, branchData]) => {
      if (regex.test(branchName)) {
        results.branches.push({ name: branchName, latestCommit: branchData.commits[0] });
      }

      branchData.commits.forEach(commit => {
        if (regex.test(commit.hash) || regex.test(commit.message || '') || regex.test(commit.author)) {
          results.commits.push({ branch: branchName, ...commit });
        }
      });
    });

    // Limit results
    results.releases = results.releases.slice(0, 5);
    results.branches = results.branches.slice(0, 5);
    results.commits = results.commits.slice(0, 5);

    return results;
  }

  // ============================================
  // HTML Builders
  // ============================================

  function buildHeader() {
    const location = parseCurrentLocation();
    currentBranch = location.branch || null;
    currentCommit = location.commit || null;
    currentRelease = location.tag || null;

    // Determine current display name
    let currentDisplay = 'Select version';
    let badgeHtml = '';

    if (location.type === 'release') {
      currentDisplay = location.tag;
      const isLatest = location.tag === versionsData.latestRelease;
      badgeHtml = isLatest 
        ? '<span class="version-badge latest">latest</span>'
        : '<span class="version-badge release">release</span>';
    } else if (location.type === 'branch') {
      currentDisplay = location.branch;
      const isPriority = (config.priorityBranches || []).includes(location.branch);
      badgeHtml = isPriority
        ? '<span class="version-badge dev">dev</span>'
        : '<span class="version-badge branch">branch</span>';
    }

    // Build dropdown content
    const dropdownHtml = buildDropdownContent(location);

    // Build commit navigator (only for branches)
    const commitNavHtml = location.type === 'branch' 
      ? buildCommitNav(location.branch, location.commit)
      : '';

    // Icons
    const icons = {
      dropdown: `<svg class="dropdown-arrow" width="12" height="12" viewBox="0 0 12 12" fill="currentColor"><path d="M2 4l4 4 4-4"/></svg>`,
      search: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/></svg>`,
      close: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6L6 18M6 6l12 12"/></svg>`,
      github: `<svg height="24" viewBox="0 0 16 16" width="24" fill="currentColor"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/></svg>`
    };

    return `
      <header class="version-header">
        <div class="header-main">
          <div class="header-left">
            <a href="${getBasePath()}/" class="header-title">${escapeHtml(config.title || 'Open Pulse Ontology')}</a>
          </div>
          <div class="header-center">
            <div class="version-selector">
              <button class="version-button" aria-haspopup="true" aria-expanded="false">
                <span class="current-version">${escapeHtml(currentDisplay)}</span>
                ${badgeHtml}
                ${icons.dropdown}
              </button>
              <div class="version-dropdown" role="menu">
                ${dropdownHtml}
              </div>
            </div>
          </div>
          <div class="header-right">
            <div class="search-container">
              <button class="search-toggle" aria-label="Search versions">
                ${icons.search}
              </button>
              <div class="search-input-wrapper">
                <input type="text" class="search-input" placeholder="Search tags, branches, commits..." aria-label="Search">
                <button class="search-close" aria-label="Close search">
                  ${icons.close}
                </button>
              </div>
              <div class="search-results"></div>
            </div>
            <a href="${config.repository || '#'}" class="github-link" target="_blank" rel="noopener noreferrer" title="View on GitHub">
              ${icons.github}
            </a>
          </div>
        </div>
        ${commitNavHtml}
      </header>
      ${buildModal()}
    `;
  }

  function buildDropdownContent(location) {
    const releases = sortReleasesBySemver(versionsData.releases);
    // Sort branches by latest commit date (newest first)
    const branchNames = sortBranchesByLatestCommit(Object.keys(versionsData.branches));

    const maxReleases = config.maxDropdownReleases || 3;
    const maxBranches = config.maxDropdownBranches || 5;

    let html = '';

    // Releases section
    if (releases.length > 0) {
      html += '<div class="version-group"><div class="version-group-label">Releases</div>';
      releases.slice(0, maxReleases).forEach(release => {
        const isLatest = release.tag === versionsData.latestRelease;
        const isCurrent = location.type === 'release' && location.tag === release.tag;
        html += `
          <a href="${getReleasePath(release.tag)}" class="version-option ${isCurrent ? 'current' : ''}">
            ${escapeHtml(release.tag)}
            ${isLatest ? '<span class="option-badge latest">latest</span>' : ''}
          </a>`;
      });
      html += '</div>';
    }

    // Branches section - sorted by latest commit, show up to maxBranches
    const displayBranches = branchNames.slice(0, maxBranches);

    if (displayBranches.length > 0) {
      html += '<div class="version-group"><div class="version-group-label">Branches (by recent activity)</div>';
      displayBranches.forEach(branchName => {
        const branchData = versionsData.branches[branchName];
        const latestCommit = branchData.commits[0];
        const isCurrent = location.type === 'branch' && location.branch === branchName;
        const isPriority = (config.priorityBranches || []).includes(branchName);
        html += `
          <a href="${getBranchCommitPath(branchName, latestCommit.hash)}" class="version-option ${isCurrent ? 'current' : ''}">
            ${escapeHtml(branchName)}
            ${isPriority ? '<span class="option-badge dev">dev</span>' : ''}
          </a>`;
      });
      html += '</div>';
    }

    // View all button
    html += '<button class="view-all-btn" data-action="open-modal">View all versions...</button>';

    return html;
  }

  function buildCommitNav(branchName, currentCommitHash) {
    const branchData = versionsData.branches[branchName];
    if (!branchData || !branchData.commits) return '';

    const commits = branchData.commits;
    const currentIndex = commits.findIndex(c => c.hash === currentCommitHash);
    const commit = commits[currentIndex] || commits[0];

    // Commits are sorted newest first (index 0 = newest)
    // "Previous" = older commits = higher index (to the left)
    // "Next" = newer commits = lower index (to the right)
    const hasOlder = currentIndex < commits.length - 1;
    const hasNewer = currentIndex > 0;
    const olderCommit = hasOlder ? commits[currentIndex + 1] : null;
    const newerCommit = hasNewer ? commits[currentIndex - 1] : null;

    // Count commits on each side
    const olderCount = commits.length - 1 - currentIndex;  // commits after current
    const newerCount = currentIndex;  // commits before current

    const icons = {
      left: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M15 18l-6-6 6-6"/></svg>`,
      right: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg>`
    };

    return `
      <div class="commit-nav">
        <div class="commit-nav-content">
          <div class="commit-nav-arrow-group">
            <button class="commit-nav-btn" ${hasOlder ? `data-href="${getBranchCommitPath(branchName, olderCommit.hash)}"` : 'disabled'} title="${hasOlder ? 'Previous (older) commit' : 'No older commits'}">
              ${icons.left}
            </button>
            <span class="commit-nav-count">${olderCount}</span>
          </div>
          <div class="commit-info">
            <a href="${getGitHubCommitUrl(commit.hash)}" class="commit-hash" target="_blank" rel="noopener" title="View on GitHub">
              ${escapeHtml(commit.hash.substring(0, 7))}
            </a>
            <span class="commit-date">${formatDate(commit.date)}</span>
            <a href="${getGitHubUserUrl(commit.author)}" class="commit-author" target="_blank" rel="noopener">
              <span class="commit-author-avatar"></span>
              <span>@${escapeHtml(commit.author)}</span>
            </a>
            <span class="commit-message">"${escapeHtml(commit.message || '')}"</span>
            <span class="commit-position">${currentIndex + 1}/${commits.length}</span>
          </div>
          <div class="commit-nav-arrow-group">
            <span class="commit-nav-count">${newerCount}</span>
            <button class="commit-nav-btn" ${hasNewer ? `data-href="${getBranchCommitPath(branchName, newerCommit.hash)}"` : 'disabled'} title="${hasNewer ? 'Next (newer) commit' : 'No newer commits'}">
              ${icons.right}
            </button>
          </div>
        </div>
      </div>
    `;
  }

  function buildModal() {
    const icons = {
      close: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6L6 18M6 6l12 12"/></svg>`,
      chevron: `<svg class="branch-accordion-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 9l6 6 6-6"/></svg>`
    };

    // Build releases table
    const releases = sortReleasesBySemver(versionsData.releases);
    let releasesHtml = `
      <table class="releases-table">
        <thead>
          <tr>
            <th>Tag</th>
            <th>Date</th>
            <th>Author</th>
            <th>Commit</th>
          </tr>
        </thead>
        <tbody>`;
    
    releases.forEach(release => {
      const isLatest = release.tag === versionsData.latestRelease;
      releasesHtml += `
        <tr>
          <td>
            <a href="${getReleasePath(release.tag)}" class="tag-link">
              ${escapeHtml(release.tag)}
              ${isLatest ? ' <span class="option-badge latest">latest</span>' : ''}
            </a>
          </td>
          <td>${formatDate(release.date)}</td>
          <td>@${escapeHtml(release.author)}</td>
          <td>
            <a href="${getGitHubCommitUrl(release.commit)}" class="commit-link" target="_blank" rel="noopener">
              ${escapeHtml(release.commit.substring(0, 7))}
            </a>
          </td>
        </tr>`;
    });
    releasesHtml += '</tbody></table>';

    // Build branches accordion - sorted by latest commit date
    const branchNames = sortBranchesByLatestCommit(Object.keys(versionsData.branches));
    let branchesHtml = '';

    branchNames.forEach(branchName => {
      const branchData = versionsData.branches[branchName];
      const isPriority = (config.priorityBranches || []).includes(branchName);
      
      branchesHtml += `
        <div class="branch-accordion" data-branch="${escapeHtml(branchName)}">
          <button class="branch-header" aria-expanded="false">
            <span>
              <span class="branch-name">${escapeHtml(branchName)}</span>
              ${isPriority ? ' <span class="option-badge dev">dev</span>' : ''}
            </span>
            <span>
              <span class="branch-commit-count">${branchData.commits.length} commits</span>
              ${icons.chevron}
            </span>
          </button>
          <div class="branch-commits">`;

      branchData.commits.forEach(commit => {
        branchesHtml += `
          <a href="${getBranchCommitPath(branchName, commit.hash)}" class="branch-commit-item">
            <span class="branch-commit-hash">${escapeHtml(commit.hash.substring(0, 7))}</span>
            <span class="branch-commit-message">${escapeHtml(commit.message || '')}</span>
            <span class="branch-commit-meta">
              <span>@${escapeHtml(commit.author)}</span>
              <span>${formatDate(commit.date)}</span>
            </span>
          </a>`;
      });

      branchesHtml += '</div></div>';
    });

    return `
      <div class="version-modal-overlay" role="dialog" aria-modal="true" aria-labelledby="modal-title">
        <div class="version-modal">
          <div class="modal-header">
            <h2 class="modal-title" id="modal-title">All Versions</h2>
            <button class="modal-close" aria-label="Close modal">
              ${icons.close}
            </button>
          </div>
          <div class="modal-search">
            <input type="text" class="modal-search-input" placeholder="Filter by tag, branch, commit, or message (supports regex)...">
          </div>
          <div class="modal-tabs">
            <button class="modal-tab active" data-tab="releases">Releases (${releases.length})</button>
            <button class="modal-tab" data-tab="branches">Branches (${branchNames.length})</button>
          </div>
          <div class="modal-content">
            <div class="modal-section active" data-section="releases">
              ${releases.length > 0 ? releasesHtml : '<p class="search-no-results">No releases found.</p>'}
            </div>
            <div class="modal-section" data-section="branches">
              ${branchNames.length > 0 ? branchesHtml : '<p class="search-no-results">No branches found.</p>'}
            </div>
          </div>
        </div>
      </div>
    `;
  }

  function buildSearchResults(results) {
    const hasResults = results.releases.length > 0 || results.branches.length > 0 || results.commits.length > 0;

    if (!hasResults) {
      return '<div class="search-no-results">No matches found</div>';
    }

    let html = '';

    if (results.releases.length > 0) {
      html += '<div class="search-results-group"><div class="search-results-label">Releases</div>';
      results.releases.forEach(release => {
        html += `
          <a href="${getReleasePath(release.tag)}" class="search-result-item">
            <span>${escapeHtml(release.tag)}</span>
            ${release.tag === versionsData.latestRelease ? '<span class="option-badge latest">latest</span>' : ''}
          </a>`;
      });
      html += '</div>';
    }

    if (results.branches.length > 0) {
      html += '<div class="search-results-group"><div class="search-results-label">Branches</div>';
      results.branches.forEach(branch => {
        html += `
          <a href="${getBranchCommitPath(branch.name, branch.latestCommit.hash)}" class="search-result-item">
            <span>${escapeHtml(branch.name)}</span>
          </a>`;
      });
      html += '</div>';
    }

    if (results.commits.length > 0) {
      html += '<div class="search-results-group"><div class="search-results-label">Commits</div>';
      results.commits.forEach(commit => {
        html += `
          <a href="${getBranchCommitPath(commit.branch, commit.hash)}" class="search-result-item">
            <span class="hash">${escapeHtml(commit.hash.substring(0, 7))}</span>
            <span>${escapeHtml(commit.message || commit.branch)}</span>
          </a>`;
      });
      html += '</div>';
    }

    return html;
  }

  // ============================================
  // Event Handlers
  // ============================================

  function initEventListeners() {
    // Version dropdown
    const versionButton = document.querySelector('.version-button');
    const versionDropdown = document.querySelector('.version-dropdown');

    if (versionButton && versionDropdown) {
      versionButton.addEventListener('click', (e) => {
        e.stopPropagation();
        const isExpanded = versionButton.getAttribute('aria-expanded') === 'true';
        versionButton.setAttribute('aria-expanded', !isExpanded);
        versionDropdown.classList.toggle('open');
      });
    }

    // View all button
    const viewAllBtn = document.querySelector('.view-all-btn');
    if (viewAllBtn) {
      viewAllBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        openModal();
      });
    }

    // Search
    const searchToggle = document.querySelector('.search-toggle');
    const searchWrapper = document.querySelector('.search-input-wrapper');
    const searchInput = document.querySelector('.search-input');
    const searchClose = document.querySelector('.search-close');
    const searchResults = document.querySelector('.search-results');

    if (searchToggle && searchWrapper && searchInput) {
      searchToggle.addEventListener('click', () => {
        isSearchOpen = true;
        searchWrapper.classList.add('open');
        searchInput.focus();
      });

      searchClose.addEventListener('click', () => {
        closeSearch();
      });

      searchInput.addEventListener('input', (e) => {
        const query = e.target.value;
        if (query.length >= 2) {
          const results = searchVersions(query);
          searchResults.innerHTML = buildSearchResults(results);
          searchResults.classList.add('open');
        } else {
          searchResults.classList.remove('open');
        }
      });

      searchInput.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
          closeSearch();
        }
      });
    }

    // Commit nav buttons
    document.querySelectorAll('.commit-nav-btn[data-href]').forEach(btn => {
      btn.addEventListener('click', () => {
        window.location.href = btn.dataset.href;
      });
    });

    // Modal
    const modalOverlay = document.querySelector('.version-modal-overlay');
    const modalClose = document.querySelector('.modal-close');
    const modalTabs = document.querySelectorAll('.modal-tab');
    const modalSearchInput = document.querySelector('.modal-search-input');

    if (modalClose) {
      modalClose.addEventListener('click', closeModal);
    }

    if (modalOverlay) {
      modalOverlay.addEventListener('click', (e) => {
        if (e.target === modalOverlay) {
          closeModal();
        }
      });
    }

    modalTabs.forEach(tab => {
      tab.addEventListener('click', () => {
        const tabName = tab.dataset.tab;
        modalTabs.forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        document.querySelectorAll('.modal-section').forEach(section => {
          section.classList.toggle('active', section.dataset.section === tabName);
        });
        activeModalTab = tabName;
      });
    });

    // Branch accordions
    document.querySelectorAll('.branch-header').forEach(header => {
      header.addEventListener('click', () => {
        const isExpanded = header.getAttribute('aria-expanded') === 'true';
        header.setAttribute('aria-expanded', !isExpanded);
        const commits = header.nextElementSibling;
        commits.classList.toggle('open');
      });
    });

    // Modal search/filter
    if (modalSearchInput) {
      modalSearchInput.addEventListener('input', (e) => {
        filterModalContent(e.target.value);
      });
    }

    // Close dropdowns on outside click
    document.addEventListener('click', () => {
      if (versionButton) {
        versionButton.setAttribute('aria-expanded', 'false');
        versionDropdown.classList.remove('open');
      }
      if (searchResults) {
        searchResults.classList.remove('open');
      }
    });

    // Keyboard navigation
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        if (isModalOpen) {
          closeModal();
        } else if (isSearchOpen) {
          closeSearch();
        }
      }
    });
  }

  function closeSearch() {
    isSearchOpen = false;
    const searchWrapper = document.querySelector('.search-input-wrapper');
    const searchInput = document.querySelector('.search-input');
    const searchResults = document.querySelector('.search-results');
    
    if (searchWrapper) searchWrapper.classList.remove('open');
    if (searchInput) searchInput.value = '';
    if (searchResults) searchResults.classList.remove('open');
  }

  function openModal() {
    isModalOpen = true;
    const modal = document.querySelector('.version-modal-overlay');
    if (modal) {
      modal.classList.add('open');
      document.body.style.overflow = 'hidden';
      const searchInput = modal.querySelector('.modal-search-input');
      if (searchInput) searchInput.focus();
    }
  }

  function closeModal() {
    isModalOpen = false;
    const modal = document.querySelector('.version-modal-overlay');
    if (modal) {
      modal.classList.remove('open');
      document.body.style.overflow = '';
    }
  }

  function filterModalContent(query) {
    if (!query.trim()) {
      // Show all
      document.querySelectorAll('.releases-table tbody tr').forEach(row => {
        row.style.display = '';
      });
      document.querySelectorAll('.branch-accordion').forEach(accordion => {
        accordion.style.display = '';
        accordion.querySelectorAll('.branch-commit-item').forEach(item => {
          item.style.display = '';
        });
      });
      return;
    }

    let regex;
    try {
      regex = new RegExp(query, 'i');
    } catch {
      regex = { test: (str) => str.toLowerCase().includes(query.toLowerCase()) };
    }

    // Filter releases table
    document.querySelectorAll('.releases-table tbody tr').forEach(row => {
      const text = row.textContent;
      row.style.display = regex.test(text) ? '' : 'none';
    });

    // Filter branches and commits
    document.querySelectorAll('.branch-accordion').forEach(accordion => {
      const branchName = accordion.dataset.branch;
      const branchMatches = regex.test(branchName);
      
      let hasVisibleCommits = false;
      accordion.querySelectorAll('.branch-commit-item').forEach(item => {
        const text = item.textContent;
        const matches = regex.test(text);
        item.style.display = matches ? '' : 'none';
        if (matches) hasVisibleCommits = true;
      });

      accordion.style.display = (branchMatches || hasVisibleCommits) ? '' : 'none';
    });
  }

  // ============================================
  // Initialization
  // ============================================

  async function init() {
    const basePath = getBasePath();

    // Load configuration and versions
    [config, versionsData] = await Promise.all([
      fetchJSON(basePath + CONFIG_PATH),
      fetchJSON(basePath + VERSIONS_PATH)
    ]);

    if (!config || !versionsData) {
      console.warn('Version header: Could not load configuration files');
      return;
    }

    // Create and inject header
    const headerHTML = buildHeader();
    const headerElement = document.createElement('div');
    headerElement.innerHTML = headerHTML;

    // Insert header at the beginning of body
    while (headerElement.firstChild) {
      document.body.insertBefore(headerElement.firstChild, document.body.firstChild);
    }

    // Add body padding to account for fixed header
    const location = parseCurrentLocation();
    const headerHeight = location.type === 'branch' ? 96 : 56; // 56 + 40 for commit nav
    document.body.style.paddingTop = headerHeight + 'px';

    // Initialize event listeners
    initEventListeners();
  }

  // Run when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
