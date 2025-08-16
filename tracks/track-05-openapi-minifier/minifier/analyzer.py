from __future__ import annotations
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple, Union
import re
import difflib

# package-safe import (works as package and flat files)
try:
    from .parser import OpenAPIParser
except Exception:  # pragma: no cover
    from parser import OpenAPIParser  # type: ignore

SpecLike = Union[OpenAPIParser, Dict[str, Any]]
HTTP_METHODS = {"get","put","post","delete","options","head","patch","trace"}

class DependencyAnalyzer:
    """
    1) Operation selection from user input (opId / METHOD:/path or METHOD /path / fuzzy)
    2) Calculate required schema names via transitive $ref traversal
    """

    # ---------- public API ----------
    def select_operations(self, spec: SpecLike, operation_requests: List[str]) -> List[Dict[str, Any]]:
        """Return a list of operations matching the user queries."""
        doc = self._doc(spec)
        paths = (doc.get("paths") or {})
        flat_ops: List[Dict[str, Any]] = []

        # Flatten all operations
        for p, item in paths.items():
            if not isinstance(item, dict):
                continue
            for m, node in item.items():
                ml = m.lower()
                if ml not in HTTP_METHODS or not isinstance(node, dict):
                    continue
                flat_ops.append({
                    "path": p,
                    "method": ml,
                    "operationId": node.get("operationId"),
                    "summary": node.get("summary"),
                    "description": node.get("description"),
                    "tags": node.get("tags") or [],
                    "node": node,
                })

        def by_operation_id(q: str) -> List[Dict[str, Any]]:
            ql = q.lower()
            exact = [op for op in flat_ops if (op["operationId"] or "").lower() == ql]
            if exact:
                return exact
            return [op for op in flat_ops if ql and ql in (op["operationId"] or "").lower()]

        def by_method_and_path(q: str) -> List[Dict[str, Any]]:
            # supports "POST:/path" or "POST /path"
            m = re.match(r"^\s*([A-Za-z]+)\s*[:\s]\s*(\S+)\s*$", q)
            if not m:
                # accept bare paths (return all methods)
                qp = q.strip()
                return [op for op in flat_ops if op["path"] == qp]
            method, path = m.group(1).lower(), m.group(2)
            return [op for op in flat_ops if op["method"] == method and op["path"] == path]

        def fuzzy_search(q: str, top_k: int = 5) -> List[Dict[str, Any]]:
            ql = q.lower()
            scored: List[Tuple[float, Dict[str, Any]]] = []
            for op in flat_ops:
                hay = " ".join([
                    op["operationId"] or "",
                    op["summary"] or "",
                    op["description"] or "",
                    " ".join(op["tags"]),
                    f"{op['method']} {op['path']}",
                ]).lower()
                ratio = difflib.SequenceMatcher(None, hay, ql).ratio()
                if ratio > 0.25:
                    scored.append((ratio, op))
            scored.sort(key=lambda t: -t[0])
            return [op for _, op in scored[:top_k]]

        candidates: List[Dict[str, Any]] = []
        for req in operation_requests:
            hits = by_operation_id(req) or by_method_and_path(req) or fuzzy_search(req)
            candidates.extend(hits)

        # Deduplicate by (method, path)
        seen: Set[Tuple[str, str]] = set()
        unique: List[Dict[str, Any]] = []
        for op in candidates:
            key = (op["method"], op["path"])
            if key not in seen:
                seen.add(key)
                unique.append(op)
        return unique

    def required_schemas(self, spec: SpecLike, operations: List[Dict[str, Any]]) -> Set[str]:
        """
        Compute the transitive set of schema names required by the given operations.
        Supports OAS3 (#/components/schemas/Name) and Swagger 2.0 (#/definitions/Name).
        """
        doc = self._doc(spec)
        version = self._detect_version(doc)

        if version == "2.0":
            all_schemas: Dict[str, Any] = (doc.get("definitions") or {})
        else:
            all_schemas = ((doc.get("components") or {}).get("schemas") or {})

        required: Set[str] = set()
        queue: List[str] = []

        def ref_to_name(ref: Any) -> Optional[str]:
            if not isinstance(ref, str):
                return None
            if version == "2.0":
                if ref.startswith("#/definitions/"):
                    return ref.split("/")[-1]
            else:
                if ref.startswith("#/components/schemas/"):
                    return ref.split("/")[-1]
            return None

        # seed queue from each operation
        for op in operations:
            node = op.get("node") or {}

            if version == "2.0":
                # parameters (in: body) schemas
                for p in node.get("parameters", []) or []:
                    if isinstance(p, dict) and p.get("in") == "body":
                        sch = p.get("schema")
                        if isinstance(sch, dict) and "$ref" in sch:
                            nm = ref_to_name(sch["$ref"])
                            if nm:
                                queue.append(nm)
                # responses top-level schema
                for r in (node.get("responses") or {}).values():
                    if isinstance(r, dict):
                        sch = r.get("schema")
                        if isinstance(sch, dict) and "$ref" in sch:
                            nm = ref_to_name(sch["$ref"])
                            if nm:
                                queue.append(nm)
            else:
                # requestBody.content.*.schema
                rb = node.get("requestBody")
                if isinstance(rb, dict):
                    for media in (rb.get("content") or {}).values():
                        sch = (media or {}).get("schema")
                        if isinstance(sch, dict) and "$ref" in sch:
                            nm = ref_to_name(sch["$ref"])
                            if nm:
                                queue.append(nm)
                # responses.*.content.*.schema
                for r in (node.get("responses") or {}).values():
                    if isinstance(r, dict):
                        for media in (r.get("content") or {}).values():
                            sch = (media or {}).get("schema")
                            if isinstance(sch, dict) and "$ref" in sch:
                                nm = ref_to_name(sch["$ref"])
                                if nm:
                                    queue.append(nm)
                # parameters.*.schema
                for p in node.get("parameters", []) or []:
                    if isinstance(p, dict):
                        sch = p.get("schema")
                        if isinstance(sch, dict) and "$ref" in sch:
                            nm = ref_to_name(sch["$ref"])
                            if nm:
                                queue.append(nm)

        # traverse schemas transitively
        visited: Set[str] = set()

        def push(nm: Optional[str]) -> None:
            if nm and nm not in visited:
                queue.append(nm)

        def walk_schema(schema: Any) -> None:
            if not isinstance(schema, dict):
                return
            # direct $ref
            nm = ref_to_name(schema.get("$ref"))
            if nm:
                push(nm)
                return
            # compositions
            for key in ("allOf", "oneOf", "anyOf"):
                for sub in schema.get(key, []) or []:
                    if isinstance(sub, dict):
                        walk_schema(sub)
            # properties
            props = schema.get("properties") or {}
            if isinstance(props, dict):
                for sub in props.values():
                    if isinstance(sub, dict):
                        walk_schema(sub)
            # items
            items = schema.get("items")
            if isinstance(items, dict):
                walk_schema(items)
            # additionalProperties
            ap = schema.get("additionalProperties")
            if isinstance(ap, dict):
                walk_schema(ap)

            # discriminator.mapping explicit refs (common in polymorphic models)
            disc = schema.get("discriminator")
            if isinstance(disc, dict):
                mapping = disc.get("mapping") or {}
                if isinstance(mapping, dict):
                    for tref in mapping.values():
                        nm2 = ref_to_name(tref)
                        if nm2:
                            push(nm2)

        while queue:
            name = queue.pop()
            if name in visited:
                continue
            visited.add(name)
            required.add(name)
            node = all_schemas.get(name)
            if isinstance(node, dict):
                walk_schema(node)

        return required

    # ---------- internals ----------
    def _doc(self, spec: SpecLike) -> Dict[str, Any]:
        if hasattr(spec, "doc"):
            spec = spec.doc  # OpenAPIParser instance
        if not isinstance(spec, dict):
            raise TypeError("spec must be a dict or OpenAPIParser")
        return spec

    def _detect_version(self, doc: Dict[str, Any]) -> str:
        if "openapi" in doc:
            return "3.x"
        if doc.get("swagger") == "2.0":
            return "2.0"
        return "3.x"


if __name__ == "__main__":
    parser = OpenAPIParser()
    spec = parser.load_spec("../examples/complex-spec.yaml")
    analyzer = DependencyAnalyzer()

    # ---------- tiny assertion helpers ----------
    def assert_eq(actual, expected, msg):
        if actual != expected:
            print(f"❌ {msg} | actual={actual!r}, expected={expected!r}")
        else:
            print(f"✅ {msg}")

    def assert_true(cond, msg):
        if not cond:
            print(f"❌ {msg}")
        else:
            print(f"✅ {msg}")

    # ---------- operation selection tests ----------
    print("—— Operation selection ——")
    ops = analyzer.select_operations(spec, ["createIssue"])
    assert_true(len(ops) >= 1, "select by operationId finds at least one op")
    if ops:
        assert_eq(ops[0]["path"], "/projects/{projectId}/issues", "op path matches")
        assert_eq(ops[0]["method"], "post", "op method matches")
        assert_eq(ops[0]["operationId"], "createIssue", "operationId matches")

    ops2 = analyzer.select_operations(spec, ["POST:/projects/{projectId}/issues"])
    assert_true(len(ops2) >= 1, "select by 'METHOD:/path' finds an op")
    if ops2:
        assert_eq((ops2[0]["method"], ops2[0]["path"]), ("post", "/projects/{projectId}/issues"),
                  "METHOD:/path selection matches")

    ops3 = analyzer.select_operations(spec, ["POST /projects/{projectId}/issues"])
    assert_true(len(ops3) >= 1, "select by 'METHOD /path' finds an op")
    if ops3:
        assert_eq((ops3[0]["method"], ops3[0]["path"]), ("post", "/projects/{projectId}/issues"),
                  "METHOD /path selection matches")

    ops4 = analyzer.select_operations(spec, ["create a new issue"])
    assert_true(any(op.get("operationId") == "createIssue" for op in ops4),
                "fuzzy search finds 'createIssue' via summary/description")

    ops_dedup = analyzer.select_operations(
        spec,
        ["createIssue", "POST:/projects/{projectId}/issues", "POST /projects/{projectId}/issues"],
    )
    # After dedupe we should still have exactly one op for that method+path
    pairs = {(op["method"], op["path"]) for op in ops_dedup}
    assert_eq(len(pairs), 1, "dedup returns a single unique (method,path)")

    # ---------- schema dependency test ----------
    print("—— Required schema closure ——")
    needed = analyzer.required_schemas(spec, ops or ops2 or ops3)
    # Minimal subset we expect your complex-spec to have (adjust if your example differs)
    expected_subset = {
        "CreateIssueRequest",
        "Issue",
        "User",
    }
    assert_true(expected_subset.issubset(needed),
                f"required_schemas contains at least {sorted(expected_subset)}")
