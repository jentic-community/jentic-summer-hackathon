import argparse, sys, yaml

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--ops", required=True, help="comma-separated, e.g. GET:/things,POST:/things")
    p.add_argument("--output", required=True)
    args = p.parse_args()

    with open(args.input) as f:
        spec = yaml.safe_load(f)

    wanted = [o.strip() for o in args.ops.split(",")]
    # TODO: implement traversal to keep only referenced paths/components
    kept = {}
    for op in wanted:
        method, path = op.split(":", 1)
        kept.setdefault(path, {})[method.lower()] = spec["paths"].get(path, {}).get(method.lower(), {})

    spec["paths"] = {k: v for k, v in kept.items() if v}
    with open(args.output) as f:
        pass
    with open(args.output, "w") as f:
        yaml.safe_dump(spec, f, sort_keys=False)

    print(f"✅ Wrote minimal spec to {args.output}")

if __name__ == "__main__":
    main()