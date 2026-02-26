"""
Test runner for SHACL validation test suite.
Validates that 'valid' test files pass (conforms=true) and 'invalid' test files fail (conforms=false).
"""

import sys
from pathlib import Path

from shacl import run_shacl_validation


def validate_test_file(test_file, shapes_file):
    """Run SHACL validation and return (conforms, results_text)"""
    return run_shacl_validation(test_file, shapes_file)


def main():
    # Determine project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent.parent

    shapes_file = project_root / "ontology-combined.ttl"
    example_dir = project_root / "example"

    if not shapes_file.exists():
        print(f"❌ Shapes file not found: {shapes_file}")
        sys.exit(1)

    if not example_dir.exists():
        print(f"❌ Example directory not found: {example_dir}")
        sys.exit(1)

    # Collect test files, based on the file names indicating valid/invalid tests
    valid_tests = sorted(example_dir.glob("test_valid_*.ttl"))
    invalid_tests = sorted(example_dir.glob("test_invalid_*.ttl"))

    print(f"🔍 Found {len(valid_tests)} valid tests and {len(invalid_tests)} invalid tests\n")

    passed = 0
    failed = 0
    errors = []

    print("=" * 70)
    print("VALID TESTS (should pass validation)")
    print("=" * 70)
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
                errors.append(f"{test_name}: Expected to pass but failed validation")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
            failed += 1
            errors.append(f"{test_name}: Exception during validation - {e}")

    print()

    print("=" * 70)
    print("INVALID TESTS (should fail validation)")
    print("=" * 70)
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
                errors.append(f"{test_name}: Expected to fail but passed validation")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
            failed += 1
            errors.append(f"{test_name}: Exception during validation - {e}")

    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total tests: {passed + failed}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")

    if errors:
        print("\n⚠️  Failures:")
        for error in errors:
            print(f"  - {error}")

    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
