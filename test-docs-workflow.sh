#!/bin/bash
# Test script to run the docs workflow locally
set -e

echo "=== Testing Documentation Workflow Locally ==="
echo ""

# Step 1: Set up Python and install dependencies
echo "Step 1: Checking Python dependencies..."
/home/rmfranken/open-pulse-ontology/.venv/bin/python -m pip install --quiet rdflib
echo "✅ Python dependencies installed"
echo ""

# Step 2: Enrich ontology with rdflib
echo "Step 2: Enriching ontology..."
/home/rmfranken/open-pulse-ontology/.venv/bin/python tools/python/docs/sparql.py
ENRICHED_FILE="/tmp/enriched.ttl"
echo "✅ Enriched ontology created at $ENRICHED_FILE"
echo ""

# Step 3: Check Java installation
echo "Step 3: Checking Java..."
if command -v java &> /dev/null; then
    JAVA_VERSION=$(java -version 2>&1 | head -n 1)
    echo "✅ Java found: $JAVA_VERSION"
else
    echo "❌ Java not found. Installing..."
    sudo apt-get update && sudo apt-get install -y openjdk-11-jdk
fi
echo ""

# Step 4: Install Graphviz
echo "Step 4: Checking Graphviz..."
if command -v dot &> /dev/null; then
    echo "✅ Graphviz already installed"
else
    echo "Installing Graphviz..."
    sudo apt-get update && sudo apt-get install -y graphviz
fi
export GRAPHVIZ_DOT=/usr/bin/dot
echo ""

# Step 5: Download SHACL Play CLI (if not exists)
echo "Step 5: Downloading SHACL Play CLI..."
if [ ! -f "shacl-play-cli.jar" ]; then
    wget -q https://github.com/sparna-git/shacl-play/releases/download/0.10.2/shacl-play-app-0.10.2-onejar.jar -O shacl-play-cli.jar
    echo "✅ SHACL Play CLI downloaded"
else
    echo "✅ SHACL Play CLI already exists"
fi
echo ""

# Step 6: Create docs directory if it doesn't exist
mkdir -p docs

# Step 7: Generate Documentation
echo "Step 6: Generating HTML documentation..."
java -jar shacl-play-cli.jar \
    doc \
    -d \
    -i "$ENRICHED_FILE" \
    -l en \
    -o docs/index.html
echo "✅ Documentation generated at docs/index.html"
echo ""

# Step 8: Generate Ontology Diagram
echo "Step 7: Generating ontology diagram..."
java -jar shacl-play-cli.jar \
    draw \
    -i "$ENRICHED_FILE" \
    -o docs/ontology.svg
echo "✅ Ontology diagram generated at docs/ontology.svg"
echo ""

echo "=== ✅ Documentation workflow completed successfully! ==="
echo ""
echo "Generated files:"
echo "  - docs/index.html (Open in browser to view)"
echo "  - docs/ontology.svg"
echo ""
echo "To view the documentation:"
echo "  xdg-open docs/index.html"
