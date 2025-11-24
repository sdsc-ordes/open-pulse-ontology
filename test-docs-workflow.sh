#!/bin/bash
# Test script to locally run the full documentation generation workflow

set -e

echo "=== Testing Full Documentation Workflow ==="
echo ""

# Create docs directory if it doesn't exist
mkdir -p docs

echo "Step 1: Enriching ontology with SPARQL transformations..."
/home/rmfranken/open-pulse-ontology/.venv/bin/python tools/python/docs/sparql.py
echo "✓ Enriched ontology saved to /tmp/enriched.ttl"
echo ""

echo "Step 2: Checking if SHACL Play CLI exists..."
if [ ! -f "shacl-play-cli.jar" ]; then
    echo "  Downloading SHACL Play CLI..."
    wget -q https://github.com/sparna-git/shacl-play/releases/download/0.10.2/shacl-play-app-0.10.2-onejar.jar -O shacl-play-cli.jar
    echo "  ✓ Downloaded"
else
    echo "  ✓ Already exists"
fi
echo ""

echo "Step 3: Generating HTML documentation..."
java -jar shacl-play-cli.jar \
    doc \
    -d \
    -i /tmp/enriched.ttl \
    -l en \
    -o docs/index.html 2>&1 | grep -v "SLF4J" || true
echo "✓ Generated docs/index.html"
echo ""

echo "Step 4: Generating ontology diagram..."
java -jar shacl-play-cli.jar \
    draw \
    -i /tmp/enriched.ttl \
    -o docs/ontology.svg 2>&1 | grep -v "SLF4J" || true
echo "✓ Generated docs/ontology.svg"
echo ""

echo "Step 5: Injecting enumeration lists into HTML..."
/home/rmfranken/open-pulse-ontology/.venv/bin/python tools/python/docs/inject_enumerations.py ontology-combined.ttl docs/index.html
echo "✓ Enumerations injected"
echo ""

echo "=== Documentation Generation Complete ==="
echo ""
echo "Generated files:"
echo "  - docs/index.html"
echo "  - docs/ontology.svg"
echo ""
echo "To view the documentation, open docs/index.html in your browser."
