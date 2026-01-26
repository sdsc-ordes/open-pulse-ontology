from flask import Flask, request, jsonify
from rdflib import Graph

app = Flask(__name__)

# Disk-backed RDF Graph using SQLAlchemy (SQLite)
# Make sure: pip install rdflib rdflib-sqlalchemy flask setuptools
graph = Graph("SQLAlchemy")
graph.open("sqlite:///rdfstore.sqlite", create=True)


@app.route("/sparql", methods=["GET", "POST"])
def sparql_endpoint():
    query = request.args.get("query") or request.form.get("query")
    update = request.form.get("update")

    try:
        if query:  # SELECT / ASK
            result = graph.query(query)
            vars = result.vars
            output = []
            for row in result:
                obj = {str(var): str(value) for var, value in zip(vars, row)}
                output.append(obj)
            return jsonify(output)
        elif update:  # INSERT / DELETE / UPDATE
            graph.update(update)
            return "Update successful", 200
        else:
            return "No query or update provided", 400
    except Exception as e:
        return str(e), 500


@app.route("/upload", methods=["POST"])
def upload_ttl():
    """Upload TTL file into the graph"""
    ttl_file = request.files.get("file")
    if not ttl_file:
        return "No file uploaded", 400

    try:
        # Direct parse (SQLAlchemy backend will handle disk storage)
        graph.parse(ttl_file, format="turtle")
        return f"Loaded {len(graph)} triples", 200
    except Exception as e:
        return f"Error parsing file: {e}", 500


if __name__ == "__main__":
    app.run(debug=True, port=3030)
