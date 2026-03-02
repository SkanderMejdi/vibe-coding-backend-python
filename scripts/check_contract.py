#!/usr/bin/env python3
"""
Check that generated OpenAPI spec is a superset of BFF contract specs.

For each contract in specs/api/*.yml, verifies that the generated openapi.yaml
contains all paths, methods, and response schemas defined in the contract.

Exit codes:
- 0: All contracts satisfied
- 1: Contract violation(s) found

Comparison logic (structural inclusion):
- Every path+method in contract must exist in generated
- Every response status code in contract must exist in generated
- Every field in contract response schema must exist in generated with same type
- Generated may have extra paths, fields, status codes — that's fine
"""

import sys
from pathlib import Path

import yaml


def load_yaml(path: Path) -> dict:
    with open(path) as f:
        return yaml.safe_load(f) or {}


def resolve_ref(ref: str, root: dict) -> dict:
    """Resolve a $ref like '#/components/schemas/Foo' within the root document."""
    if not ref.startswith("#/"):
        return {}
    parts = ref.lstrip("#/").split("/")
    node = root
    for part in parts:
        node = node.get(part, {})
        if not isinstance(node, dict):
            return {}
    return node


def resolve_schema(schema: dict, root: dict) -> dict:
    """Recursively resolve $ref and anyOf (nullable pattern) in a schema."""
    if "$ref" in schema:
        return resolve_schema(resolve_ref(schema["$ref"], root), root)
    # FastAPI nullable pattern: anyOf: [{$ref or type: object}, {type: null}]
    if "anyOf" in schema:
        non_null = [s for s in schema["anyOf"] if s.get("type") != "null"]
        if len(non_null) == 1:
            return resolve_schema(non_null[0], root)
    return schema


def check_schema_subset(
    contract_schema: dict,
    generated_schema: dict,
    contract_root: dict,
    generated_root: dict,
    path: str = "",
) -> list[str]:
    """
    Check that contract_schema is a subset of generated_schema.

    Returns list of error messages (empty = OK).
    """
    errors: list[str] = []

    contract_schema = resolve_schema(contract_schema, contract_root)
    generated_schema = resolve_schema(generated_schema, generated_root)

    # Check type match
    c_type = contract_schema.get("type")
    g_type = generated_schema.get("type")
    if c_type and g_type and c_type != g_type:
        errors.append(f"{path}: type mismatch — contract={c_type}, generated={g_type}")
        return errors

    # Check array items
    if c_type == "array" and "items" in contract_schema:
        if "items" not in generated_schema:
            errors.append(f"{path}: contract expects array items but generated has none")
        else:
            errors.extend(
                check_schema_subset(
                    contract_schema["items"],
                    generated_schema["items"],
                    contract_root,
                    generated_root,
                    path=f"{path}[]",
                )
            )

    # Check object properties
    c_props = contract_schema.get("properties", {})
    g_props = generated_schema.get("properties", {})

    for prop_name, prop_schema in c_props.items():
        if prop_name not in g_props:
            errors.append(f"{path}.{prop_name}: missing in generated schema")
        else:
            errors.extend(
                check_schema_subset(
                    prop_schema,
                    g_props[prop_name],
                    contract_root,
                    generated_root,
                    path=f"{path}.{prop_name}",
                )
            )

    # Check required fields
    c_required = set(contract_schema.get("required", []))
    g_required = set(generated_schema.get("required", []))
    missing_required = c_required - g_required
    if missing_required:
        for field in missing_required:
            errors.append(
                f"{path}.{field}: required in contract but not in generated"
            )

    return errors


def check_contract(contract_path: Path, generated: dict) -> list[str]:
    """Check one contract file against generated OpenAPI. Returns errors."""
    contract = load_yaml(contract_path)
    errors: list[str] = []
    contract_name = contract_path.name

    contract_paths = contract.get("paths", {})
    generated_paths = generated.get("paths", {})

    if not contract_paths:
        errors.append(f"[{contract_name}] No paths defined in contract")
        return errors

    for path_key, methods in contract_paths.items():
        if path_key not in generated_paths:
            errors.append(f"[{contract_name}] Path {path_key} missing in generated")
            continue

        for method, operation in methods.items():
            if not isinstance(operation, dict):
                continue

            if method not in generated_paths[path_key]:
                errors.append(
                    f"[{contract_name}] {method.upper()} {path_key} missing in generated"
                )
                continue

            gen_operation = generated_paths[path_key][method]

            # Check response schemas
            # YAML parses bare 200: as int, but OpenAPI generators use "200" strings
            gen_responses = gen_operation.get("responses", {})
            gen_responses_str = {str(k): v for k, v in gen_responses.items()}
            for status_code, response in operation.get("responses", {}).items():
                sc = str(status_code)
                if sc not in gen_responses_str:
                    errors.append(
                        f"[{contract_name}] {method.upper()} {path_key} "
                        f"response {status_code} missing in generated"
                    )
                    continue

                # Compare response schema
                c_content = response.get("content", {})
                g_content = gen_responses_str[sc].get("content", {})

                for media_type, c_media in c_content.items():
                    if media_type not in g_content:
                        errors.append(
                            f"[{contract_name}] {method.upper()} {path_key} "
                            f"response {status_code} missing content type {media_type}"
                        )
                        continue

                    c_schema = c_media.get("schema", {})
                    g_schema = g_content[media_type].get("schema", {})

                    schema_errors = check_schema_subset(
                        c_schema,
                        g_schema,
                        contract,
                        generated,
                        path=f"{method.upper()} {path_key} [{status_code}]",
                    )
                    errors.extend(
                        f"[{contract_name}] {e}" for e in schema_errors
                    )

    return errors


def main() -> int:
    generated_path = Path("openapi.yaml")
    contracts_dir = Path("specs/api")

    if not generated_path.exists():
        print("ERROR: openapi.yaml not found. Run 'make openapi' first.")
        return 1

    if not contracts_dir.exists():
        print("No specs/api/ directory — nothing to check.")
        return 0

    contract_files = sorted(contracts_dir.glob("*.yml")) + sorted(
        contracts_dir.glob("*.yaml")
    )

    if not contract_files:
        print("No contract files in specs/api/ — nothing to check.")
        return 0

    generated = load_yaml(generated_path)
    all_errors: list[str] = []

    for contract_path in contract_files:
        print(f"Checking {contract_path} ...")
        errors = check_contract(contract_path, generated)
        all_errors.extend(errors)

    if all_errors:
        print(f"\n{len(all_errors)} contract violation(s):\n")
        for error in all_errors:
            print(f"  ✗ {error}")
        print()
        return 1

    print(f"\nAll {len(contract_files)} contract(s) satisfied.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
