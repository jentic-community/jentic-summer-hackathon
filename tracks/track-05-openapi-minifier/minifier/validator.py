from __future__ import annotations
from typing import Any, Dict, List, Set, Tuple
import re
try:
    from .parser import OpenAPIParser
except ImportError:  # pragma: no cover
    from parser import OpenAPIParser  # type: ignore


HTTP_METHODS = {"get","put","post","delete","options","head","patch","trace"}

class SpecValidator:
    def __init__(self, strict: bool = True, allow_external_refs: bool = False, use_external: bool = False):
        self.strict = strict
        self.allow_external_refs = allow_external_refs
        self.use_external = use_external

    def validate(self, spec: OpenAPIParser) -> List[str]:
        """
        Validate a spec loaded by OpenAPIParser.
        Returns a list of human-readable error strings (empty list == valid).
        """
        errs: List[str] = []
        doc = spec.doc
        version = spec.version

        # ---- Top-level structure ----
        if not isinstance(doc, dict):
            return ["Spec root must be a mapping/dict."]
        if "openapi" not in doc and "swagger" not in doc:
            errs.append("Missing 'openapi' (3.x) or 'swagger' (2.0) version.")
        info = doc.get("info", {})
        if not (isinstance(info, dict) and info.get("title") and info.get("version")):
            errs.append("Missing required 'info.title' or 'info.version'.")
        paths = spec.paths()
        if not isinstance(paths, dict):
            errs.append("Missing or invalid 'paths'.")

        # ---- Components & security schemes ----
        components = spec.components()
        if not isinstance(components, dict):
            components = {}
        security_schemes = set((components.get("securitySchemes") or {}).keys())

        # ---- Validate each path & operation ----
        seen_op_ids: Set[str] = set()
        for p, item in (paths or {}).items():
            if not isinstance(item, dict):
                errs.append(f"Path item for '{p}' must be an object.")
                continue

            # path template variables
            path_vars = set(re.findall(r"\{([^}/]+)\}", p))
            # path-level params (for dedupe and required checks)
            path_params = [pp for pp in item.get("parameters", []) if isinstance(pp, dict)]
            path_param_keys = {(pp.get("in"), pp.get("name")) for pp in path_params}

            for m, op in item.items():
                ml = m.lower()
                if ml not in HTTP_METHODS:
                    # allow non-operation fields and vendor exts
                    if m not in {"parameters","summary","description"} and not m.startswith("x-"):
                        errs.append(f"Invalid field under path '{p}': '{m}'.")
                    continue

                if not isinstance(op, dict):
                    errs.append(f"Operation '{m} {p}' must be an object.")
                    continue

                # operationId uniqueness (soft error unless strict)
                op_id = op.get("operationId")
                if isinstance(op_id, str):
                    if op_id in seen_op_ids:
                        errs.append(f"Duplicate operationId: {op_id}")
                    seen_op_ids.add(op_id)

                # Merge params to check duplicates & required path params
                op_params = [pp for pp in op.get("parameters", []) if isinstance(pp, dict)]
                op_param_keys = {(pp.get("in"), pp.get("name")) for pp in op_params}

                # Duplicate parameters at the same level
                if len(op_param_keys) != len(op_params):
                    errs.append(f"Duplicate parameters in operation '{m} {p}'.")

                # Required path variables present
                merged_keys = path_param_keys | op_param_keys
                for var in path_vars:
                    if ("path", var) not in merged_keys:
                        errs.append(f"Missing required path parameter '{{{var}}}' in '{m} {p}'.")

                # Path params must be required=True
                for pp in path_params + op_params:
                    if pp.get("in") == "path" and not pp.get("required", False):
                        errs.append(f"Path parameter '{pp.get('name')}' must be required in '{m} {p}'.")

                # Request body sanity (OAS3) / body param (v2)
                if version.startswith("3."):
                    rb = op.get("requestBody")
                    if rb is not None:
                        if not isinstance(rb, dict):
                            errs.append(f"requestBody must be an object in '{m} {p}'.")
                        else:
                            content = rb.get("content")
                            if not isinstance(content, dict) or not content:
                                errs.append(f"requestBody without 'content' in '{m} {p}'.")
                elif version == "2.0":
                    # Swagger 2.0: body is a parameter with in: body
                    for pp in op_params:
                        if pp.get("in") == "body":
                            sch = pp.get("schema")
                            if sch is None:
                                errs.append(f"Body parameter missing 'schema' in '{m} {p}'.")

                # Responses sanity
                resps = op.get("responses")
                if not isinstance(resps, dict) or not resps:
                    errs.append(f"Operation '{m} {p}' must have responses.")
                else:
                    for code, rnode in resps.items():
                        if not (code == "default" or re.match(r"^[1-5][0-9][0-9]$", str(code))):
                            errs.append(f"Invalid response code '{code}' in '{m} {p}'.")
                        if isinstance(rnode, dict) and "description" not in rnode:
                            errs.append(f"Response '{code}' in '{m} {p}' missing 'description'.")

                # Security: reference only defined schemes
                for req in op.get("security") or []:
                    if isinstance(req, dict):
                        for sname in req.keys():
                            if sname not in security_schemes:
                                errs.append(f"Security scheme '{sname}' not defined (in {m} {p}).")

        # ---- $ref integrity (internal graph) ----
        errs += self._check_internal_refs(doc)

        # ---- Discriminator checks ----
        errs += self._check_discriminators(doc)

        # ---- Optional external validator ----
        if self.use_external:
            errs += self._external_validate(doc)

        # Downgrade some messages to warnings if not strict
        if not self.strict:
            errs = [e for e in errs if not e.startswith("Duplicate operationId")]

        return errs

    # -------- Helpers --------
    def _iter_refs(self, node: Any) -> List[str]:
        out: List[str] = []
        if isinstance(node, dict):
            if "$ref" in node and isinstance(node["$ref"], str):
                out.append(node["$ref"])
            for k, v in node.items():
                if k == "$ref":
                    continue
                out.extend(self._iter_refs(v))
        elif isinstance(node, list):
            for it in node:
                out.extend(self._iter_refs(it))
        return out

    def _resolve_internal_ref(self, root: Dict[str, Any], ref: str) -> Any:
        assert ref.startswith("#/")
        cur: Any = root
        for part in ref[2:].split("/"):
            if part == "":
                continue
            cur = cur[part]
        return cur

    def _check_internal_refs(self, root: Dict[str, Any]) -> List[str]:
        e: List[str] = []
        for ref in self._iter_refs(root):
            if not isinstance(ref, str):
                continue
            if ref.startswith("#/"):
                try:
                    _ = self._resolve_internal_ref(root, ref)
                except Exception:
                    e.append(f"Unresolved $ref: {ref}")
            else:
                if not self.allow_external_refs:
                    e.append(f"External $ref not allowed: {ref}")
        return e

    def _check_discriminators(self, root: Dict[str, Any]) -> List[str]:
        e: List[str] = []
        comps = (root.get("components") or {})
        schemas = (comps.get("schemas") or {})
        for name, node in schemas.items():
            if not isinstance(node, dict):
                continue
            disc = node.get("discriminator")
            if not isinstance(disc, dict):
                continue
            prop = disc.get("propertyName")
            if not isinstance(prop, str) or not prop:
                e.append(f"Schema '{name}' discriminator missing 'propertyName'.")
                continue
            if not self._property_maybe_present(node, prop):
                e.append(f"Schema '{name}' discriminator property '{prop}' not found in schema properties.")
            mapping = disc.get("mapping") or {}
            if isinstance(mapping, dict):
                for _, tref in mapping.items():
                    if isinstance(tref, str) and tref.startswith("#/"):
                        try:
                            self._resolve_internal_ref(root, tref)
                        except Exception:
                            e.append(f"Discriminator mapping target not found: {tref} (in schema '{name}').")
        return e

    def _property_maybe_present(self, schema: Dict[str, Any], prop: str) -> bool:
        if "properties" in schema and isinstance(schema["properties"], dict) and prop in schema["properties"]:
            return True
        for key in ("allOf","oneOf","anyOf"):
            for sub in schema.get(key, []) or []:
                if isinstance(sub, dict) and self._property_maybe_present(sub, prop):
                    return True
        return False
