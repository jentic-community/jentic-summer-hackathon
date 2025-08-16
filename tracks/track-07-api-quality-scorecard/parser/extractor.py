"""Data extraction from OpenAPI specifications into structured models."""

from typing import Dict, Any, List, Optional
import re

from core.models import (
    OpenAPISpec,
    OperationInfo,
    ParameterInfo,
    ResponseInfo,
    SchemaInfo
)
from core.types import HTTPMethod, OpenAPIVersion
from core.exceptions import ParseError


class DataExtractor:
    """Extracts structured data from raw OpenAPI specifications."""
    
    def __init__(self):
        self.http_methods = {method.value for method in HTTPMethod}
    
    def extract(self, raw_spec: Dict[str, Any]) -> OpenAPISpec:
        """Extract structured data from raw OpenAPI specification.
        
        Parameters
        ----------
        raw_spec : Dict[str, Any]
            Raw OpenAPI specification data.
            
        Returns
        -------
        OpenAPISpec
            Structured specification data.
            
        Raises
        ------
        ParseError
            If data extraction fails.
        """
        try:
            version = self._extract_version(raw_spec)
            info = raw_spec.get('info', {})
            
            spec = OpenAPISpec(
                version=version,
                title=info.get('title', 'Untitled API'),
                description=info.get('description'),
                version_info=info.get('version', '1.0.0'),
                servers=raw_spec.get('servers', []),
                tags=raw_spec.get('tags', []),
                security_schemes=self._extract_security_schemes(raw_spec),
                operations=self._extract_operations(raw_spec),
                schemas=self._extract_schemas(raw_spec)
            )
            
            return spec
            
        except Exception as e:
            raise ParseError(f"Failed to extract data from specification: {e}")
    
    def _extract_version(self, raw_spec: Dict[str, Any]) -> OpenAPIVersion:
        """Extract OpenAPI version from specification.
        
        Parameters
        ----------
        raw_spec : Dict[str, Any]
            Raw specification data.
            
        Returns
        -------
        OpenAPIVersion
            Detected OpenAPI version.
        """
        version_str = str(raw_spec.get('openapi', '3.0'))
        if version_str.startswith('3.1'):
            return OpenAPIVersion.V3_1
        else:
            return OpenAPIVersion.V3_0
    
    def _extract_operations(self, raw_spec: Dict[str, Any]) -> List[OperationInfo]:
        """Extract operation information from paths.
        
        Parameters
        ----------
        raw_spec : Dict[str, Any]
            Raw specification data.
            
        Returns
        -------
        List[OperationInfo]
            List of extracted operations.
        """
        operations = []
        paths = raw_spec.get('paths', {})
        
        for path, path_item in paths.items():
            if not isinstance(path_item, dict):
                continue
                
            for method, operation in path_item.items():
                if method.lower() not in self.http_methods:
                    continue
                    
                if not isinstance(operation, dict):
                    continue
                
                op_info = self._extract_operation_info(operation, method, path)
                operations.append(op_info)
        
        return operations
    
    def _extract_operation_info(self, operation: Dict[str, Any], method: str, path: str) -> OperationInfo:
        """Extract information for a single operation.
        
        Parameters
        ----------
        operation : Dict[str, Any]
            Operation object from OpenAPI spec.
        method : str
            HTTP method.
        path : str
            API path.
            
        Returns
        -------
        OperationInfo
            Extracted operation information.
        """
        parameters = self._extract_parameters(operation.get('parameters', []))
        responses = self._extract_responses(operation.get('responses', {}))
        
        return OperationInfo(
            operation_id=operation.get('operationId'),
            method=HTTPMethod(method.lower()),
            path=path,
            summary=operation.get('summary'),
            description=operation.get('description'),
            tags=operation.get('tags', []),
            parameters=parameters,
            responses=responses,
            has_request_body='requestBody' in operation,
            request_body_schema=self._get_request_body_schema(operation.get('requestBody')),
            security_requirements=self._extract_security_requirements(operation.get('security', []))
        )
    
    def _extract_parameters(self, parameters: List[Dict[str, Any]]) -> List[ParameterInfo]:
        """Extract parameter information.
        
        Parameters
        ----------
        parameters : List[Dict[str, Any]]
            List of parameter objects.
            
        Returns
        -------
        List[ParameterInfo]
            List of extracted parameter information.
        """
        param_list = []
        
        for param in parameters:
            if not isinstance(param, dict):
                continue
            
            param_info = ParameterInfo(
                name=param.get('name', ''),
                location=param.get('in', ''),
                type=self._get_parameter_type(param),
                description=param.get('description'),
                required=param.get('required', False),
                has_example='example' in param or 'examples' in param,
                has_constraints=self._has_parameter_constraints(param)
            )
            param_list.append(param_info)
        
        return param_list
    
    def _extract_responses(self, responses: Dict[str, Any]) -> List[ResponseInfo]:
        """Extract response information.
        
        Parameters
        ----------
        responses : Dict[str, Any]
            Responses object from operation.
            
        Returns
        -------
        List[ResponseInfo]
            List of extracted response information.
        """
        response_list = []
        
        for status_code, response in responses.items():
            if not isinstance(response, dict):
                continue
            
            content = response.get('content', {})
            content_types = list(content.keys()) if content else []
            
            response_info = ResponseInfo(
                status_code=str(status_code),
                description=response.get('description'),
                has_schema=self._has_response_schema(response),
                has_example=self._has_response_example(response),
                content_types=content_types
            )
            response_list.append(response_info)
        
        return response_list
    
    def _extract_schemas(self, raw_spec: Dict[str, Any]) -> List[SchemaInfo]:
        """Extract schema information from components.
        
        Parameters
        ----------
        raw_spec : Dict[str, Any]
            Raw specification data.
            
        Returns
        -------
        List[SchemaInfo]
            List of extracted schema information.
        """
        schemas = []
        components = raw_spec.get('components', {})
        schema_defs = components.get('schemas', {})
        
        for name, schema in schema_defs.items():
            if not isinstance(schema, dict):
                continue
            
            schema_info = SchemaInfo(
                name=name,
                type=schema.get('type'),
                properties_count=len(schema.get('properties', {})),
                required_fields=schema.get('required', []),
                has_description='description' in schema,
                has_examples='example' in schema or 'examples' in schema,
                nested_depth=self._calculate_schema_depth(schema)
            )
            schemas.append(schema_info)
        
        return schemas
    
    def _extract_security_schemes(self, raw_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Extract security scheme information.
        
        Parameters
        ----------
        raw_spec : Dict[str, Any]
            Raw specification data.
            
        Returns
        -------
        Dict[str, Any]
            Security schemes data.
        """
        components = raw_spec.get('components', {})
        return components.get('securitySchemes', {})
    
    def _extract_security_requirements(self, security: List[Dict[str, Any]]) -> List[str]:
        """Extract security requirement names.
        
        Parameters
        ----------
        security : List[Dict[str, Any]]
            Security requirements list.
            
        Returns
        -------
        List[str]
            List of security scheme names.
        """
        requirements = []
        for req in security:
            if isinstance(req, dict):
                requirements.extend(req.keys())
        return requirements
    
    def _get_parameter_type(self, param: Dict[str, Any]) -> Optional[str]:
        """Get parameter type from schema or direct type field.
        
        Parameters
        ----------
        param : Dict[str, Any]
            Parameter object.
            
        Returns
        -------
        Optional[str]
            Parameter type if available.
        """
        if 'schema' in param and isinstance(param['schema'], dict):
            return param['schema'].get('type')
        return param.get('type')
    
    def _has_parameter_constraints(self, param: Dict[str, Any]) -> bool:
        """Check if parameter has validation constraints.
        
        Parameters
        ----------
        param : Dict[str, Any]
            Parameter object.
            
        Returns
        -------
        bool
            True if parameter has constraints.
        """
        schema = param.get('schema', param)
        if not isinstance(schema, dict):
            return False
        
        constraint_fields = [
            'minimum', 'maximum', 'minLength', 'maxLength', 
            'pattern', 'enum', 'format', 'minItems', 'maxItems'
        ]
        
        return any(field in schema for field in constraint_fields)
    
    def _has_response_schema(self, response: Dict[str, Any]) -> bool:
        """Check if response has schema definition.
        
        Parameters
        ----------
        response : Dict[str, Any]
            Response object.
            
        Returns
        -------
        bool
            True if response has schema.
        """
        content = response.get('content', {})
        for media_type in content.values():
            if isinstance(media_type, dict) and 'schema' in media_type:
                return True
        return False
    
    def _has_response_example(self, response: Dict[str, Any]) -> bool:
        """Check if response has example data.
        
        Parameters
        ----------
        response : Dict[str, Any]
            Response object.
            
        Returns
        -------
        bool
            True if response has examples.
        """
        content = response.get('content', {})
        for media_type in content.values():
            if isinstance(media_type, dict):
                if 'example' in media_type or 'examples' in media_type:
                    return True
        return False
    
    def _get_request_body_schema(self, request_body: Optional[Dict[str, Any]]) -> Optional[str]:
        """Get request body schema reference or type.
        
        Parameters
        ----------
        request_body : Optional[Dict[str, Any]]
            Request body object.
            
        Returns
        -------
        Optional[str]
            Schema reference or type name.
        """
        if not request_body or not isinstance(request_body, dict):
            return None
        
        content = request_body.get('content', {})
        for media_type in content.values():
            if isinstance(media_type, dict) and 'schema' in media_type:
                schema = media_type['schema']
                if isinstance(schema, dict):
                    if '$ref' in schema:
                        return schema['$ref'].split('/')[-1]
                    elif 'type' in schema:
                        return schema['type']
        
        return None
    
    def _calculate_schema_depth(self, schema: Dict[str, Any], current_depth: int = 0) -> int:
        """Calculate maximum nesting depth of schema.
        
        Parameters
        ----------
        schema : Dict[str, Any]
            Schema object to analyze.
        current_depth : int, optional
            Current nesting depth, by default 0.
            
        Returns
        -------
        int
            Maximum nesting depth.
        """
        if current_depth > 10:
            return current_depth
        
        max_depth = current_depth
        
        if isinstance(schema, dict):
            properties = schema.get('properties', {})
            for prop_schema in properties.values():
                if isinstance(prop_schema, dict):
                    depth = self._calculate_schema_depth(prop_schema, current_depth + 1)
                    max_depth = max(max_depth, depth)
            
            if 'items' in schema and isinstance(schema['items'], dict):
                depth = self._calculate_schema_depth(schema['items'], current_depth + 1)
                max_depth = max(max_depth, depth)
        
        return max_depth