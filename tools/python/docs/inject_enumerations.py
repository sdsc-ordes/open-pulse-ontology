#!/usr/bin/env python3
"""
Inject enumeration lists into the SHACL Play generated HTML documentation.
This script parses the ontology to extract enumeration values and injects them
into the generated HTML documentation.
"""

from rdflib import Graph, Namespace, RDF
from bs4 import BeautifulSoup
import sys

# Define namespaces
PULSE = Namespace("https://open-pulse.epfl.ch/ontology#")
SCHEMA = Namespace("http://schema.org/")
WD = Namespace("http://www.wikidata.org/entity/")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")


def extract_enumerations(ttl_file):
    """Extract enumeration classes and their values from the ontology."""
    g = Graph()
    g.parse(ttl_file, format="turtle")

    enumerations = {}

    # Find enumeration classes
    enum_classes = [
        PULSE.DisciplineEnumeration,
        PULSE.RepositoryTypeEnumeration,
        PULSE.OrganizationTypeEnumeration,
    ]

    for enum_class in enum_classes:
        values = []

        # Find all instances of this enumeration
        for s in g.subjects(RDF.type, enum_class):
            label = g.value(s, SKOS.prefLabel)
            comment = g.value(s, SKOS.definition)

            # Get the local name or use full URI
            if hasattr(s, "fragment"):
                name = s.fragment or str(s).split("/")[-1]
            else:
                name = str(s).split("#")[-1] if "#" in str(s) else str(s).split("/")[-1]

            values.append(
                {
                    "uri": str(s),
                    "name": name,
                    "label": str(label) if label else name,
                    "comment": str(comment) if comment else None,
                }
            )

        if values:
            # Get enum class info
            enum_label = g.value(enum_class, SKOS.prefLabel)
            enum_comment = g.value(enum_class, SKOS.definition)

            enumerations[str(enum_class)] = {
                "label": str(enum_label) if enum_label else enum_class.split("#")[-1],
                "comment": str(enum_comment) if enum_comment else None,
                "values": sorted(values, key=lambda x: x["label"]),
            }

    return enumerations


def generate_enumeration_html(enumerations):
    """Generate HTML for enumeration sections."""
    html_parts = []

    html_parts.append("""
    <section id="enumerations">
        <h2>Enumerations</h2>
        <p>The following enumerations define controlled vocabularies used in the ontology.</p>
    """)

    for enum_uri, enum_data in enumerations.items():
        enum_id = enum_uri.split("#")[-1] if "#" in enum_uri else enum_uri.split("/")[-1]

        html_parts.append(f"""
        <section id="enum-values-{enum_id}" class="enumeration">
            <h3>{enum_data['label']}</h3>
        """)

        if enum_data["comment"]:
            html_parts.append(f'<p class="comment">{enum_data["comment"]}</p>')

        html_parts.append('<table class="enum-values">')
        html_parts.append(
            "<thead><tr><th>Value</th><th>Label</th><th>Description</th></tr></thead>"
        )
        html_parts.append("<tbody>")

        for value in enum_data["values"]:
            comment = value["comment"] if value["comment"] else ""
            html_parts.append(f"""
            <tr>
                <td><code><a href="{value['uri']}" target="_blank">{value['uri']}</a></code></td>
                <td>{value['label']}</td>
                <td>{comment}</td>
            </tr>
            """)

        html_parts.append("</tbody></table>")
        html_parts.append("</section>")

    html_parts.append("</section>")

    return "\n".join(html_parts)


def is_inside_svg(element):
    """Check if an element is inside an SVG element."""
    for parent in element.parents:
        if parent.name == "svg":
            return True
    return False


def inject_references_to_enum_classes(soup, enumerations):
    """Add references to enumeration value tables in their class sections."""
    for enum_uri, enum_data in enumerations.items():
        enum_id = enum_uri.split("#")[-1] if "#" in enum_uri else enum_uri.split("/")[-1]

        # Try to find the section for this enumeration class
        # Look for headings or sections that contain the class name
        possible_selectors = [
            f"#{enum_id}",
            f'[id*="{enum_id}"]',
            f'section:has(h3:contains("{enum_data["label"]}"))',
            f'h3:contains("{enum_data["label"]}")',
        ]

        target_element = None
        for selector in possible_selectors:
            try:
                # BeautifulSoup doesn't support :contains, so we'll search manually
                if "contains" in selector:
                    for elem in soup.find_all(["h2", "h3", "h4"]):
                        if elem.get_text() and enum_data["label"] in elem.get_text():
                            # Skip elements inside SVG
                            if not is_inside_svg(elem):
                                target_element = elem
                                break
                else:
                    candidate = soup.select_one(selector)
                    # Skip elements inside SVG
                    if candidate and not is_inside_svg(candidate):
                        target_element = candidate

                if target_element:
                    break
            except Exception as e:
                print(f"Warning: Failed to process selector '{selector}': {e}")
                continue

        if target_element:
            # Create a reference note
            reference = soup.new_tag("div", **{"class": "enum-reference"})
            reference.string = "See enumeration values in the "
            link = soup.new_tag("a", href=f"#enum-values-{enum_id}")
            link.string = "Enumerations section"
            reference.append(link)

            # Insert after the heading or at the start of the section
            if target_element.name in ["h2", "h3", "h4"]:
                # Insert after the heading
                target_element.insert_after(reference)
            else:
                # Insert at the start of the section
                target_element.insert(0, reference)


def inject_into_html(html_file, enumeration_html, enumerations):
    """Inject enumeration HTML into the generated documentation."""
    with open(html_file, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    # Find the main content area (adjust selector based on SHACL Play's structure)
    # Try to find the container after the main content sections
    main_content = soup.find("div", class_="container") or soup.find("main") or soup.find("body")

    if main_content:
        # Create a new div for enumerations
        enum_section = BeautifulSoup(enumeration_html, "html.parser")

        # Add some CSS for styling
        style_tag = soup.new_tag("style")
        style_tag.string = """
        #enumerations {
            margin-top: 2rem;
            border-top: 2px solid #ccc;
            padding-top: 2rem;
        }
        .enumeration {
            margin-bottom: 2rem;
        }
        .enum-values {
            width: 100%;
            border-collapse: collapse;
            margin-top: 1rem;
        }
        .enum-values th,
        .enum-values td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        .enum-values th {
            background-color: #f2f2f2;
            font-weight: bold;
        }
        .enum-values tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        .enum-values code {
            background-color: #f4f4f4;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: monospace;
            font-size: 0.85em;
        }
        .enum-values code a {
            color: #0066cc;
            text-decoration: none;
            word-break: break-all;
        }
        .enum-values code a:hover {
            text-decoration: underline;
        }
        .comment {
            font-style: italic;
            color: #666;
        }
        .enum-reference {
            margin: 0.5rem 0 1rem 0;
            padding: 0.5rem;
            background-color: #e8f4f8;
            border-left: 4px solid #0066cc;
            font-size: 0.95em;
        }
        .enum-reference a {
            color: #0066cc;
            font-weight: bold;
            text-decoration: none;
        }
        .enum-reference a:hover {
            text-decoration: underline;
        }
        """

        # Add style to head
        head = soup.find("head")
        if head:
            head.append(style_tag)

        # Append enumeration section to main content
        main_content.append(enum_section)

    # Add references to enumeration classes
    inject_references_to_enum_classes(soup, enumerations)

    # Replace all occurrences of schema1 with schema
    html_content = str(soup)
    html_content = html_content.replace("schema1:", "schema:")
    html_content = html_content.replace("schema1", "schema")

    # Write back
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_content)


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <ontology.ttl> <index.html>")
        sys.exit(1)

    ttl_file = sys.argv[1]
    html_file = sys.argv[2]

    print(f"Extracting enumerations from {ttl_file}...")
    enumerations = extract_enumerations(ttl_file)

    print(f"Found {len(enumerations)} enumeration classes:")
    for enum_uri, enum_data in enumerations.items():
        print(f"  - {enum_data['label']}: {len(enum_data['values'])} values")

    print("\nGenerating HTML for enumerations...")
    enumeration_html = generate_enumeration_html(enumerations)

    print(f"Injecting into {html_file}...")
    inject_into_html(html_file, enumeration_html, enumerations)

    print("Done!")


if __name__ == "__main__":
    main()
