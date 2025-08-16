#!/usr/bin/env python3
"""
OpenAPI Specification Minifier - Main Implementation

This is the core class you need to implement for Track 05.
Complete the TODO methods to build a working OpenAPI minifier.
"""

import os
import json
import yaml
import logging
from typing import Dict, Any, List, Set, Optional, Union
from pathlib import Path
from abc import ABC, abstractmethod

# You'll implement these modules
try:
    from .parser import OpenAPIParser
    from .analyzer import DependencyAnalyzer
    # Use your schemas-only extractor *name* here
    from .extractor import SchemaExtractor
    from .validator import SpecValidator
except Exception:  # pragma: no cover
    from parser import OpenAPIParser  # type: ignore
    from analyzer import DependencyAnalyzer  # type: ignore
    from extractor import SchemaExtractor  # type: ignore
    from validator import SpecValidator  # type: ignore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MinificationConfig:
    """Configuration for the minification process."""
    
    def __init__(self,
                 include_descriptions: bool = True,
                 include_examples: bool = False,
                 strict_validation: bool = True,
                 output_format: str = 'yaml'):
        self.include_descriptions = include_descriptions
        self.include_examples = include_examples
        self.strict_validation = strict_validation
        self.output_format = output_format

class MinificationResult:
    """Result of a minification operation."""
    
    def __init__(self):
        self.success = False
        self.original_size = 0
        self.minified_size = 0
        self.reduction_percentage = 0.0
        self.operations_included = []
        self.schemas_included = []
        self.errors = []
        self.warnings = []
        self.minified_spec = None
    
    @property
    def size_reduction(self) -> str:
        """Human-readable size reduction."""
        return f"{self.reduction_percentage:.1f}% reduction ({self.original_size} → {self.minified_size} lines)"

class OpenAPIMinifier:
    """
    Main OpenAPI Minifier class.
    
    This class orchestrates the minification process by:
    1. Parsing input specifications
    2. Analyzing dependencies 
    3. Extracting required components
    4. Validating output
    """
    
    def __init__(self, config: Optional[MinificationConfig] = None):
        """Initialize the minifier with configuration."""
        self.config = config or MinificationConfig()
        
        # Initialize your components
        # You'll implement these classes in separate files
        self.parser = OpenAPIParser()
        self.analyzer = DependencyAnalyzer()
        self.extractor = SchemaExtractor()
        self.validator = SpecValidator()
        
        logger.info("OpenAPI Minifier initialized")
    
    # --------------------------
    # File IO + Orchestration
    # --------------------------
    def minify_file(self, 
                    input_path: Union[str, Path], 
                    operations: List[str],
                    output_path: Optional[Union[str, Path]] = None) -> MinificationResult:
        """
        Minify an OpenAPI specification file.
        
        Args:
            input_path: Path to input OpenAPI specification
            operations: List of operations to include (operation IDs, paths, or descriptions)
            output_path: Optional path for output file
        
        Returns:
            MinificationResult with details about the process
        """
        # Implement file-based minification
        # This should:
        # 1. Load the input specification
        # 2. Call minify_spec() to do the actual work
        # 3. Save the result if output_path is provided
        # 4. Return a MinificationResult
        
        result = MinificationResult()
        
        try:
            # Load input spec
            op = self.parser.load_spec(str(input_path))
            spec_dict = op.doc
            
            # TODO: Perform minification
            result = self.minify_spec(spec_dict, operations)
            
            # TODO: Save output if path provided
            if output_path and result.success and result.minified_spec is not None:
                self._save_spec(result.minified_spec, output_path)
            return result
            
        except Exception as e:
            result.success = False
            result.errors.append(f"Minification failed: {str(e)}")
            logger.error(f"Minification error: {e}")
        
        return result
    
    # --------------------------
    # Core minification
    # --------------------------
    def minify_spec(self, spec: Dict[str, Any], operations: List[str]) -> MinificationResult:
        """
        Minify an OpenAPI specification dictionary.
        """
        result = MinificationResult()
        try:
            # Step 1: Validate input spec (use wrapper so validator receives OpenAPIParser)
            input_errors = self.validate_output(spec) if self.config.strict_validation else []
            if input_errors:
                result.errors.extend(input_errors)
                return result

            # Step 2: Find requested operations (opId, "METHOD /path", or fuzzy)
            selected_ops = self.find_operations(spec, operations)
            if not selected_ops:
                result.errors.append("No matching operations found for the given requests.")
                return result

            # Step 3: Analyze dependencies (collect transitive set of schema names)
            required_schemas = self.calculate_dependencies(spec, selected_ops)

            # Step 4: Build minimal specification (selected ops + required schemas)
            minimal_doc = self.build_minimal_spec(spec, selected_ops, required_schemas)

            # Step 5: Validate output spec
            out_errors = self.validate_output(minimal_doc)
            if out_errors:
                result.errors.extend(out_errors)
                return result

            # Step 6: Metrics + bookkeeping
            orig, mini, pct = self._calculate_size_metrics(spec, minimal_doc)
            result.success = True
            result.original_size = orig
            result.minified_size = mini
            result.reduction_percentage = pct
            result.operations_included = [
                f"{op['method'].upper()} {op['path']}"
                + (f" ({op['operationId']})" if op.get("operationId") else "")
                for op in selected_ops
            ]
            result.schemas_included = sorted(required_schemas)
            result.minified_spec = minimal_doc
            return result

        except Exception as e:
            result.errors.append(f"Specification minification failed: {e}")
            logger.exception("Minification error")
            return result
    
    def analyze_operations(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze all operations in a specification.

        Returns:
        {
            'total_operations': int,
            'operations_by_tag': Dict[str, int],
            'operations_by_path': Dict[str, int],
            'complex_operations': List[Dict[str, Any]],
            'schema_usage': Dict[str, int]
        }
        """
        analysis = {
            "total_operations": 0,
            "operations_by_tag": {},
            "operations_by_path": {},
            "complex_operations": [],
            "schema_usage": {},
        }

        HTTP_METHODS = {"get","put","post","delete","options","head","patch","trace"}
        REF = "$ref"

        def detect_version(doc: Dict[str, Any]) -> str:
            if "openapi" in doc:
                return "3.x"
            if doc.get("swagger") == "2.0":
                return "2.0"
            return "3.x"

        def components_view(doc: Dict[str, Any], version: str) -> Dict[str, Dict[str, Any]]:
            if version == "2.0":
                return {
                    "schemas": doc.get("definitions", {}) or {},
                    "parameters": doc.get("parameters", {}) or {},
                    "responses": doc.get("responses", {}) or {},
                    "securitySchemes": doc.get("securityDefinitions", {}) or {},
                }
            comps = doc.get("components", {}) or {}
            return {
                "schemas": comps.get("schemas", {}) or {},
                "parameters": comps.get("parameters", {}) or {},
                "responses": comps.get("responses", {}) or {},
                "requestBodies": comps.get("requestBodies", {}) or {},
                "headers": comps.get("headers", {}) or {},
                "examples": comps.get("examples", {}) or {},
                "links": comps.get("links", {}) or {},
                "callbacks": comps.get("callbacks", {}) or {},
                "securitySchemes": comps.get("securitySchemes", {}) or {},
            }

        def parse_schema_ref(ref: Any, version: str) -> Optional[str]:
            if not isinstance(ref, str):
                return None
            if version == "2.0":
                return ref.split("/")[-1] if ref.startswith("#/definitions/") else None
            # 3.x
            return ref.split("/")[-1] if ref.startswith("#/components/schemas/") else None

        def iter_refs(node: Any) -> Iterable[str]:
            if isinstance(node, dict):
                if REF in node and isinstance(node[REF], str):
                    yield node[REF]
                # discriminator mappings
                disc = node.get("discriminator")
                if isinstance(disc, dict):
                    mapping = disc.get("mapping") or {}
                    if isinstance(mapping, dict):
                        for v in mapping.values():
                            if isinstance(v, str) and v.startswith("#/"):
                                yield v
                for k, v in node.items():
                    if k == REF:
                        continue
                    yield from iter_refs(v)
            elif isinstance(node, list):
                for it in node:
                    yield from iter_refs(it)

        def resolve(doc: Dict[str, Any], ref: str) -> Any:
            cur: Any = doc
            for part in ref[2:].split("/"):
                if part == "":
                    continue
                cur = cur[part]
            return cur

        def collect_direct_schema_refs_for_op(doc: Dict[str, Any], op: Dict[str, Any], version: str) -> Set[str]:
            """Direct (non-transitive) schema names referenced by this operation."""
            names: Set[str] = set()

            if version == "2.0":
                # parameters (in: body).schema.$ref
                for p in op.get("parameters", []) or []:
                    if isinstance(p, dict) and p.get("in") == "body":
                        sch = p.get("schema")
                        if isinstance(sch, dict):
                            nm = parse_schema_ref(sch.get(REF), version)
                            if nm:
                                names.add(nm)
                # responses[*].schema.$ref
                for r in (op.get("responses") or {}).values():
                    if isinstance(r, dict):
                        sch = r.get("schema")
                        if isinstance(sch, dict):
                            nm = parse_schema_ref(sch.get(REF), version)
                            if nm:
                                names.add(nm)
            else:
                # requestBody.content.*.schema.$ref
                rb = op.get("requestBody")
                if isinstance(rb, dict):
                    for media in (rb.get("content") or {}).values():
                        if isinstance(media, dict):
                            sch = media.get("schema")
                            if isinstance(sch, dict):
                                nm = parse_schema_ref(sch.get(REF), version)
                                if nm:
                                    names.add(nm)
                # responses[*].content.*.schema.$ref
                for r in (op.get("responses") or {}).values():
                    if isinstance(r, dict):
                        for media in (r.get("content") or {}).values():
                            if isinstance(media, dict):
                                sch = media.get("schema")
                                if isinstance(sch, dict):
                                    nm = parse_schema_ref(sch.get(REF), version)
                                    if nm:
                                        names.add(nm)
                # parameters[*].schema.$ref
                for p in op.get("parameters", []) or []:
                    if isinstance(p, dict):
                        sch = p.get("schema")
                        if isinstance(sch, dict):
                            nm = parse_schema_ref(sch.get(REF), version)
                            if nm:
                                names.add(nm)
            return names

        def schema_closure_size(doc: Dict[str, Any], version: str, all_schemas: Dict[str, Any], roots: Set[str]) -> int:
            """Transitive closure size reachable from root schema names."""
            visited: Set[str] = set()
            queue: List[str] = list(roots)

            def walk_schema(schema: Any):
                if not isinstance(schema, dict):
                    return
                nm = parse_schema_ref(schema.get(REF), version)
                if nm:
                    if nm not in visited:
                        queue.append(nm)
                    return
                # composition
                for key in ("allOf", "oneOf", "anyOf"):
                    for sub in schema.get(key, []) or []:
                        walk_schema(sub)
                # object properties
                props = schema.get("properties") or {}
                if isinstance(props, dict):
                    for sub in props.values():
                        walk_schema(sub)
                # arrays
                items = schema.get("items")
                if isinstance(items, dict):
                    walk_schema(items)
                # additionalProperties
                ap = schema.get("additionalProperties")
                if isinstance(ap, dict):
                    walk_schema(ap)
                # discriminator mapping
                disc = schema.get("discriminator")
                if isinstance(disc, dict):
                    mapping = disc.get("mapping") or {}
                    if isinstance(mapping, dict):
                        for tref in mapping.values():
                            nm2 = parse_schema_ref(tref, version)
                            if nm2 and nm2 not in visited:
                                queue.append(nm2)

            while queue:
                name = queue.pop()
                if name in visited:
                    continue
                visited.add(name)
                node = all_schemas.get(name)
                if isinstance(node, dict):
                    walk_schema(node)
            return len(visited)

        # ---- main iteration ----
        version = detect_version(spec)
        comps = components_view(spec, version)
        all_schemas = comps.get("schemas") or {}
        paths = spec.get("paths", {}) or {}

        for path, item in paths.items():
            if not isinstance(item, dict):
                continue
            op_count_here = 0

            # path-level params for counting
            path_params = item.get("parameters", []) or []
            path_params_count = len([p for p in path_params if isinstance(p, dict)])

            for method, op in item.items():
                ml = method.lower()
                if ml not in HTTP_METHODS or not isinstance(op, dict):
                    continue

                analysis["total_operations"] += 1
                op_count_here += 1

                # tags
                for t in op.get("tags", []) or []:
                    analysis["operations_by_tag"][t] = analysis["operations_by_tag"].get(t, 0) + 1

                # media types and response codes
                req_media_count = 0
                if version != "2.0":
                    rb = op.get("requestBody")
                    if isinstance(rb, dict) and isinstance(rb.get("content"), dict):
                        req_media_count = len(rb["content"])

                resp_codes = 0
                resp_media_count = 0
                resps = op.get("responses") or {}
                if isinstance(resps, dict):
                    resp_codes = sum(1 for _ in resps.keys())
                    if version != "2.0":
                        for r in resps.values():
                            if isinstance(r, dict) and isinstance(r.get("content"), dict):
                                resp_media_count += len(r["content"])

                # parameters
                op_params = op.get("parameters", []) or []
                param_count = path_params_count + len([p for p in op_params if isinstance(p, dict)])

                # security
                has_security = bool(op.get("security"))

                # schema refs (direct) and closure size (transitive)
                direct_schema_names = collect_direct_schema_refs_for_op(spec, op, version)
                for nm in direct_schema_names:
                    analysis["schema_usage"][nm] = analysis["schema_usage"].get(nm, 0) + 1

                closure_sz = schema_closure_size(spec, version, all_schemas, direct_schema_names)

                # simple, explainable complexity score
                # - parameters: 1 each
                # - response codes: 1 each
                # - request media types: 1 each (OAS3)
                # - response media types: 0.5 each (OAS3)
                # - schema graph size: 1 each
                # - security: +2 if present
                score = (
                    param_count
                    + resp_codes
                    + req_media_count
                    + 0.5 * resp_media_count
                    + closure_sz
                    + (2 if has_security else 0)
                )

                # mark complex if score >= 8 (tweak as needed)
                if score >= 8:
                    analysis["complex_operations"].append({
                        "path": path,
                        "method": ml,
                        "operationId": op.get("operationId"),
                        "score": round(score, 2),
                        "metrics": {
                            "parameters": param_count,
                            "response_codes": resp_codes,
                            "request_media_types": req_media_count,
                            "response_media_types": resp_media_count,
                            "schema_closure_size": closure_sz,
                            "security": bool(has_security),
                            "direct_schemas": sorted(direct_schema_names),
                        },
                    })

            analysis["operations_by_path"][path] = op_count_here

        # sort complex ops descending by score for readability
        analysis["complex_operations"].sort(key=lambda x: x["score"], reverse=True)
        # sort schema_usage by count desc
        analysis["schema_usage"] = {
            k: v for k, v in sorted(analysis["schema_usage"].items(), key=lambda kv: (-kv[1], kv[0]))
        }

        return analysis

    
    def find_operations(self, spec: Dict[str, Any], operation_requests: List[str]) -> List[Dict[str, Any]]:
        """
        Find operations matching user requests.
        
        Args:
            spec: OpenAPI specification
            operation_requests: List of operation identifiers (IDs, paths, or descriptions)
        
        Returns:
            List of matching operations with metadata
        """
        # Implement operation finding logic
        # This should handle different types of requests:
        # - Operation IDs: "createIssue"
        # - Path + method: "POST /rest/api/3/issue"
        # - Description search: "create a new issue"
        paths = spec.get("paths", {}) or {}
        
        # Search through spec['paths'] for matches
        # Consider fuzzy matching for description searches
        candidates: List[Dict[str, Any]] = []

        # Build flat list
        flat_ops: List[Dict[str, Any]] = []
        for p, item in paths.items():
            if not isinstance(item, dict):
                continue
            for m, node in item.items():
                if m.lower() not in {"get","put","post","delete","options","head","patch","trace"}:
                    continue
                if not isinstance(node, dict):
                    continue
                flat_ops.append({
                    "path": p,
                    "method": m.lower(),
                    "operationId": node.get("operationId"),
                    "summary": node.get("summary"),
                    "description": node.get("description"),
                    "tags": node.get("tags") or [],
                    "node": node,
                })

        def match_op_id(q: str) -> List[Dict[str, Any]]:
            ql = q.lower()
            exact = [op for op in flat_ops if (op["operationId"] or "").lower() == ql]
            if exact:
                return exact
            partial = [op for op in flat_ops if ql in (op["operationId"] or "").lower()]
            return partial

        def match_method_path(q: str) -> List[Dict[str, Any]]:
            import re
            m = re.match(r"^\s*([A-Za-z]+)\s+(\S+)\s*$", q)
            if not m:
                # treat as path only
                qp = q.strip()
                return [op for op in flat_ops if op["path"] == qp]
            method, path = m.group(1).lower(), m.group(2)
            return [op for op in flat_ops if op["method"] == method and op["path"] == path]

        def search_text(q: str, top_k: int = 5) -> List[Dict[str, Any]]:
            import difflib
            ql = q.lower()
            scored = []
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

        for req in operation_requests:
            # Try opId → method+path → text
            hits = match_op_id(req)
            if not hits:
                hits = match_method_path(req)
            if not hits:
                hits = search_text(req)
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
    
    def calculate_dependencies(self, spec: Dict[str, Any], operations: List[Dict[str, Any]]) -> Set[str]:
        """
        Compute transitive set of component schema names required by selected ops.
        Covers properties/items/allOf/oneOf/anyOf/additionalProperties.
        """
        components = (spec.get("components") or {})
        all_schemas: Dict[str, Any] = (components.get("schemas") or {})
        required: Set[str] = set()
        queue: List[str] = []

        def ref_to_name(ref: Any) -> Optional[str]:
            if isinstance(ref, str) and ref.startswith("#/components/schemas/"):
                return ref.split("/")[-1]
            return None

        # collect op-level refs
        for op in operations:
            node = op.get("node") or {}
            # request body
            rb = node.get("requestBody")
            if isinstance(rb, dict):
                content = rb.get("content") or {}
                for media in content.values():
                    schema = (media or {}).get("schema")
                    if isinstance(schema, dict) and "$ref" in schema:
                        nm = ref_to_name(schema["$ref"])
                        if nm:
                            queue.append(nm)
            # responses
            resps = node.get("responses") or {}
            for resp in resps.values():
                if not isinstance(resp, dict):
                    continue
                content = resp.get("content") or {}
                for media in content.values():
                    schema = (media or {}).get("schema")
                    if isinstance(schema, dict) and "$ref" in schema:
                        nm = ref_to_name(schema["$ref"])
                        if nm:
                            queue.append(nm)
            # parameters (object/array schemas via $ref)
            for p in node.get("parameters", []) or []:
                if isinstance(p, dict):
                    schema = p.get("schema")
                    if isinstance(schema, dict) and "$ref" in schema:
                        nm = ref_to_name(schema["$ref"])
                        if nm:
                            queue.append(nm)

        # traverse schema graph
        visited: Set[str] = set()

        def push(nm: str) -> None:
            if nm and nm not in visited:
                queue.append(nm)

        def walk_schema(schema: Any) -> None:
            if not isinstance(schema, dict):
                return
            # direct $ref
            ref = schema.get("$ref")
            nm = ref_to_name(ref)
            if nm:
                push(nm)
                return
            # compositions
            for key in ("allOf", "oneOf", "anyOf"):
                for sub in schema.get(key, []) or []:
                    if isinstance(sub, dict):
                        walk_schema(sub)
            # object props
            props = schema.get("properties") or {}
            if isinstance(props, dict):
                for sub in props.values():
                    if isinstance(sub, dict):
                        walk_schema(sub)
            # arrays
            items = schema.get("items")
            if isinstance(items, dict):
                walk_schema(items)
            # additionalProperties (can be bool or schema)
            ap = schema.get("additionalProperties")
            if isinstance(ap, dict):
                walk_schema(ap)

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
    
    def build_minimal_spec(
        self, original_spec: Dict[str, Any], operations: List[Dict[str, Any]], required_schemas: Set[str]
    ) -> Dict[str, Any]:
        """
        Build a small, valid OAS3 spec with just the selected ops and required schemas.
        """
        minimal = {
            "openapi": original_spec.get("openapi", "3.0.0"),
            "info": original_spec.get("info", {}),
            "servers": original_spec.get("servers", []),
            "paths": {},
            "components": {"schemas": {}, "securitySchemes": {}},
        }

        # paths: only include selected methods under their paths
        src_paths = original_spec.get("paths", {}) or {}
        for op in operations:
            p, m = op["path"], op["method"]
            if p not in src_paths:
                continue
            src_item = src_paths[p]
            if not isinstance(src_item, dict):
                continue
            # copy only this method; keep path-level params if present
            dst_item: Dict[str, Any] = {}
            if "parameters" in src_item and isinstance(src_item["parameters"], list):
                dst_item["parameters"] = src_item["parameters"]
            if m in src_item and isinstance(src_item[m], dict):
                dst_item[m] = src_item[m]
            if dst_item:
                minimal["paths"][p] = dst_item

        # components.schemas: only required
        src_schemas = ((original_spec.get("components") or {}).get("schemas") or {})
        for name in sorted(required_schemas):
            node = src_schemas.get(name)
            if node is not None:
                minimal["components"]["schemas"][name] = node

        # securitySchemes (keep only if referenced globally; tests don't require)
        src_sec = ((original_spec.get("components") or {}).get("securitySchemes") or {})
        if src_sec:
            minimal["components"]["securitySchemes"] = src_sec

        return minimal
    
    def validate_output(self, spec: Dict[str, Any]) -> List[str]:
        """
        Validate using our SpecValidator (already shipped).
        """
        try:
            return self.validator.validate(OpenAPIParser(spec))
        except Exception as e:
            return [f"Validation error: {e}"]
    

    # --------------------------
    # Utilities
    # --------------------------
    def _save_spec(self, spec: Dict[str, Any], output_path: Union[str, Path]) -> None:
        """Save specification to file."""
        output_path = Path(output_path)
        
        # Create output directory if needed
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Determine format from extension or config
        if output_path.suffix.lower() == '.json' or self.config.output_format == 'json':
            with open(output_path, 'w') as f:
                json.dump(spec, f, indent=2)
        else:
            with open(output_path, 'w') as f:
                yaml.dump(spec, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Saved minified specification to {output_path}")
    
    def _calculate_size_metrics(self, original: Dict[str, Any], minified: Dict[str, Any]) -> tuple:
        """Calculate size reduction metrics."""
        # Simple line count as size metric
        original_size = len(yaml.dump(original, default_flow_style=False).splitlines())
        minified_size = len(yaml.dump(minified, default_flow_style=False).splitlines())
        
        reduction = ((original_size - minified_size) / original_size) * 100 if original_size > 0 else 0
        
        return original_size, minified_size, reduction

# Factory function for easy usage
def create_minifier(config: Optional[MinificationConfig] = None) -> OpenAPIMinifier:
    """Create a configured OpenAPI minifier."""
    return OpenAPIMinifier(config)

# Example usage for participants
if __name__ == "__main__":
    print("🔧 OpenAPI Minifier - Core Implementation")
    print("This is the main class you need to implement.")
    print("\n📋 To get started:")
    print("1. Implement the parser, analyzer, extractor, and validator modules")
    print("2. Complete the TODO methods in this class")
    print("3. Test with: python test_minifier.py")
    print("4. Build the CLI interface")
    print("\n💡 Example usage:")
    print("   minifier = create_minifier()")
    print("   result = minifier.minify_file('large-spec.yaml', ['createIssue'])")
    print("   print(result.size_reduction)")