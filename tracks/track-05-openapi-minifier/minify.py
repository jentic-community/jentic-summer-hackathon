from __future__ import annotations
import argparse, sys, yaml
from typing import List

# Package-safe imports (works both as package and as flat files)
try:
    from minifier.spec_minifier import OpenAPIMinifier, MinificationConfig, create_minifier
except Exception:  # fallback if run alongside the modules
    from spec_minifier import OpenAPIMinifier, MinificationConfig, create_minifier  # type: ignore


def _parse_ops_arg(csv: str) -> List[str]:
    """
    Accepts a single comma-separated string (your original UX).
    Each item can be:
      - operationId           e.g., createIssue
      - METHOD:/path          e.g., POST:/rest/api/3/issue
      - METHOD /path          e.g., POST /rest/api/3/issue
      - free text             e.g., create a new issue
    """
    if not csv:
        return []
    return [x.strip() for x in csv.split(",") if x.strip()]


def build_argparser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Minify an OpenAPI/Swagger spec for selected operations.")
    p.add_argument("--input", required=True, help="Path to OpenAPI YAML/JSON file.")
    p.add_argument("--ops", required=True, help="Comma-separated selectors, e.g. 'GET:/things,POST:/things' or 'createIssue'.")
    p.add_argument("--output", required=True, help="Where to write the minified spec (YAML or JSON by extension).")

    # Optional toggles mapped to MinificationConfig
    p.add_argument("--no-descriptions", action="store_true",
                   help="Drop descriptions/summaries to shrink output.")
    p.add_argument("--examples", action="store_true",
                   help="Keep examples (default: off).")
    p.add_argument("--no-strict", action="store_true",
                   help="Allow validation warnings without failing.")

    return p

def main() -> None:
    args = build_argparser().parse_args()

    ops = _parse_ops_arg(args.ops)
    if not ops:
        print("❌ No operations specified via --ops", file=sys.stderr)
        sys.exit(2)

    # Decide output format from file extension
    out_lower = args.output.lower()
    output_format = "json" if out_lower.endswith(".json") else "yaml"

    config = MinificationConfig(
        include_descriptions=not args.no_descriptions,
        include_examples=args.examples,
        strict_validation=not args.no_strict,
        output_format=output_format,
    )

    # Create and run the minifier
    minifier = create_minifier(config) if 'create_minifier' in globals() else OpenAPIMinifier(config)
    result = minifier.minify_file(args.input, ops, output_path=args.output)

    if not result.success:
        print("❌ Minification failed.", file=sys.stderr)
        if result.errors:
            print("Errors:", file=sys.stderr)
            for e in result.errors:
                print(" -", e, file=sys.stderr)
        sys.exit(1)

    # Success summary
    print(f"✅ Wrote minified spec to {args.output}")
    if result.reduction_percentage:
        print(f"   {result.size_reduction}")
    if result.operations_included:
        print("   Included ops:")
        for op in result.operations_included:
            print("   -", op)
    if result.schemas_included:
        print(f"   Schemas kept: {len(result.schemas_included)}")

if __name__ == "__main__":
    main()