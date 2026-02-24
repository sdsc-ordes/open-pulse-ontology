# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.1] - 2026-02-24

### Miscellaneous Tasks

- Bump main to v2.1.0
- Add publish release action for post merge release promotion
- Hotfix the release/changelog workflow
- Small formatting/description edits
- Increment version
- Token permission for changelog step

## [2.1.0-develop] - 2026-02-23

### Bug Fixes

- **(tests)** Orcid is an identifier so test shouldn't have it
- **(tests)** Allign comment to reality
- **(tests)** Github sub org without identifier
- Update ontology
- RepositoryType enum
- Add reference to memberOf for schema:person
- Schema1 stuff
- Schema1 stuff
- Remove unused terms from ontology
- Remove relatedPublications object
- Schema1 thing + add to inject script
- Fix schema org
- Add URLshape to avoid redundancy
- Add git hash shape with regex + fix role cardinality
- Create Gender and Email shape for Person Properties
- Replace schema:Dataset property with custom property to avoid conflict in official description of property and align other properties with their original descriptions
- Update cardinalities + property types to class from node type
- Minor fixes + replace inverse properties with custom named properties
- Minor fixes + replace hasPart inverse properties with custom named properties
- Add inverse properties definition replacing hasPart property
- Update SoftwareSourceCode properties and restructure the file
- Fix discipline enumeration error
- Update GitUsernameShape
- Write descriptions of the properties and update the key
- Add descriptions of properties
- Restructure file for better readability
- Minor fixes and add shapes of github stats
- Standardize the case for property shapes
- Delete shacl play logs
- Add comments for organization and role properties and further standardize letter case
- Replace rdfs label with skos:prefLabel for repository and Organization type enumerations
- Replace rdfs label with skos:prefLabel for discipline enumeration
- Replace rdfs:comment with skos:definition, and rdfs:label with skos:prefLabel
- Fix + feat: update tests with new properties
- Rename revised_ontology file as ontology_combined
- Fix name of ontology-combined.ttl
- Fix ontology file name and add 'ontology-revision' branch in list of branches
- Update .gitignore
- Fix inject_enumerations.py to generate the documentation with accurate enum values
- Replace 'rdfs:Property' with 'rdf:Property' to pass Shacl validation quality check in Github (shacl-shacl.ttl)
- Set action to 'commit generated docs' for push event only
- Minor fixes in property labels and definitions
- Minor labels and comments related fixes
- Change skos prefix
- Remove inverse path property shape and replace full paths with relative path
- Github org url validation
- One last org url
- Remove old useless test
- Make tests more consistent with ontology, fix smal syntax errors
- Bare exception
- Remove old files
- First round of test fixing - urls
- Xone -> sh:or
- Ror test
- Forgot to attach two new shapes to their respective objects
- Docs drawing generation
- Docs svg empty namespace fix
- Also do it for the html docs
- Don't put enum elements inside svg - it doesn't like that
- Renaming yaml to avoid conflict
- Avoid triggering action on PRs
- Pulse:GithubRepositoryHandleShape fix. GH handle contains .
- DoiPropertyShape mandatory
- Information engineering wd identifier
- Remove old shapes file
- Updated regex pattern
- Remove useless commit messages from auto-changelog
- Renaming yaml to avoid conflict
- Improve tag existence check in changelog workflow
- Better parsing regex
- Show breaking changes in changelog
- Upload everything that is generated in docs
- Check for semver in version
- Remove old duplicate docs workflow
- Make all actions use uv, add explicit validation step in validate-test action
- Make all actions use uv, add explicit validation step in validate-test action
- Make all actions use uv, add explicit validation step in validate-test action
- Make all actions use uv, add explicit validation step in validate-test action
- Good lord let the merge conflict end
- Account for similar logic in organizational identifiers as persons, add owl:sameAs exception to ignoredProperties for future mapping purposes
- LessThanOrEquals for date omparisons (same day usecase)
- Remove useless commit messages from auto-changelog
- Renaming yaml to avoid conflict
- Improve tag existence check in changelog workflow
- Better parsing regex
- Show breaking changes in changelog
- Upload everything that is generated in docs
- Check for semver in version
- Remove old duplicate docs workflow
- Make all actions use uv, add explicit validation step in validate-test action
- Make all actions use uv, add explicit validation step in validate-test action
- Make all actions use uv, add explicit validation step in validate-test action
- Good lord let the merge conflict end

### Documentation

- Add contribution guidelines
- Add contribution guidelines

### Features

- Gen script for instances, tentris based notebook
- Align ontology with data model, actions and scripts for generation docs.
- Add enum lists
- Add properties for org to repositories and person to repositories  relationship
- Connect organization in membership shape properties with actual organization class
- Add DataSet class and link it with softwareSourceCode class
- Add comments for better documentation generation
- Add label names and comments to the class properties for better documentation
- Add example graph and dateCreated property in Repository shape
- Add example graph
- Add tests for the ontology
- Add pattern to check repository IRI
- Add valid tests
- Add organization type enumerations
- Add github stats as properties
- Add relatedToEPFL flag in software source code class
- Add more tests
- Add more tests
- Create github workflow to run tests and validate shacl ontology
- Add python based validation test file
- Add 'pulse' prefix everywhere, instead of 'ex'
- Align ontology better to reality
- Update test data
- Add link from contribution back to repository. Update tests accordingly
- Specify and constrain identifiers for people, org and repos, relax cardinalities for personal identifiers
- Manual dispatch
- Renaming index.html to docs.html for wrapper compatibility
- Add Readme
- Adding gh actions for docs
- Gh action for auto-changelog
- Manual dispatch
- Add larger test dataset
- Add larger test dataset
- Gh action for auto-changelog
- Manual dispatch

### Miscellaneous Tasks

- **(docs)** Use uv for python
- **(ontology)** Increment version number
- **(ontology)** Increment version number
- Update gitignore
- Align ontology with data
- Reformat python files with black
- Clean up, rename infoscienceUsername + tests
- Trigger ci
- Update documentation tool version
- Attempt docs ci fix
- Testing /docs branch ci
- Testing docs site
- Make docs gen only on main to prevent red crosses on ci
- Increment version
- Cleanup
- Add .env
- Increment version to 2.1.0
- Testing /docs branch ci
- Rename yml->yaml
- Rename yamls
- Rename changelog yaml->yml for consistency
- Rename yml->yaml
- Cleanup
- Increment version to 2.1.0
- Testing /docs branch ci
- Rename yml->yaml
- Rename yamls
- Rename changelog yaml->yml for consistency
- Rename yml->yaml
- Fix uv step in docs-versioned
- Formatting
- Formatting
- Fix uv python -> uv run
- Cleanup test comment
- Fix git cliff permissions
- Run ci and create pre-release

### Refactoring

- Re-work the -develop workflow with pre-releases
- Use uv, update docs
- Make sure gh actions also uses uv
- Make sure gh actions also uses uv
- Make sure gh actions also uses uv
- Make sure gh actions also uses uv
- Use uv, update docs
- Make sure gh actions also uses uv
- Re-work the -develop workflow with pre-releases
- Make sure gh actions also uses uv
- Make sure gh actions also uses uv
- Make sure gh actions also uses uv
- Make sure gh actions also uses uv

### Testing

- Testing ci
- Testing ci

### Update

- Add description of class properties except org:role


