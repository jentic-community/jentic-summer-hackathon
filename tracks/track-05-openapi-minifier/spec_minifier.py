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
from .parser import OpenAPIParser
from .analyzer import DependencyAnalyzer
from .extractor import SchemaExtractor
from .validator import SpecValidator

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
        
        # TODO: Initialize your components
        # You'll implement these classes in separate files
        self.parser = None  # TODO: OpenAPIParser()
        self.analyzer = None  # TODO: DependencyAnalyzer()
        self.extractor = None  # TODO: SchemaExtractor()
        self.validator = None  # TODO: SpecValidator()
        
        logger.info("OpenAPI Minifier initialized")
    
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
        # TODO: Implement file-based minification
        # This should:
        # 1. Load the input specification
        # 2. Call minify_spec() to do the actual work
        # 3. Save the result if output_path is provided
        # 4. Return a MinificationResult
        
        result = MinificationResult()
        
        try:
            # TODO: Load input spec
            # spec = self.parser.load_spec(input_path)
            
            # TODO: Perform minification
            # result = self.minify_spec(spec, operations)
            
            # TODO: Save output if path provided
            # if output_path and result.success:
            #     self._save_spec(result.minified_spec, output_path)
            
            pass  # Replace with your implementation
            
        except Exception as e:
            result.success = False
            result.errors.append(f"Minification failed: {str(e)}")
            logger.error(f"Minification error: {e}")
        
        return result
    
    def minify_spec(self, spec: Dict[str, Any], operations: List[str]) -> MinificationResult:
        """
        Minify an OpenAPI specification dictionary.
        
        Args:
            spec: OpenAPI specification as dictionary
            operations: List of operations to include
        
        Returns:
            MinificationResult with minified specification
        """
        result = MinificationResult()
        
        try:
            # TODO: Implement the core minification logic
            # This is the heart of your implementation
            
            # Step 1: Validate input specification
            # TODO: Use self.validator to check input spec
            
            # Step 2: Find requested operations
            # TODO: Use self.analyzer to find operations matching the request
            
            # Step 3: Analyze dependencies
            # TODO: Build dependency graph of all required schemas
            
            # Step 4: Extract minimal specification
            # TODO: Use self.extractor to build minimal spec
            
            # Step 5: Validate output
            # TODO: Ensure output spec is valid
            
            # Step 6: Calculate metrics
            # TODO: Compute size reduction and other metrics
            
            # Placeholder implementation - replace with your logic
            result.success = False
            result.errors.append("minify_spec() not implemented yet")
            
        except Exception as e:
            result.success = False
            result.errors.append(f"Specification minification failed: {str(e)}")
            logger.error(f"Minification error: {e}")
        
        return result
    
    def analyze_operations(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze all operations in a specification.
        
        Args:
            spec: OpenAPI specification
        
        Returns:
            Analysis results with operation details
        """
        # TODO: Implement operation analysis
        # This should return information about:
        # - All available operations
        # - Their dependencies
        # - Complexity metrics
        # - Usage patterns
        
        analysis = {
            'total_operations': 0,
            'operations_by_tag': {},
            'operations_by_path': {},
            'complex_operations': [],
            'schema_usage': {}
        }
        
        # TODO: Fill in the analysis
        # Hint: Iterate through spec['paths'] and analyze each operation
        
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
        # TODO: Implement operation finding logic
        # This should handle different types of requests:
        # - Operation IDs: "createIssue"
        # - Path + method: "POST /rest/api/3/issue"
        # - Description search: "create a new issue"
        
        matching_operations = []
        
        # TODO: Search through spec['paths'] for matches
        # Consider fuzzy matching for description searches
        
        return matching_operations
    
    def calculate_dependencies(self, spec: Dict[str, Any], operations: List[Dict[str, Any]]) -> Set[str]:
        """
        Calculate all schema dependencies for given operations.
        
        Args:
            spec: OpenAPI specification
            operations: List of operation objects
        
        Returns:
            Set of schema names that are required
        """
        # TODO: Implement dependency calculation
        # This is a key part of the minifier - you need to:
        # 1. Find all direct schema references in operations
        # 2. Recursively resolve nested schema dependencies  
        # 3. Handle $ref resolution
        # 4. Return complete set of required schemas
        
        required_schemas = set()
        
        # TODO: Analyze each operation for schema dependencies
        # Hint: Look at requestBody, responses, and parameters
        
        return required_schemas
    
    def build_minimal_spec(self, 
                          original_spec: Dict[str, Any], 
                          operations: List[Dict[str, Any]], 
                          required_schemas: Set[str]) -> Dict[str, Any]:
        """
        Build a minimal OpenAPI specification.
        
        Args:
            original_spec: Original OpenAPI specification
            operations: Operations to include
            required_schemas: Schema names to include
        
        Returns:
            Minimal OpenAPI specification
        """
        # TODO: Build the minimal specification
        # Start with basic structure and add only required components
        
        minimal_spec = {
            'openapi': original_spec.get('openapi', '3.0.0'),
            'info': original_spec.get('info', {}),
            'servers': original_spec.get('servers', []),
            'paths': {},
            'components': {
                'schemas': {},
                'securitySchemes': {}
            }
        }
        
        # TODO: Add selected operations to paths
        # TODO: Add required schemas to components
        # TODO: Add necessary security schemes
        # TODO: Apply configuration options (descriptions, examples, etc.)
        
        return minimal_spec
    
    def validate_output(self, spec: Dict[str, Any]) -> List[str]:
        """
        Validate the output specification.
        
        Args:
            spec: Minified OpenAPI specification
        
        Returns:
            List of validation errors (empty if valid)
        """
        # TODO: Implement output validation
        # Use openapi-spec-validator or similar tool
        # Check that all $ref references resolve
        # Verify the spec structure is correct
        
        errors = []
        
        # TODO: Add validation logic
        
        return errors
    
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