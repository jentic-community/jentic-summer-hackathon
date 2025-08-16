"""
OpenAPI Parser Module
Handles loading and parsing of OpenAPI specifications from YAML/JSON files.
"""

import json
import yaml
from pathlib import Path
from typing import Dict, Any, List, Set, Optional, Union
import logging

logger = logging.getLogger(__name__)


class OpenAPIParser:
    """Parser for OpenAPI specifications that can load and analyze spec files."""
    
    def __init__(self):
        """Initialize the OpenAPI parser."""
        self.spec = None
        self.file_path = None
    
    def load(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Load an OpenAPI specification from a YAML or JSON file.
        
        Args:
            file_path: Path to the OpenAPI specification file
            
        Returns:
            Parsed OpenAPI specification as a dictionary
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file format is unsupported or invalid
        """
        file_path = Path(file_path)
        self.file_path = file_path
        
        if not file_path.exists():
            raise FileNotFoundError(f"OpenAPI spec file not found: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_path.suffix.lower() in ['.yaml', '.yml']:
                    # Handle multi-document YAML files by taking the first document
                    docs = list(yaml.safe_load_all(f))
                    if not docs:
                        raise ValueError("Empty YAML file")
                    self.spec = docs[0]  # Use the first document
                elif file_path.suffix.lower() == '.json':
                    self.spec = json.load(f)
                else:
                    raise ValueError(f"Unsupported file format: {file_path.suffix}")
            
            # Basic validation
            if not isinstance(self.spec, dict):
                raise ValueError("Invalid OpenAPI spec: must be a dictionary")
            
            if 'openapi' not in self.spec:
                raise ValueError("Invalid OpenAPI spec: missing 'openapi' field")
            
            logger.info(f"Successfully loaded OpenAPI spec from {file_path}")
            return self.spec
            
        except yaml.YAMLError as e:
            raise ValueError(f"Failed to parse YAML file: {e}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON file: {e}")
    
    def get_operations(self) -> List[Dict[str, Any]]:
        """
        Extract all operations (path + method combinations) from the loaded spec.
        
        Returns:
            List of operation dictionaries with path, method, and operation details
        """
        if not self.spec:
            raise ValueError("No spec loaded. Call load() first.")
        
        operations = []
        paths = self.spec.get('paths', {})
        
        for path, path_item in paths.items():
            if not isinstance(path_item, dict):
                continue
                
            # HTTP methods that can contain operations
            http_methods = ['get', 'post', 'put', 'delete', 'patch', 'head', 'options', 'trace']
            
            for method in http_methods:
                if method in path_item:
                    operation = path_item[method]
                    if isinstance(operation, dict):
                        operations.append({
                            'path': path,
                            'method': method.upper(),
                            'operationId': operation.get('operationId'),
                            'operation_id': operation.get('operationId'),  # Keep both for compatibility
                            'summary': operation.get('summary'),
                            'description': operation.get('description'),
                            'tags': operation.get('tags', []),
                            'operation': operation
                        })
        
        logger.info(f"Found {len(operations)} operations in the spec")
        return operations
    
    def get_schemas(self) -> Dict[str, Any]:
        """
        Extract all schema definitions from the loaded spec.
        
        Returns:
            Dictionary of schema definitions from components/schemas
        """
        if not self.spec:
            raise ValueError("No spec loaded. Call load() first.")
        
        components = self.spec.get('components', {})
        schemas = components.get('schemas', {})
        
        logger.info(f"Found {len(schemas)} schema definitions in the spec")
        return schemas
    
    def get_operation_by_id(self, operation_id: str) -> Optional[Dict[str, Any]]:
        """
        Find an operation by its operation ID.
        
        Args:
            operation_id: The operationId to search for
            
        Returns:
            Operation dictionary if found, None otherwise
        """
        operations = self.get_operations()
        for op in operations:
            if op['operation_id'] == operation_id:
                return op
        return None
    
    def get_operations_by_path_method(self, path: str, method: str) -> Optional[Dict[str, Any]]:
        """
        Find an operation by its path and HTTP method.
        
        Args:
            path: The path (e.g., "/users/{id}")
            method: The HTTP method (e.g., "GET", "POST")
            
        Returns:
            Operation dictionary if found, None otherwise
        """
        operations = self.get_operations()
        method = method.upper()
        for op in operations:
            if op['path'] == path and op['method'] == method:
                return op
        return None
    
    def find_operations_by_description(self, search_term: str) -> List[Dict[str, Any]]:
        """
        Find operations that match a description search term.
        
        Args:
            search_term: Term to search for in summary/description
            
        Returns:
            List of matching operation dictionaries
        """
        operations = self.get_operations()
        matching_ops = []
        search_term = search_term.lower()
        
        for op in operations:
            summary = (op.get('summary') or '').lower()
            description = (op.get('description') or '').lower()
            
            if search_term in summary or search_term in description:
                matching_ops.append(op)
        
        return matching_ops
    
    def get_schema_references(self, obj: Any, refs: Optional[Set[str]] = None) -> Set[str]:
        """
        Recursively find all $ref references in an object.
        
        Args:
            obj: Object to search for references
            refs: Set to accumulate references (for recursion)
            
        Returns:
            Set of all $ref paths found
        """
        if refs is None:
            refs = set()
        
        if isinstance(obj, dict):
            # Check for $ref
            if '$ref' in obj:
                ref_path = obj['$ref']
                refs.add(ref_path)
            
            # Recursively check all values
            for value in obj.values():
                self.get_schema_references(value, refs)
                
        elif isinstance(obj, list):
            # Recursively check all items
            for item in obj:
                self.get_schema_references(item, refs)
        
        return refs
    
    def resolve_schema_reference(self, ref_path: str) -> Optional[Any]:
        """
        Resolve a $ref path to the actual schema object.
        
        Args:
            ref_path: Reference path (e.g., "#/components/schemas/User")
            
        Returns:
            The referenced schema object, or None if not found
        """
        if not self.spec:
            raise ValueError("No spec loaded. Call load() first.")
        
        # Handle internal references starting with #/
        if ref_path.startswith('#/'):
            path_parts = ref_path[2:].split('/')
            current = self.spec
            
            for part in path_parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    return None
            
            return current
        
        # External references not supported yet
        logger.warning(f"External reference not supported: {ref_path}")
        return None
    
    def get_info(self) -> Dict[str, Any]:
        """Get the info section of the OpenAPI spec."""
        if not self.spec:
            raise ValueError("No spec loaded. Call load() first.")
        return self.spec.get('info', {})
    
    def get_servers(self) -> List[Dict[str, Any]]:
        """Get the servers section of the OpenAPI spec."""
        if not self.spec:
            raise ValueError("No spec loaded. Call load() first.")
        return self.spec.get('servers', [])
    
    def get_security_schemes(self) -> Dict[str, Any]:
        """Get the security schemes from components."""
        if not self.spec:
            raise ValueError("No spec loaded. Call load() first.")
        components = self.spec.get('components', {})
        return components.get('securitySchemes', {})
    
    def get_spec_size_info(self) -> Dict[str, Any]:
        """Get information about the spec size and complexity."""
        if not self.spec:
            raise ValueError("No spec loaded. Call load() first.")
        
        operations = self.get_operations()
        schemas = self.get_schemas()
        
        # Count lines if file was loaded
        lines = 0
        if self.file_path and self.file_path.exists():
            with open(self.file_path, 'r', encoding='utf-8') as f:
                lines = sum(1 for _ in f)
        
        return {
            'total_lines': lines,
            'operation_count': len(operations),
            'schema_count': len(schemas),
            'path_count': len(self.spec.get('paths', {})),
            'file_size_bytes': self.file_path.stat().st_size if self.file_path else 0
        }