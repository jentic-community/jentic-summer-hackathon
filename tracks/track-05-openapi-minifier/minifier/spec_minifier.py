"""
OpenAPI Spec Minifier Module
Main implementation for extracting minimal OpenAPI specifications.
"""

from typing import Dict, Any, List, Optional, Set, Union
from dataclasses import dataclass
from pathlib import Path
import logging

from .parser import OpenAPIParser
from .dependency_analyzer import AdvancedDependencyAnalyzer

logger = logging.getLogger(__name__)


@dataclass
class MinificationConfig:
    """Configuration for minification process."""
    include_descriptions: bool = True
    include_examples: bool = True
    strip_unused_schemas: bool = True
    preserve_security: bool = True
    # Phase 2 optimizations
    optimize_allof_oneof: bool = True
    strip_unused_properties: bool = False  # Conservative default
    build_dependency_graph: bool = True
    detect_circular_refs: bool = True


@dataclass
class MinificationResult:
    """Result of a minification operation."""
    success: bool
    spec: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    errors: Optional[List[str]] = None  # Phase 3: Multiple errors
    metrics: Optional[Dict[str, Any]] = None
    # Phase 2 enhancements
    dependency_analysis: Optional[Dict[str, Any]] = None
    optimization_report: Optional[Dict[str, Any]] = None
    circular_dependencies: Optional[List[List[str]]] = None
    # Phase 3 enhancements
    validation_errors: Optional[List[str]] = None
    reduction_percentage: Optional[float] = None
    completeness_score: Optional[float] = None
    quality_metrics: Optional[Dict[str, Any]] = None


class Analyzer:
    """Component for analyzing OpenAPI specifications."""
    
    def __init__(self, parser: OpenAPIParser):
        self.parser = parser
    
    def find_dependencies(self, operations: List[str]) -> Set[str]:
        """Find all schema dependencies for given operations."""
        return set()  # Basic implementation


class Extractor:
    """Component for extracting minimal specifications."""
    
    def __init__(self, parser: OpenAPIParser):
        self.parser = parser
    
    def build_minimal_spec(self, operations: List[str], dependencies: Set[str]) -> Dict[str, Any]:
        """Build a minimal OpenAPI spec with only required components."""
        return {}  # Basic implementation


class Validator:
    """Component for validating extracted specifications."""
    
    def __init__(self):
        try:
            from openapi_spec_validator import validate_spec
            self.openapi_validator = validate_spec
            self.validation_available = True
        except ImportError:
            self.openapi_validator = None
            self.validation_available = False
    
    def validate_spec(self, spec: Dict[str, Any]) -> List[str]:
        """
        Validate that the generated spec is valid OpenAPI.
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Basic structural validation
        errors.extend(self._validate_basic_structure(spec))
        
        # Advanced OpenAPI validation if available
        if self.validation_available and self.openapi_validator:
            try:
                self.openapi_validator(spec)
            except Exception as e:
                errors.append(f"OpenAPI validation error: {str(e)}")
        
        return errors
    
    def _validate_basic_structure(self, spec: Dict[str, Any]) -> List[str]:
        """Validate basic OpenAPI structure."""
        errors = []
        
        # Required fields
        if 'openapi' not in spec:
            errors.append("Missing required field 'openapi'")
        elif not isinstance(spec['openapi'], str):
            errors.append("Field 'openapi' must be a string")
        
        if 'info' not in spec:
            errors.append("Missing required field 'info'")
        elif not isinstance(spec['info'], dict):
            errors.append("Field 'info' must be an object")
        else:
            info = spec['info']
            if 'title' not in info:
                errors.append("Missing required field 'info.title'")
            if 'version' not in info:
                errors.append("Missing required field 'info.version'")
        
        if 'paths' not in spec:
            errors.append("Missing required field 'paths'")
        elif not isinstance(spec['paths'], dict):
            errors.append("Field 'paths' must be an object")
        
        # Validate paths structure
        if 'paths' in spec and isinstance(spec['paths'], dict):
            for path, path_item in spec['paths'].items():
                if not isinstance(path_item, dict):
                    errors.append(f"Path '{path}' must be an object")
                    continue
                
                for method, operation in path_item.items():
                    if method.lower() in ['get', 'post', 'put', 'delete', 'patch', 'head', 'options', 'trace']:
                        if not isinstance(operation, dict):
                            errors.append(f"Operation '{method.upper()} {path}' must be an object")
                        elif 'responses' not in operation:
                            errors.append(f"Operation '{method.upper()} {path}' missing required 'responses'")
        
        # Validate components if present
        if 'components' in spec:
            components = spec['components']
            if 'schemas' in components:
                for schema_name, schema_def in components['schemas'].items():
                    if not isinstance(schema_def, dict):
                        errors.append(f"Schema '{schema_name}' must be an object")
        
        return errors
    
    def validate_references(self, spec: Dict[str, Any]) -> List[str]:
        """Validate that all $ref references resolve correctly."""
        errors = []
        
        def check_refs(obj, path=""):
            if isinstance(obj, dict):
                if '$ref' in obj:
                    ref_path = obj['$ref']
                    if not self._resolve_reference(spec, ref_path):
                        errors.append(f"Unresolved reference '{ref_path}' at {path}")
                else:
                    for key, value in obj.items():
                        check_refs(value, f"{path}.{key}" if path else key)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    check_refs(item, f"{path}[{i}]" if path else f"[{i}]")
        
        check_refs(spec)
        return errors
    
    def _resolve_reference(self, spec: Dict[str, Any], ref_path: str) -> bool:
        """Check if a reference path can be resolved in the spec."""
        if not ref_path.startswith('#/'):
            return False  # External references not supported
        
        parts = ref_path[2:].split('/')
        current = spec
        
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return False
        
        return True


class OpenAPIMinifier:
    """Main class for minifying OpenAPI specifications."""
    
    def __init__(self, config: Optional[MinificationConfig] = None):
        """Initialize the minifier with optional configuration."""
        self.config = config or MinificationConfig()
        self.parser = OpenAPIParser()
        self.analyzer = Analyzer(self.parser)
        self.extractor = Extractor(self.parser)
        self.validator = Validator()
        # Phase 2: Advanced dependency analyzer
        self.dependency_analyzer = AdvancedDependencyAnalyzer(self.parser)
        self._configure_dependency_analyzer()
    
    def _configure_dependency_analyzer(self):
        """Configure the dependency analyzer based on minification config."""
        optimization_config = {
            'remove_descriptions': not self.config.include_descriptions,
            'remove_examples': not self.config.include_examples,
            'strip_unused_properties': self.config.strip_unused_properties,
            'optimize_allof_oneof': self.config.optimize_allof_oneof,
            'preserve_required_fields': True
        }
        self.dependency_analyzer.set_optimization_config(optimization_config)
    
    def minify_file(self, spec_path: Union[str, Path], operations: List[str]) -> MinificationResult:
        """
        Minify an OpenAPI specification file.
        
        Args:
            spec_path: Path to the OpenAPI specification file
            operations: List of operation identifiers to include
            
        Returns:
            MinificationResult with success status and minified spec
        """
        try:
            spec_path = Path(spec_path)
            
            # Check if file exists
            if not spec_path.exists():
                return MinificationResult(
                    success=False,
                    error=f"File not found: {spec_path}"
                )
            
            # Load and minify the spec
            minified_spec = self.minify(str(spec_path), operations)
            
            # Calculate metrics
            metrics = {
                'original_operations': len(self.parser.get_operations()),
                'minified_operations': len(operations),
                'original_schemas': len(self.parser.get_schemas()),
                'size_reduction': 0.8  # Placeholder
            }
            
            return MinificationResult(
                success=True,
                spec=minified_spec,
                metrics=metrics
            )
            
        except Exception as e:
            return MinificationResult(
                success=False,
                error=str(e)
            )
    
    def minify(self, spec_path: str, operations: List[str]) -> Dict[str, Any]:
        """
        Main minification logic - extracts minimal spec for specified operations.
        
        Args:
            spec_path: Path to the OpenAPI specification file
            operations: List of operation identifiers to include
            
        Returns:
            Minified OpenAPI specification
        """
        # Load the original spec
        original_spec = self.parser.load(spec_path)
        
        # For now, return a basic minified spec structure
        # This will be expanded in later phases
        minified_spec = {
            'openapi': original_spec.get('openapi'),
            'info': original_spec.get('info'),
            'servers': original_spec.get('servers', []),
            'paths': {},
            'components': {
                'schemas': {}
            }
        }
        
        return minified_spec
    
    def find_operations(self, spec: Dict[str, Any], operations: List[str]) -> List[Dict[str, Any]]:
        """
        Find operations by different selection methods.
        
        Args:
            spec: The OpenAPI specification dictionary
            operations: List of operation identifiers (can be operation IDs, 
                       path+method strings, or description search terms)
            
        Returns:
            List of found operation dictionaries
        """
        # Store original spec and temporarily use the provided spec
        original_spec = self.parser.spec
        self.parser.spec = spec
        
        try:
            if not self.parser.spec:
                return []
            
            found_operations = []
            
            for op_identifier in operations:
                # Try different selection methods
                op = None
                
                # Method 1: Try by operation ID
                op = self.parser.get_operation_by_id(op_identifier)
                if op:
                    found_operations.append(op)
                    continue
                
                # Method 2: Try by path + method (format: "METHOD /path")
                if ' ' in op_identifier:
                    parts = op_identifier.split(' ', 1)
                    if len(parts) == 2:
                        method, path = parts
                        op = self.parser.get_operations_by_path_method(path, method)
                        if op:
                            found_operations.append(op)
                            continue
                
                # Method 3: Try by description search
                matching_ops = self.parser.find_operations_by_description(op_identifier)
                if matching_ops:
                    found_operations.extend(matching_ops)
            
            # Remove duplicates while preserving order
            seen = set()
            unique_operations = []
            for op in found_operations:
                op_key = (op['path'], op['method'])
                if op_key not in seen:
                    seen.add(op_key)
                    unique_operations.append(op)
            
            return unique_operations
        
        finally:
            # Restore original spec
            self.parser.spec = original_spec
    
    def calculate_dependencies(self, spec: Dict[str, Any], operations: List[Dict[str, Any]]) -> Set[str]:
        """
        Calculate all schema dependencies for the given operations.
        
        Args:
            spec: The loaded OpenAPI specification
            operations: List of operation dictionaries
            
        Returns:
            Set of required schema names (not full paths)
        """
        # Store original spec and temporarily use the provided spec
        original_spec = self.parser.spec
        self.parser.spec = spec
        
        try:
            # Phase 2: Use advanced dependency analyzer if configured
            if self.config.build_dependency_graph:
                return self._calculate_dependencies_with_graph(spec, operations)
            else:
                # Fall back to Phase 1 method
                return self._calculate_dependencies_basic(operations)
        
        finally:
            # Restore original spec
            self.parser.spec = original_spec
    
    def _calculate_dependencies_with_graph(self, spec: Dict[str, Any], operations: List[Dict[str, Any]]) -> Set[str]:
        """Calculate dependencies using the advanced graph-based analyzer."""
        # Build complete dependency graph
        self.dependency_analyzer.build_complete_dependency_graph(spec)
        
        # Extract initial schema references from operations
        all_refs = set()
        for operation in operations:
            operation_refs = self._extract_operation_schemas(operation)
            all_refs.update(operation_refs)
        
        # Use graph-based resolution
        resolved_refs, analysis = self.dependency_analyzer.resolve_dependencies_with_graph(all_refs)
        
        # Store analysis results for reporting
        self._last_dependency_analysis = analysis
        
        # Convert to schema names
        schema_names = set()
        for ref in resolved_refs:
            if ref.startswith('#/components/schemas/'):
                schema_name = ref.split('/')[-1]
                schema_names.add(schema_name)
        
        return schema_names
    
    def _calculate_dependencies_basic(self, operations: List[Dict[str, Any]]) -> Set[str]:
        """Basic dependency calculation (Phase 1 method)."""
        all_refs = set()
        
        for operation in operations:
            # Extract schemas from this operation
            operation_refs = self._extract_operation_schemas(operation)
            all_refs.update(operation_refs)
        
        # Now recursively resolve all schema dependencies
        resolved_refs = self._resolve_schema_dependencies(all_refs)
        
        # Convert full reference paths to schema names
        schema_names = set()
        for ref in resolved_refs:
            if ref.startswith('#/components/schemas/'):
                schema_name = ref.split('/')[-1]
                schema_names.add(schema_name)
        
        return schema_names
    
    def _extract_operation_schemas(self, operation: Dict[str, Any]) -> Set[str]:
        """
        Extract all schema references from a single operation.
        
        Args:
            operation: Operation dictionary
            
        Returns:
            Set of schema references found in this operation
        """
        refs = set()
        op_details = operation.get('operation', {})
        
        # 1. Extract request body schemas
        request_body = op_details.get('requestBody', {})
        if request_body:
            content = request_body.get('content', {})
            for media_type, schema_info in content.items():
                schema = schema_info.get('schema', {})
                schema_refs = self.parser.get_schema_references(schema)
                refs.update(schema_refs)
        
        # 2. Extract response schemas
        responses = op_details.get('responses', {})
        for status_code, response in responses.items():
            content = response.get('content', {})
            for media_type, schema_info in content.items():
                schema = schema_info.get('schema', {})
                schema_refs = self.parser.get_schema_references(schema)
                refs.update(schema_refs)
        
        # 3. Extract parameter schemas
        parameters = op_details.get('parameters', [])
        for param in parameters:
            if isinstance(param, dict):
                schema = param.get('schema', {})
                if schema:
                    schema_refs = self.parser.get_schema_references(schema)
                    refs.update(schema_refs)
        
        return refs
    
    def _resolve_schema_dependencies(self, initial_refs: Set[str]) -> Set[str]:
        """
        Recursively resolve all schema dependencies.
        
        Args:
            initial_refs: Set of initial schema references
            
        Returns:
            Set of all required schema references (including nested dependencies)
        """
        all_refs = set(initial_refs)
        refs_to_process = set(initial_refs)
        
        while refs_to_process:
            current_ref = refs_to_process.pop()
            
            # Resolve the current reference to get the actual schema
            schema = self.parser.resolve_schema_reference(current_ref)
            if schema:
                # Find all references within this schema
                nested_refs = self.parser.get_schema_references(schema)
                
                # Add any new references we haven't seen yet
                new_refs = nested_refs - all_refs
                all_refs.update(new_refs)
                refs_to_process.update(new_refs)
        
        return all_refs
    
    def analyze_dependencies(self, spec: Dict[str, Any], operations: List[str]) -> Set[str]:
        """
        Find all required schemas and components for the specified operations.
        
        Args:
            spec: The loaded OpenAPI specification
            operations: List of operation identifiers
            
        Returns:
            Set of required schema references
        """
        # Find the actual operations first
        found_operations = self.find_operations(spec, operations)
        
        # Then calculate dependencies
        return self.calculate_dependencies(spec, found_operations)
    
    def validate_output(self, spec: Dict[str, Any]) -> List[str]:
        """
        Validate that the output specification is valid OpenAPI.
        
        Args:
            spec: The OpenAPI specification to validate
            
        Returns:
            List of validation errors (empty if valid)
        """
        all_errors = []
        
        # Basic structure validation
        structure_errors = self.validator.validate_spec(spec)
        all_errors.extend(structure_errors)
        
        # Reference validation
        reference_errors = self.validator.validate_references(spec)
        all_errors.extend(reference_errors)
        
        return all_errors
    
    def minify_spec(self, spec: Dict[str, Any], operations: List[str]) -> MinificationResult:
        """
        Complete minification with validation and quality metrics.
        
        Args:
            spec: The OpenAPI specification to minify
            operations: List of operation identifiers to include
            
        Returns:
            MinificationResult with comprehensive information
        """
        try:
            # Store original spec
            original_spec = self.parser.spec
            self.parser.spec = spec
            
            # Find operations
            found_operations = self.find_operations(spec, operations)
            if not found_operations:
                return MinificationResult(
                    success=False,
                    error="No operations found",
                    errors=["No operations found for the given identifiers"]
                )
            
            # Calculate dependencies
            dependencies = self.calculate_dependencies(spec, found_operations)
            
            # Build minimal spec
            minimal_spec = self.build_minimal_spec(spec, found_operations, dependencies)
            
            # Validate output
            validation_errors = self.validate_output(minimal_spec)
            
            # Calculate quality metrics
            quality_metrics = self._calculate_quality_metrics(spec, minimal_spec, found_operations, dependencies)
            
            # Get dependency analysis
            dependency_analysis = self.get_dependency_analysis()
            
            return MinificationResult(
                success=len(validation_errors) == 0,
                spec=minimal_spec,
                errors=validation_errors if validation_errors else None,
                validation_errors=validation_errors,
                reduction_percentage=quality_metrics['size_reduction_percentage'],
                completeness_score=quality_metrics['completeness_score'],
                quality_metrics=quality_metrics,
                dependency_analysis=dependency_analysis,
                metrics={
                    'original_operations': len(self.parser.get_operations()),
                    'minified_operations': len(found_operations),
                    'original_schemas': len(self.parser.get_schemas()),
                    'minified_schemas': len(dependencies)
                }
            )
            
        except Exception as e:
            return MinificationResult(
                success=False,
                error=str(e),
                errors=[str(e)]
            )
        
        finally:
            # Restore original spec
            self.parser.spec = original_spec
    
    def _calculate_quality_metrics(self, original_spec: Dict[str, Any], minimal_spec: Dict[str, Any], 
                                 operations: List[Dict[str, Any]], dependencies: Set[str]) -> Dict[str, Any]:
        """Calculate comprehensive quality metrics."""
        
        # Size reduction metrics
        original_operations = len(original_spec.get('paths', {}))
        original_schemas = len(original_spec.get('components', {}).get('schemas', {}))
        
        minified_operations = len(minimal_spec.get('paths', {}))
        minified_schemas = len(minimal_spec.get('components', {}).get('schemas', {}))
        
        # Calculate reduction percentages
        operation_reduction = ((original_operations - minified_operations) / max(original_operations, 1)) * 100
        schema_reduction = ((original_schemas - minified_schemas) / max(original_schemas, 1)) * 100
        overall_reduction = (operation_reduction + schema_reduction) / 2
        
        # Completeness score (how well we preserved functionality)
        requested_operations = len(operations)
        found_operations = minified_operations
        completeness = (found_operations / max(requested_operations, 1)) * 100
        
        # Estimate spec size (rough)
        import json
        original_size = len(json.dumps(original_spec, separators=(',', ':')))
        minimal_size = len(json.dumps(minimal_spec, separators=(',', ':')))
        size_reduction = ((original_size - minimal_size) / max(original_size, 1)) * 100
        
        return {
            'size_reduction_percentage': round(overall_reduction, 2),
            'operation_reduction_percentage': round(operation_reduction, 2),
            'schema_reduction_percentage': round(schema_reduction, 2),
            'byte_size_reduction_percentage': round(size_reduction, 2),
            'completeness_score': round(min(completeness, 100), 2),
            'original_operations': original_operations,
            'minified_operations': minified_operations,
            'original_schemas': original_schemas,
            'minified_schemas': minified_schemas,
            'original_size_bytes': original_size,
            'minified_size_bytes': minimal_size,
            'requested_operations': requested_operations,
            'found_operations': found_operations
        }
    
    def get_dependency_analysis(self) -> Optional[Dict[str, Any]]:
        """Get the latest dependency analysis results."""
        return getattr(self, '_last_dependency_analysis', None)
    
    def get_optimization_opportunities(self, spec: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get optimization opportunities for the given spec."""
        # Store original spec and temporarily use the provided spec
        original_spec = self.parser.spec
        self.parser.spec = spec
        
        try:
            self.dependency_analyzer.build_complete_dependency_graph(spec)
            all_schemas = set(f"#/components/schemas/{name}" for name in spec.get('components', {}).get('schemas', {}).keys())
            return self.dependency_analyzer._identify_optimization_opportunities(all_schemas)
        
        finally:
            # Restore original spec
            self.parser.spec = original_spec
    
    def build_minimal_spec(self, spec: Dict[str, Any], operations: List[Dict[str, Any]], dependencies: Set[str]) -> Dict[str, Any]:
        """Build a minimal OpenAPI spec with optimizations."""
        # Store original spec and temporarily use the provided spec
        original_spec = self.parser.spec
        self.parser.spec = spec
        
        try:
            # Start with basic structure
            minimal_spec = {
                'openapi': spec.get('openapi'),
                'info': spec.get('info'),
                'servers': spec.get('servers', []) if self.config.preserve_security else [],
                'paths': self._extract_operation_paths(operations),
                'components': {
                    'schemas': self._extract_and_optimize_schemas(spec, dependencies),
                    'securitySchemes': spec.get('components', {}).get('securitySchemes', {}) if self.config.preserve_security else {}
                }
            }
            
            # Add security if present and configured to preserve
            if self.config.preserve_security and 'security' in spec:
                minimal_spec['security'] = spec['security']
            
            return minimal_spec
        
        finally:
            # Restore original spec
            self.parser.spec = original_spec
    
    def _extract_operation_paths(self, operations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract path definitions for selected operations."""
        paths = {}
        for operation in operations:
            path = operation['path']
            method = operation['method'].lower()
            
            if path not in paths:
                paths[path] = {}
            
            # Get the full operation definition from the original spec
            original_path_item = self.parser.spec['paths'][path]
            paths[path][method] = original_path_item[method]
        
        return paths
    
    def _extract_and_optimize_schemas(self, spec: Dict[str, Any], dependencies: Set[str]) -> Dict[str, Any]:
        """Extract and optimize schema definitions."""
        all_schemas = spec.get('components', {}).get('schemas', {})
        
        # Get only the schemas we need
        needed_schemas = {name: all_schemas[name] for name in dependencies if name in all_schemas}
        
        # Apply optimizations if configured
        if any([self.config.optimize_allof_oneof, not self.config.include_descriptions, not self.config.include_examples]):
            needed_schemas = self.dependency_analyzer.optimize_schema_definitions(needed_schemas)
        
        return needed_schemas


def create_minifier(config: Optional[MinificationConfig] = None) -> OpenAPIMinifier:
    """Factory function to create a configured minifier instance."""
    return OpenAPIMinifier(config)