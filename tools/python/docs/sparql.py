from pathlib import Path

from rdflib import Graph, Namespace

# Define SHACL namespace
SH = Namespace("http://www.w3.org/ns/shacl#")


def enrich_ontology(ontology_path: Path, output_path: Path) -> None:
    """Enrich the ontology by materialising anonymous sh:node shapes."""
    g = Graph()
    g.parse(ontology_path, format="turtle")

    to_replace = []
    for s, p, o in g.triples((None, SH.node, None)):
        to_replace.append((s, p, o))

    for s, p, o in to_replace:
        g.remove((s, p, o))
        g.add((s, SH.term("notanode"), o))

    insert_query = """
PREFIX sh: <http://www.w3.org/ns/shacl#>
INSERT {
  ?parentShape sh:node ?newNodeShape .
  ?newNodeShape a sh:NodeShape .
  ?newNodeShape sh:property ?innerPropertyShape .
  ?innerPropertyShape ?p ?o .
}
WHERE {
  ?parentShape sh:notanode ?anonShape .
  ?anonShape sh:property ?innerPropertyShape .
  ?innerPropertyShape sh:hasValue ?val ;
                      ?p ?o .
  FILTER(isIRI(?val))
  FILTER(isBlank(?anonShape))
  FILTER(isBlank(?innerPropertyShape))
  BIND(IRI(CONCAT(STR(?val), "Shape")) AS ?newNodeShape)
}
"""
    g.update(insert_query)

    delete_query = """
PREFIX sh: <http://www.w3.org/ns/shacl#>
DELETE {
  ?s sh:notanode ?something .
}
WHERE {
  ?s sh:notanode ?something .
}
"""
    g.update(delete_query)

    ttl_data = g.serialize(format="turtle")
    output_path.write_text(ttl_data)
    print("Ontology enriched with new node shapes.")
    print(ttl_data)
    print(f"Enriched ontology saved to: {output_path}")


if __name__ == "__main__":
    repo_root = Path(__file__).resolve().parent.parent.parent.parent
    ontology_file = repo_root / "ontology-combined.ttl"
    output_file = repo_root / "ontology-enriched.ttl"
    enrich_ontology(ontology_file, output_file)
