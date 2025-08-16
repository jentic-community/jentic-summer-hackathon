# extractor.py
from __future__ import annotations
from typing import Any, Dict, Set, Union
import copy

# Optional: accept your parser instance or raw dict
try:
    from .parser import OpenAPIParser
except ImportError:  # pragma: no cover
    from parser import OpenAPIParser  # type: ignore

try:
    SpecLike = Union[OpenAPIParser, Dict[str, Any]]
except Exception:
    SpecLike = Dict[str, Any]  # fallback for tests without the parser


class SchemaExtractor:
    """
    Schemas-only extractor.
    Given a source spec and a set of schema names, copy only those schema
    definitions (deep-copied) out of the source spec.

    Supports:
      - OpenAPI 3.x: components.schemas
      - Swagger 2.0: definitions
    """

    # ---- public API -----------------------------------------------------
    def extract_schemas_map(self, spec: SpecLike, required: Set[str]) -> Dict[str, Any]:
        """
        Return a {schema_name: schema_object} dict containing only `required`.
        Missing names are silently ignored.
        """
        doc = self._doc(spec)
        version = self._detect_version(doc)

        if version == "2.0":
            src = (doc.get("definitions") or {})
        else:
            src = ((doc.get("components") or {}).get("schemas") or {})

        out: Dict[str, Any] = {}
        for name in sorted(required):
            node = src.get(name)
            if node is not None:
                out[name] = copy.deepcopy(node)
        return out

    def build_components_block(self, spec: SpecLike, required: Set[str]) -> Dict[str, Any]:
        """
        Build just the components/definitions block that includes the selected schemas.
        For OAS3 -> {'components': {'schemas': {...}}}
        For v2   -> {'definitions': {...}}
        """
        doc = self._doc(spec)
        version = self._detect_version(doc)
        schemas_map = self.extract_schemas_map(doc, required)

        if version == "2.0":
            return {"definitions": schemas_map} if schemas_map else {}
        else:
            return {"components": {"schemas": schemas_map}} if schemas_map else {}

    # ---- internals ------------------------------------------------------
    def _doc(self, spec: SpecLike) -> Dict[str, Any]:
        """Normalize the spec to a dict."""
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
        # Default to 3.x shape if uncertain; tests use 3.0.0
        return "3.x"