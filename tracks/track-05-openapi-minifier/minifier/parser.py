from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import json
import yaml

HTTP_METHODS = {"get", "put", "post", "delete", "options", "head", "patch", "trace"}
REF = "$ref"

@dataclass
class OperationRef:
    path: str
    method: str
    operation_id: Optional[str]
    summary: Optional[str]
    tags: List[str]

def _load_yaml_or_json(text: str) -> Dict[str, Any]:
    """Try JSON first; if that fails, load YAML (supporting multi-doc streams)."""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    docs = list(yaml.safe_load_all(text))
    # Return the last mapping document (common in multi-doc YAML)
    for node in reversed(docs):
        if isinstance(node, dict):
            return node
    return docs[0] if docs else {}

class OpenAPIParser:
    """OpenAPI/Swagger parser for loading and navigating specs."""
    def __init__(self, doc: Dict[str, Any] = {}):
        self.doc = doc
        self.version = self._detect_version()

    # ---------- Construction ----------
    @staticmethod
    def load_spec(path: str) -> "OpenAPIParser":
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        data = _load_yaml_or_json(text)
        return OpenAPIParser(data)

    def _detect_version(self) -> str:
        if isinstance(self.doc, dict):
            if "openapi" in self.doc:
                return str(self.doc["openapi"])  # e.g., "3.0.3" or "3.1.0"
            if self.doc.get("swagger") == "2.0":
                return "2.0"
        return "unknown"

    # ---------- Top-level accessors ----------
    def servers(self) -> List[Dict[str, Any]]:
        """Return normalized servers (Swagger 2.0 synthesized)."""
        if self.version == "2.0":
            host = self.doc.get("host", "") or ""
            base = self.doc.get("basePath", "") or ""
            schemes = self.doc.get("schemes", ["http"]) or ["http"]
            return [{"url": f"{scheme}://{host}{base}"} for scheme in schemes]
        return self.doc.get("servers", []) or []

    def paths(self) -> Dict[str, Any]:
        return self.doc.get("paths", {}) or {}

    def components(self) -> Dict[str, Any]:
        """Return an OAS-3-like components dict (maps Swagger 2.0 fields when needed)."""
        if self.version == "2.0":
            return {
                "schemas": self.doc.get("definitions", {}) or {},
                "parameters": self.doc.get("parameters", {}) or {},
                "responses": self.doc.get("responses", {}) or {},
                "securitySchemes": self.doc.get("securityDefinitions", {}) or {},
            }
        return self.doc.get("components", {}) or {}

    # ---------- Listings ----------
    def list_operations(self) -> List[OperationRef]:
        ops: List[OperationRef] = []
        for path, item in self.paths().items():
            if not isinstance(item, dict):
                continue
            for method, op in item.items():
                if method.lower() not in HTTP_METHODS or not isinstance(op, dict):
                    continue
                ops.append(OperationRef(
                    path=path,
                    method=method.lower(),
                    operation_id=op.get("operationId"),
                    summary=op.get("summary"),
                    tags=list(op.get("tags", []) or []),
                ))
        return ops

    def list_schemas(self) -> Dict[str, Dict[str, Any]]:
        return dict(self.components().get("schemas", {}) or {})

    def list_security_schemes(self) -> Dict[str, Any]:
        return dict(self.components().get("securitySchemes", {}) or {})

    # ---------- Per-operation schema refs ----------
    def op_request_body_schema_refs(self, op_node: Dict[str, Any]) -> List[str]:
        """Return list of $ref strings used in an operation's request body."""
        refs: List[str] = []
        if self.version == "2.0":
            for p in op_node.get("parameters", []) or []:
                if isinstance(p, dict) and p.get("in") == "body":
                    schema = p.get("schema")
                    if isinstance(schema, dict) and REF in schema and isinstance(schema[REF], str):
                        refs.append(schema[REF])
        else:
            rb = op_node.get("requestBody")
            if isinstance(rb, dict):
                for media in (rb.get("content") or {}).values():
                    schema = (media or {}).get("schema")
                    if isinstance(schema, dict) and REF in schema and isinstance(schema[REF], str):
                        refs.append(schema[REF])
        return refs

    def op_response_schema_refs(self, op_node: Dict[str, Any]) -> List[str]:
        """Return list of $ref strings used across an operation's responses."""
        refs: List[str] = []
        resps = op_node.get("responses", {}) or {}
        for resp in resps.values():
            if not isinstance(resp, dict):
                continue
            if self.version == "2.0":
                schema = resp.get("schema")
                if isinstance(schema, dict) and REF in schema and isinstance(schema[REF], str):
                    refs.append(schema[REF])
            else:
                for media in (resp.get("content") or {}).values():
                    schema = (media or {}).get("schema")
                    if isinstance(schema, dict) and REF in schema and isinstance(schema[REF], str):
                        refs.append(schema[REF])
        return refs

# ---------- Minimal usage example ----------
if __name__ == "__main__":
    parser = OpenAPIParser()
    spec = parser.load_spec("../examples/complex-spec.yaml")

    print("Version:", spec.version)
    print("Servers:", spec.servers())

    print("\nOperations:")
    for op in spec.list_operations():
        print(f"  {op.method.upper():6} {op.path:40}  id={op.operation_id!s:20}  tags={op.tags}")

    print("\nSchemas:")
    for name in spec.list_schemas().keys():
        print("  -", name)

    print("\nSecurity Schemes:")
    for name in spec.list_security_schemes().keys():
        print("  -", name)

    # Show request/response refs for the first operation (demo)
    ops = spec.list_operations()
    if ops:
        first = ops[0]
        op_node = spec.paths()[first.path][first.method]
        print(f"\nFirst operation: {first.method.upper()} {first.path}")
        print("  Request body $refs:", spec.op_request_body_schema_refs(op_node))
        print("  Response $refs:", spec.op_response_schema_refs(op_node))