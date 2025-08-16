#!/usr/bin/env python3
"""
Test Suite for OpenAPI Minifier
This test framework validates your implementation.
Run: python test_minifier.py [test_name]
"""
import os
import json
import yaml
import sys
from pathlib import Path
from typing import Dict, Any, List

# Import your implementation
try:
    from minifier.spec_minifier import OpenAPIMinifier, MinificationConfig, create_minifier
    MINIFIER_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Cannot import minifier modules: {e}")
    print("Make sure you've implemented the required modules!")
    MINIFIER_AVAILABLE = False

class MinifierTester:
    """Test framework for the OpenAPI minifier."""
    
    def __init__(self):
        """Initialize tester."""
        self.test_results = []
        self.minifier = None
        
        if MINIFIER_AVAILABLE:
            try:
                self.minifier = create_minifier()
                print("✅ Minifier created successfully")
            except Exception as e:
                print(f"❌ Failed to create minifier: {e}")
    
    def run_test(self, test_name: str, test_func, *args, **kwargs) -> bool:
        """Run a single test and record results."""
        print(f"\n🧪 Running test: {test_name}")
        try:
            result = test_func(*args, **kwargs)
            if result:
                print(f"   ✅ PASS: {test_name}")
                self.test_results.append({'test': test_name, 'status': 'PASS'})
                return True
            else:
                print(f"   ❌ FAIL: {test_name}")
                self.test_results.append({'test': test_name, 'status': 'FAIL'})
                return False
        except NotImplementedError:
            print(f"   🚧 NOT IMPLEMENTED: {test_name}")
            self.test_results.append({'test': test_name, 'status': 'NOT_IMPLEMENTED'})
            return False
        except Exception as e:
            print(f"   💥 ERROR: {test_name} - {str(e)}")
            self.test_results.append({'test': test_name, 'status': 'ERROR', 'error': str(e)})
            return False
    
    def test_minifier_initialization(self) -> bool:
        """Test that minifier initializes correctly."""
        if not MINIFIER_AVAILABLE:
            print("   Minifier modules not available")
            return False
        
        if not self.minifier:
            print("   Minifier not initialized")
            return False
        
        # Check that minifier has required components
        required_attrs = ['config', 'parser', 'analyzer', 'extractor', 'validator']
        for attr in required_attrs:
            if not hasattr(self.minifier, attr):
                print(f"   Missing required attribute: {attr}")
                return False
        
        print("   Minifier initialized with all required components")
        return True
    
    def test_simple_spec_loading(self) -> bool:
        """Test loading a simple OpenAPI specification."""
        # Create a minimal test spec
        test_spec = {
            'openapi': '3.0.0',
            'info': {'title': 'Test API', 'version': '1.0.0'},
            'paths': {
                '/test': {
                    'get': {
                        'operationId': 'getTest',
                        'responses': {
                            '200': {
                                'description': 'Success',
                                'content': {
                                    'application/json': {
                                        'schema': {'type': 'string'}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        
        # Save test spec to file
        test_file = Path('test_simple_spec.yaml')
        try:
            with open(test_file, 'w') as f:
                yaml.dump(test_spec, f)
            
            # Test minification
            result = self.minifier.minify_file(test_file, ['getTest'])
            
            # Clean up
            test_file.unlink()
            
            if not result:
                print("   No result returned from minify_file")
                return False
            
            # Check result structure
            if not hasattr(result, 'success'):
                print("   Result missing 'success' attribute")
                return False
            
            print(f"   Minification result success: {result.success}")
            return True
            
        except Exception as e:
            # Clean up on error
            if test_file.exists():
                test_file.unlink()
            raise e
    
    def test_operation_finding(self) -> bool:
        """Test finding operations by different methods."""
        test_spec = {
            'openapi': '3.0.0',
            'info': {'title': 'Test API', 'version': '1.0.0'},
            'paths': {
                '/users': {
                    'get': {
                        'operationId': 'getUsers',
                        'summary': 'Get all users',
                        'description': 'Retrieve a list of all users'
                    },
                    'post': {
                        'operationId': 'createUser',
                        'summary': 'Create user',
                        'description': 'Create a new user account'
                    }
                },
                '/users/{id}': {
                    'get': {
                        'operationId': 'getUserById',
                        'summary': 'Get user by ID'
                    }
                }
            }
        }
        
        # Test finding operations by operation ID
        operations = self.minifier.find_operations(test_spec, ['createUser'])
        if not operations:
            print("   Failed to find operation by ID")
            return False
        
        if len(operations) != 1:
            print(f"   Expected 1 operation, found {len(operations)}")
            return False
        
        if operations[0].get('operationId') != 'createUser':
            print(f"   Wrong operation found: {operations[0].get('operationId')}")
            return False
        
        # Test finding multiple operations
        operations = self.minifier.find_operations(test_spec, ['getUsers', 'getUserById'])
        if len(operations) != 2:
            print(f"   Expected 2 operations, found {len(operations)}")
            return False
        
        print("   Successfully found operations by ID")
        return True
    
    def test_dependency_resolution(self) -> bool:
        """Test schema dependency resolution."""
        test_spec = {
            'openapi': '3.0.0',
            'info': {'title': 'Test API', 'version': '1.0.0'},
            'paths': {
                '/users': {
                    'post': {
                        'operationId': 'createUser',
                        'requestBody': {
                            'content': {
                                'application/json': {
                                    'schema': {'$ref': '#/components/schemas/User'}
                                }
                            }
                        },
                        'responses': {
                            '200': {
                                'content': {
                                    'application/json': {
                                        'schema': {'$ref': '#/components/schemas/UserResponse'}
                                    }
                                }
                            }
                        }
                    }
                }
            },
            'components': {
                'schemas': {
                    'User': {
                        'type': 'object',
                        'properties': {
                            'name': {'type': 'string'},
                            'profile': {'$ref': '#/components/schemas/Profile'}
                        }
                    },
                    'Profile': {
                        'type': 'object',
                        'properties': {
                            'bio': {'type': 'string'}
                        }
                    },
                    'UserResponse': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'integer'},
                            'user': {'$ref': '#/components/schemas/User'}
                        }
                    },
                    'UnusedSchema': {
                        'type': 'object',
                        'properties': {
                            'unused': {'type': 'string'}
                        }
                    }
                }
            }
        }
        
        # Find the createUser operation
        operations = self.minifier.find_operations(test_spec, ['createUser'])
        if not operations:
            print("   Failed to find createUser operation")
            return False
        
        # Calculate dependencies
        dependencies = self.minifier.calculate_dependencies(test_spec, operations)
        
        # Should include User, Profile, and UserResponse but not UnusedSchema
        expected_schemas = {'User', 'Profile', 'UserResponse'}
        
        if not isinstance(dependencies, set):
            print(f"   Dependencies should be a set, got {type(dependencies)}")
            return False
        
        missing = expected_schemas - dependencies
        if missing:
            print(f"   Missing required schemas: {missing}")
            return False
        
        if 'UnusedSchema' in dependencies:
            print("   Included unused schema (should be excluded)")
            return False
        
        print(f"   Found correct dependencies: {dependencies}")
        return True
    
    def test_minimal_spec_generation(self) -> bool:
        """Test building a minimal specification."""
        test_spec = {
            'openapi': '3.0.0',
            'info': {'title': 'Test API', 'version': '1.0.0'},
            'servers': [{'url': 'https://api.example.com'}],
            'paths': {
                '/users': {
                    'get': {
                        'operationId': 'getUsers',
                        'responses': {
                            '200': {
                                'content': {
                                    'application/json': {
                                        'schema': {'$ref': '#/components/schemas/UserList'}
                                    }
                                }
                            }
                        }
                    },
                    'post': {
                        'operationId': 'createUser',
                        'responses': {
                            '200': {
                                'content': {
                                    'application/json': {
                                        'schema': {'$ref': '#/components/schemas/User'}
                                    }
                                }
                            }
                        }
                    }
                },
                '/products': {
                    'get': {
                        'operationId': 'getProducts',
                        'responses': {
                            '200': {
                                'content': {
                                    'application/json': {
                                        'schema': {'$ref': '#/components/schemas/ProductList'}
                                    }
                                }
                            }
                        }
                    }
                }
            },
            'components': {
                'schemas': {
                    'User': {
                        'type': 'object',
                        'properties': {'name': {'type': 'string'}}
                    },
                    'UserList': {
                        'type': 'array',
                        'items': {'$ref': '#/components/schemas/User'}
                    },
                    'Product': {
                        'type': 'object',
                        'properties': {'name': {'type': 'string'}}
                    },
                    'ProductList': {
                        'type': 'array',
                        'items': {'$ref': '#/components/schemas/Product'}
                    }
                }
            }
        }
        
        # Build minimal spec for just getUsers operation
        operations = self.minifier.find_operations(test_spec, ['getUsers'])
        dependencies = self.minifier.calculate_dependencies(test_spec, operations)
        minimal_spec = self.minifier.build_minimal_spec(test_spec, operations, dependencies)
        
        if not isinstance(minimal_spec, dict):
            print(f"   Expected dict, got {type(minimal_spec)}")
            return False
        
        # Check structure
        required_keys = ['openapi', 'info', 'paths', 'components']
        for key in required_keys:
            if key not in minimal_spec:
                print(f"   Missing key: {key}")
                return False
        
        # Should only have getUsers path
        if '/users' not in minimal_spec['paths']:
            print("   Missing /users path")
            return False
        
        if '/products' in minimal_spec['paths']:
            print("   Should not include /products path")
            return False
        
        # Should only have get method under /users
        if 'get' not in minimal_spec['paths']['/users']:
            print("   Missing GET method under /users")
            return False
        
        if 'post' in minimal_spec['paths']['/users']:
            print("   Should not include POST method under /users")
            return False
        
        # Check schemas
        schemas = minimal_spec.get('components', {}).get('schemas', {})
        expected_schemas = {'User', 'UserList'}
        
        if not all(schema in schemas for schema in expected_schemas):
            print(f"   Missing required schemas. Expected {expected_schemas}, got {set(schemas.keys())}")
            return False
        
        if 'Product' in schemas or 'ProductList' in schemas:
            print("   Should not include Product schemas")
            return False
        
        print("   Generated correct minimal specification")
        return True
    
    def test_spec_validation(self) -> bool:
        """Test specification validation."""
        # Valid spec
        valid_spec = {
            'openapi': '3.0.0',
            'info': {'title': 'Test', 'version': '1.0.0'},
            'paths': {
                '/test': {
                    'get': {
                        'responses': {
                            '200': {'description': 'Success'}
                        }
                    }
                }
            }
        }
        
        errors = self.minifier.validate_output(valid_spec)
        if errors:
            print(f"   Valid spec reported errors: {errors}")
            return False
        
        # Invalid spec (missing required fields)
        invalid_spec = {
            'openapi': '3.0.0',
            'paths': {
                '/test': {
                    'get': {
                        'responses': {
                            '200': {'description': 'Success'}
                        }
                    }
                }
            }
        }
        
        errors = self.minifier.validate_output(invalid_spec)
        if not errors:
            print("   Invalid spec reported no errors")
            return False
        
        print(f"   Validation correctly identified {len(errors)} errors")
        return True
    
    def test_size_reduction_metrics(self) -> bool:
        """Test size reduction calculation."""
        large_spec = {
            'openapi': '3.0.0',
            'info': {'title': 'Large API', 'version': '1.0.0'},
            'paths': {}
        }
        
        # Add many paths to make it "large"
        for i in range(50):
            large_spec['paths'][f'/resource{i}'] = {
                'get': {
                    'operationId': f'getResource{i}',
                    'responses': {
                        '200': {
                            'description': 'Success',
                            'content': {
                                'application/json': {
                                    'schema': {'$ref': f'#/components/schemas/Resource{i}'}
                                }
                            }
                        }
                    }
                }
            }
        
        # Add schemas
        large_spec['components'] = {'schemas': {}}
        for i in range(50):
            large_spec['components']['schemas'][f'Resource{i}'] = {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'name': {'type': 'string'},
                    'description': {'type': 'string'},
                    'metadata': {'type': 'object'}
                }
            }
        
        # Test minification with just one operation
        result = self.minifier.minify_spec(large_spec, ['getResource0'])
        
        if not result.success:
            print(f"   Minification failed: {result.errors}")
            return False
        
        if result.reduction_percentage < 80:
            print(f"   Size reduction too small: {result.reduction_percentage}%")
            return False
        
        if result.reduction_percentage > 99:
            print(f"   Size reduction suspiciously high: {result.reduction_percentage}%")
            return False
        
        print(f"   Achieved {result.reduction_percentage:.1f}% size reduction")
        return True
    
    def test_configuration_options(self) -> bool:
        """Test different configuration options."""
        # Test with descriptions included
        config_with_desc = MinificationConfig(include_descriptions=True)
        minifier_with_desc = create_minifier(config_with_desc)
        
        if not minifier_with_desc.config.include_descriptions:
            print("   Configuration not applied correctly")
            return False
        
        # Test with descriptions excluded
        config_no_desc = MinificationConfig(include_descriptions=False)
        minifier_no_desc = create_minifier(config_no_desc)
        
        if minifier_no_desc.config.include_descriptions:
            print("   Configuration not applied correctly")
            return False
        
        print("   Configuration options working correctly")
        return True
    
    def test_error_handling(self) -> bool:
        """Test error handling for invalid inputs."""
        # Test with non-existent file
        result = self.minifier.minify_file('non_existent_file.yaml', ['someOp'])
        
        if result.success:
            print("   Should fail for non-existent file")
            return False
        
        if not result.errors:
            print("   Should report errors for non-existent file")
            return False
        
        # Test with empty operation list
        test_spec = {
            'openapi': '3.0.0',
            'info': {'title': 'Test', 'version': '1.0.0'},
            'paths': {}
        }
        
        result = self.minifier.minify_spec(test_spec, [])
        
        # This might succeed or fail depending on implementation
        # Just check that it doesn't crash
        
        print("   Error handling working correctly")
        return True
    
    def run_all_tests(self) -> None:
        """Run all tests and show summary."""
        if not MINIFIER_AVAILABLE:
            print("\n❌ Cannot run tests - minifier modules not available")
            print("Implement the required modules first:")
            print("  - minifier/parser.py")
            print("  - minifier/analyzer.py") 
            print("  - minifier/extractor.py")
            print("  - minifier/validator.py")
            print("  - minifier/spec_minifier.py")
            return
        
        print("🚀 OpenAPI Minifier Test Suite")
        print("=" * 50)
        
        tests = [
            ("Minifier Initialization", self.test_minifier_initialization),
            ("Simple Spec Loading", self.test_simple_spec_loading),
            ("Operation Finding", self.test_operation_finding),
            ("Dependency Resolution", self.test_dependency_resolution),
            ("Minimal Spec Generation", self.test_minimal_spec_generation),
            ("Spec Validation", self.test_spec_validation),
            ("Size Reduction Metrics", self.test_size_reduction_metrics),
            ("Configuration Options", self.test_configuration_options),
            ("Error Handling", self.test_error_handling)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            if self.run_test(test_name, test_func):
                passed += 1
        
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print(f"✅ Passed: {passed}/{total}")
        print(f"❌ Failed: {total - passed}/{total}")
        
        if passed == total:
            print("\n🎉 ALL TESTS PASSED! Your minifier is working correctly.")
            print("Next steps:")
            print("  - Build the CLI interface (minify.py)")
            print("  - Test with real OpenAPI specs")
            print("  - Optimize for larger specifications")
        else:
            print("\n🔧 Some tests failed. Check your implementation:")
            for result in self.test_results:
                if result['status'] != 'PASS':
                    print(f"  - {result['test']}: {result['status']}")
        
        # Show implementation status
        not_implemented = [r for r in self.test_results if r['status'] == 'NOT_IMPLEMENTED']
        if not_implemented:
            print(f"\n🚧 {len(not_implemented)} tests not implemented yet")
            print("This is normal for a hackathon - implement step by step!")

def main():
    """Main test runner."""
    tester = MinifierTester()
    
    # Check if specific test requested
    if len(sys.argv) > 1:
        test_name = sys.argv[1]
        
        # Map test names to methods
        test_map = {
            'init': tester.test_minifier_initialization,
            'loading': tester.test_simple_spec_loading,
            'operations': tester.test_operation_finding,
            'dependencies': tester.test_dependency_resolution,
            'minification': tester.test_minimal_spec_generation,
            'validation': tester.test_spec_validation,
            'metrics': tester.test_size_reduction_metrics,
            'config': tester.test_configuration_options,
            'errors': tester.test_error_handling
        }
        
        if test_name in test_map:
            tester.run_test(test_name.title(), test_map[test_name])
        else:
            print(f"Unknown test: {test_name}")
            print(f"Available tests: {', '.join(test_map.keys())}")
    else:
        tester.run_all_tests()

if __name__ == "__main__":
    main()