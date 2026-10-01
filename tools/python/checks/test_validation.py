"""
Test runner for SHACL validation test suite.
Validates that 'valid' test files pass (conforms=true) and 'invalid' test files fail (conforms=false).

Runs three variants:
  - canonical:   ontology-combined-canonical.ttl against example/
  - raw:         ontology-combined-raw.ttl against example/raw/
  - provenance:  ontology-combined-provenance.ttl against example/provenance/

The provenance variant only covers the plain-RDF parts of graph:prov (pulse:ExtractionRun).
The RDF-star winner-links (<<s p o>> prov:wasDerivedFrom ...) are NOT covered and can't be
— SHACL cannot target a quoted triple as a focus node (no tool in this repo's stack supports
RDF-star: rdflib can't parse Turtle-star, pySHACL has no quoted-triple support).
"""

import sys
from pathlib import Path

from shacl import run_shacl_validation


def validate_test_file(test_file, shapes_file):
    """Run SHACL validation and return (conforms, results_text)"""
    return run_shacl_validation(test_file, shapes_file)


def run_variant(label, shapes_file, example_dir):
    """Run one (shapes_file, example_dir) variant. Returns (passed, failed, errors)."""
    if not shapes_file.exists():
        print(f"❌ Shapes file not found: {shapes_file}")
        return 0, 1, [f"{label}: shapes file not found: {shapes_file}"]

    if not example_dir.exists():
        print(f"❌ Example directory not found: {example_dir}")
        return 0, 1, [f"{label}: example directory not found: {example_dir}"]

    valid_tests = sorted(example_dir.glob("test_valid_*.ttl"))
    invalid_tests = sorted(example_dir.glob("test_invalid_*.ttl"))

    print("=" * 70)
    print(f"{label.upper()} ({shapes_file.relative_to(shapes_file.parents[2])})")
    print(f"🔍 Found {len(valid_tests)} valid tests and {len(invalid_tests)} invalid tests")
    print("=" * 70)

    passed = 0
    failed = 0
    errors = []

    print("\nVALID TESTS (should pass validation)")
    for test_file in valid_tests:
        test_name = test_file.name
        try:
            conforms, results_text = validate_test_file(test_file, shapes_file)
            if conforms:
                print(f"✅ {test_name}: PASSED (conforms=true)")
                passed += 1
            else:
                print(f"❌ {test_name}: FAILED (expected conforms=true, got conforms=false)")
                print(f"   Validation errors:\n{results_text}")
                failed += 1
                errors.append(f"[{label}] {test_name}: Expected to pass but failed validation")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
            failed += 1
            errors.append(f"[{label}] {test_name}: Exception during validation - {e}")

    print("\nINVALID TESTS (should fail validation)")
    for test_file in invalid_tests:
        test_name = test_file.name
        try:
            conforms, results_text = validate_test_file(test_file, shapes_file)
            if not conforms:
                print(f"✅ {test_name}: PASSED (conforms=false as expected)")
                passed += 1
            else:
                print(f"❌ {test_name}: FAILED (expected conforms=false, got conforms=true)")
                failed += 1
                errors.append(f"[{label}] {test_name}: Expected to fail but passed validation")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
            failed += 1
            errors.append(f"[{label}] {test_name}: Exception during validation - {e}")

    print()
    return passed, failed, errors


def main():
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent.parent
    ontology_dir = project_root / "src" / "ontology"

    variants = [
        ("canonical", ontology_dir / "ontology-combined-canonical.ttl", project_root / "example"),
        ("raw", ontology_dir / "ontology-combined-raw.ttl", project_root / "example" / "raw"),
        ("provenance", ontology_dir / "ontology-combined-provenance.ttl", project_root / "example" / "provenance"),
    ]

    total_passed = 0
    total_failed = 0
    all_errors = []

    for label, shapes_file, example_dir in variants:
        passed, failed, errors = run_variant(label, shapes_file, example_dir)
        total_passed += passed
        total_failed += failed
        all_errors.extend(errors)

    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total tests: {total_passed + total_failed}")
    print(f"✅ Passed: {total_passed}")
    print(f"❌ Failed: {total_failed}")

    if all_errors:
        print("\n⚠️  Failures:")
        for error in all_errors:
            print(f"  - {error}")

    sys.exit(0 if total_failed == 0 else 1)


if __name__ == "__main__":
    main()
