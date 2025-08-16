#!/usr/bin/env python3
"""
OpenAPI Minifier CLI - Phase 3 Advanced Features
Command-line interface for minifying OpenAPI specifications.
"""

import argparse
import sys
import yaml
import json
from pathlib import Path
from typing import List, Dict, Any

from minifier.spec_minifier import create_minifier, MinificationConfig
from minifier.analytics_engine import APIAnalyticsEngine
from minifier.ecosystem_integration import EcosystemIntegrator, IntegrationConfig


def main():
    """Main CLI entry point with Phase 3 features."""
    parser = argparse.ArgumentParser(
        description="Minify OpenAPI specifications for agent optimization",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic minification
  python minify.py --input api.yaml --operations createTask,updateTask --output minimal.yaml
  
  # Advanced configuration
  python minify.py --input api.yaml --operations createTask --output minimal.json \\
    --format json --no-descriptions --no-examples --validate
  
  # Batch processing
  python minify.py --batch --config batch_config.yaml
  
  # Agent-specific optimization
  python minify.py --input api.yaml --operations createTask --output task_agent.yaml \\
    --agent-type task_creator --optimize-for speed
        """
    )
    
    # Input/Output options
    parser.add_argument("--input", "-i", required=True, 
                       help="Input OpenAPI specification file (YAML/JSON)")
    parser.add_argument("--output", "-o", required=True,
                       help="Output file for minified specification")
    parser.add_argument("--operations", "--ops", required=True,
                       help="Comma-separated operations (IDs, paths, or descriptions)")
    
    # Format options
    parser.add_argument("--format", choices=["yaml", "json"], default="auto",
                       help="Output format (auto-detect from extension)")
    parser.add_argument("--pretty", action="store_true",
                       help="Pretty-print output with indentation")
    
    # Optimization options
    parser.add_argument("--no-descriptions", action="store_true",
                       help="Remove description fields to reduce size")
    parser.add_argument("--no-examples", action="store_true",
                       help="Remove example fields to reduce size")
    parser.add_argument("--strip-unused", action="store_true",
                       help="Strip unused properties from schemas")
    parser.add_argument("--optimize-allof", action="store_true", default=True,
                       help="Optimize allOf/oneOf/anyOf constructs")
    parser.add_argument("--no-security", action="store_true",
                       help="Remove security schemes and requirements")
    
    # Agent-specific options
    parser.add_argument("--agent-type", choices=["task_creator", "bug_tracker", "review_manager", "board_admin", "notification_agent"],
                       help="Use predefined optimization for agent type")
    parser.add_argument("--optimize-for", choices=["speed", "size", "completeness"], default="balanced",
                       help="Optimization strategy")
    
    # Validation and quality
    parser.add_argument("--validate", action="store_true",
                       help="Validate output specification")
    parser.add_argument("--metrics", action="store_true",
                       help="Show detailed quality metrics")
    parser.add_argument("--min-reduction", type=float, default=0.0,
                       help="Minimum required size reduction percentage")
    
    # Advanced features
    parser.add_argument("--batch", action="store_true",
                       help="Batch processing mode")
    parser.add_argument("--config", 
                       help="Configuration file for batch processing")
    parser.add_argument("--dependency-graph", action="store_true",
                       help="Generate dependency graph analysis")
    parser.add_argument("--circular-check", action="store_true", default=True,
                       help="Check for circular dependencies")
    
    # Debugging
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Verbose output")
    parser.add_argument("--debug", action="store_true",
                       help="Debug mode with detailed analysis")
    
    # Phase 4: Advanced Features
    parser.add_argument("--analytics", action="store_true",
                       help="Run advanced analytics on the API")
    parser.add_argument("--ecosystem-validate", action="store_true",
                       help="Validate with ecosystem tools (Spectral, Swagger, etc.)")
    parser.add_argument("--generate-sdks", 
                       help="Generate client SDKs (comma-separated languages)")
    parser.add_argument("--generate-docs", choices=["html", "pdf"],
                       help="Generate API documentation")
    parser.add_argument("--ci-integration", action="store_true",
                       help="Enable CI/CD integration features")
    parser.add_argument("--monitoring", action="store_true",
                       help="Set up API monitoring")
    
    args = parser.parse_args()
    
    if args.batch:
        return handle_batch_processing(args)
    else:
        return handle_single_file(args)


def handle_single_file(args) -> int:
    """Handle single file minification."""
    try:
        # Create configuration
        config = create_config_from_args(args)
        
        # Create minifier
        minifier = create_minifier(config)
        
        if args.verbose:
            print(f"🔧 Loading OpenAPI spec from {args.input}")
        
        # Load input spec
        input_path = Path(args.input)
        if not input_path.exists():
            print(f"❌ Error: Input file not found: {args.input}")
            return 1
        
        spec = load_spec_file(input_path)
        
        if args.verbose:
            original_ops = len(spec.get('paths', {}))
            original_schemas = len(spec.get('components', {}).get('schemas', {}))
            print(f"📊 Original spec: {original_ops} operations, {original_schemas} schemas")
        
        # Parse operations
        operations = [op.strip() for op in args.operations.split(',')]
        
        if args.verbose:
            print(f"🎯 Target operations: {operations}")
        
        # Perform minification
        result = minifier.minify_spec(spec, operations)
        
        if not result.success:
            print(f"❌ Minification failed:")
            for error in result.errors or []:
                print(f"   • {error}")
            return 1
        
        # Check minimum reduction requirement
        if args.min_reduction > 0 and result.reduction_percentage < args.min_reduction:
            print(f"❌ Size reduction {result.reduction_percentage:.1f}% below minimum {args.min_reduction:.1f}%")
            return 1
        
        # Validate if requested
        if args.validate:
            validation_errors = minifier.validate_output(result.spec)
            if validation_errors:
                print(f"❌ Validation failed:")
                for error in validation_errors:
                    print(f"   • {error}")
                return 1
            elif args.verbose:
                print("✅ Validation passed")
        
        # Save output
        output_path = Path(args.output)
        save_spec_file(result.spec, output_path, args)
        
        # Show results
        print(f"✅ Minified spec saved to {args.output}")
        print(f"📉 Size reduction: {result.reduction_percentage:.1f}%")
        print(f"🎯 Completeness: {result.completeness_score:.1f}%")
        
        if args.metrics:
            show_detailed_metrics(result)
        
        if args.debug:
            show_debug_info(result, minifier)
        
        # Phase 4: Advanced Features
        if any([args.analytics, args.ecosystem_validate, args.generate_sdks, 
                args.generate_docs, args.ci_integration, args.monitoring]):
            run_phase4_features(args, spec, result.spec, minifier)
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        return 1


def handle_batch_processing(args) -> int:
    """Handle batch processing mode."""
    if not args.config:
        print("❌ Error: --config required for batch processing")
        return 1
    
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"❌ Error: Config file not found: {args.config}")
        return 1
    
    try:
        with open(config_path) as f:
            batch_config = yaml.safe_load(f)
        
        results = []
        for job in batch_config.get('jobs', []):
            print(f"🔄 Processing {job['name']}...")
            
            # Override args with job config
            job_args = argparse.Namespace(**{**vars(args), **job})
            result_code = handle_single_file(job_args)
            
            results.append({
                'name': job['name'],
                'success': result_code == 0
            })
        
        # Show batch results
        successful = sum(1 for r in results if r['success'])
        total = len(results)
        print(f"\n📊 Batch Results: {successful}/{total} successful")
        
        for result in results:
            status = "✅" if result['success'] else "❌"
            print(f"   {status} {result['name']}")
        
        return 0 if successful == total else 1
        
    except Exception as e:
        print(f"❌ Batch processing error: {e}")
        return 1


def create_config_from_args(args) -> MinificationConfig:
    """Create MinificationConfig from command line arguments."""
    
    # Agent-specific presets
    if args.agent_type:
        if args.agent_type == "task_creator":
            return MinificationConfig(
                include_descriptions=True,
                include_examples=True,
                strip_unused_properties=False,
                optimize_allof_oneof=True,
                preserve_security=not args.no_security
            )
        elif args.agent_type == "bug_tracker":
            return MinificationConfig(
                include_descriptions=False,
                include_examples=False,
                strip_unused_properties=True,
                optimize_allof_oneof=True,
                preserve_security=not args.no_security
            )
        elif args.agent_type == "notification_agent":
            return MinificationConfig(
                include_descriptions=False,
                include_examples=False,
                strip_unused_properties=True,
                optimize_allof_oneof=True,
                preserve_security=False
            )
    
    # Optimization strategy presets
    if args.optimize_for == "speed":
        return MinificationConfig(
            include_descriptions=False,
            include_examples=False,
            strip_unused_properties=True,
            optimize_allof_oneof=True,
            preserve_security=not args.no_security
        )
    elif args.optimize_for == "size":
        return MinificationConfig(
            include_descriptions=False,
            include_examples=False,
            strip_unused_properties=True,
            optimize_allof_oneof=True,
            preserve_security=False
        )
    elif args.optimize_for == "completeness":
        return MinificationConfig(
            include_descriptions=True,
            include_examples=True,
            strip_unused_properties=False,
            optimize_allof_oneof=False,
            preserve_security=True
        )
    
    # Custom configuration from flags
    return MinificationConfig(
        include_descriptions=not args.no_descriptions,
        include_examples=not args.no_examples,
        strip_unused_properties=args.strip_unused,
        optimize_allof_oneof=args.optimize_allof,
        preserve_security=not args.no_security,
        build_dependency_graph=args.dependency_graph,
        detect_circular_refs=args.circular_check
    )


def load_spec_file(file_path: Path) -> Dict[str, Any]:
    """Load OpenAPI spec from YAML or JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        if file_path.suffix.lower() in ['.yaml', '.yml']:
            # Handle multi-document YAML files by taking the first document
            docs = list(yaml.safe_load_all(f))
            return docs[0] if docs else {}
        elif file_path.suffix.lower() == '.json':
            return json.load(f)
        else:
            # Try to detect format
            content = f.read()
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                # Try YAML with multi-document support
                docs = list(yaml.safe_load_all(content))
                return docs[0] if docs else {}


def save_spec_file(spec: Dict[str, Any], file_path: Path, args) -> None:
    """Save OpenAPI spec to YAML or JSON file."""
    
    # Determine format
    if args.format == "auto":
        if file_path.suffix.lower() == '.json':
            format_type = "json"
        else:
            format_type = "yaml"
    else:
        format_type = args.format
    
    # Ensure parent directory exists
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        if format_type == "json":
            if args.pretty:
                json.dump(spec, f, indent=2, sort_keys=False)
            else:
                json.dump(spec, f, separators=(',', ':'))
        else:
            yaml.dump(spec, f, default_flow_style=False, sort_keys=False)


def show_detailed_metrics(result) -> None:
    """Show detailed quality metrics."""
    if not result.quality_metrics:
        return
    
    metrics = result.quality_metrics
    print("\n📊 Detailed Metrics:")
    print(f"   Operation reduction: {metrics['operation_reduction_percentage']:.1f}%")
    print(f"   Schema reduction: {metrics['schema_reduction_percentage']:.1f}%")
    print(f"   Byte size reduction: {metrics['byte_size_reduction_percentage']:.1f}%")
    print(f"   Operations: {metrics['minified_operations']}/{metrics['original_operations']}")
    print(f"   Schemas: {metrics['minified_schemas']}/{metrics['original_schemas']}")
    print(f"   Size: {metrics['minified_size_bytes']:,} / {metrics['original_size_bytes']:,} bytes")


def show_debug_info(result, minifier) -> None:
    """Show debug information."""
    print("\n🔍 Debug Information:")
    
    if result.dependency_analysis:
        analysis = result.dependency_analysis
        print(f"   Direct dependencies: {analysis['direct_dependencies']}")
        print(f"   Total dependencies: {analysis['total_dependencies']}")
        print(f"   Circular references: {len(analysis['circular_refs'])}")
        
        if analysis['dependency_chains']:
            print("   Dependency chains:")
            for schema, deps in list(analysis['dependency_chains'].items())[:3]:
                schema_name = schema.split('/')[-1] if '/' in schema else schema
                dep_names = [d.split('/')[-1] if '/' in d else d for d in deps[:3]]
                print(f"     • {schema_name} → {dep_names}")
    
    if result.validation_errors:
        print(f"   Validation errors: {len(result.validation_errors)}")
        for error in result.validation_errors[:3]:
            print(f"     • {error}")


def run_phase4_features(args, original_spec: Dict[str, Any], minified_spec: Dict[str, Any], minifier) -> None:
    """Run Phase 4 advanced features."""
    
    print("\n🚀 Running Phase 4 Advanced Features...")
    
    # Advanced Analytics
    if args.analytics:
        print("\n📊 Running Advanced Analytics...")
        try:
            analytics = APIAnalyticsEngine(minifier.parser)
            
            # Analyze original spec
            complexity_metrics = analytics.analyze_api_complexity(original_spec)
            print(f"   • API Complexity Score: {complexity_metrics.overall_complexity_score:.2f}")
            print(f"   • Optimization Potential: {complexity_metrics.optimization_potential:.1f}%")
            print(f"   • Hotspot Operations: {len(complexity_metrics.hotspot_operations)}")
            
            # Generate recommendations
            recommendations = analytics.generate_intelligent_recommendations(original_spec, complexity_metrics)
            critical_recs = [r for r in recommendations if r.priority == 'critical']
            print(f"   • Critical Recommendations: {len(critical_recs)}")
            
            # Performance benchmark
            operations = [args.operations] if args.operations else list(original_spec.get('paths', {}).keys())[:5]
            benchmark = analytics.benchmark_performance(original_spec, operations)
            print(f"   • Performance: {benchmark.load_time_ms:.1f}ms load, {benchmark.memory_usage_mb:.1f}MB memory")
            
        except Exception as e:
            print(f"   ❌ Analytics failed: {e}")
    
    # Ecosystem Validation
    if args.ecosystem_validate:
        print("\n🔍 Running Ecosystem Validation...")
        try:
            integrator = EcosystemIntegrator()
            validation_results = integrator.validate_with_ecosystem_tools(minified_spec)
            
            if validation_results:
                valid_count = sum(1 for r in validation_results if r.valid)
                print(f"   • Validation Results: {valid_count}/{len(validation_results)} tools passed")
                
                for result in validation_results:
                    status = "✅" if result.valid else "❌"
                    print(f"     {status} {result.validator_used}: {len(result.errors)} errors, {len(result.warnings)} warnings")
            else:
                print("   ⚠️  No ecosystem validators available")
                
        except Exception as e:
            print(f"   ❌ Ecosystem validation failed: {e}")
    
    # SDK Generation
    if args.generate_sdks:
        print("\n🛠️  Generating Client SDKs...")
        try:
            languages = [lang.strip() for lang in args.generate_sdks.split(',')]
            integrator = EcosystemIntegrator()
            
            sdk_results = integrator.generate_client_sdks(minified_spec, languages, 'generated-sdks')
            
            for language, success in sdk_results.items():
                status = "✅" if success else "❌"
                print(f"   {status} {language} SDK")
                
        except Exception as e:
            print(f"   ❌ SDK generation failed: {e}")
    
    # Documentation Generation
    if args.generate_docs:
        print(f"\n📚 Generating {args.generate_docs.upper()} Documentation...")
        try:
            integrator = EcosystemIntegrator()
            success = integrator.generate_documentation(minified_spec, args.generate_docs, 'docs')
            
            if success:
                print(f"   ✅ Documentation generated in docs/ directory")
            else:
                print(f"   ❌ Documentation generation failed")
                
        except Exception as e:
            print(f"   ❌ Documentation generation failed: {e}")
    
    # CI/CD Integration
    if args.ci_integration:
        print("\n🔄 Setting up CI/CD Integration...")
        try:
            integrator = EcosystemIntegrator(IntegrationConfig(enable_ci_integration=True))
            
            # Create GitHub workflow
            from minifier.ecosystem_integration import create_ci_cd_workflow
            workflow_created = create_ci_cd_workflow("openapi-minifier")
            
            if workflow_created:
                print("   ✅ GitHub Actions workflow created")
            
            # Run quality gates
            quality_gates = integrator._run_quality_gates(args.input, {args.output: args.output})
            passed_gates = sum(1 for gate in quality_gates if gate['passed'])
            print(f"   • Quality Gates: {passed_gates}/{len(quality_gates)} passed")
            
        except Exception as e:
            print(f"   ❌ CI/CD integration failed: {e}")
    
    # Monitoring Setup
    if args.monitoring:
        print("\n📈 Setting up API Monitoring...")
        try:
            integrator = EcosystemIntegrator(IntegrationConfig(enable_monitoring=True))
            
            # Extract API endpoints for monitoring
            endpoints = []
            for path in original_spec.get('paths', {}).keys():
                # Convert OpenAPI path to actual URL (simplified)
                if original_spec.get('servers'):
                    base_url = original_spec['servers'][0]['url']
                    endpoints.append(f"{base_url}{path}")
            
            monitoring_config = integrator.setup_monitoring(endpoints[:5])  # Monitor top 5 endpoints
            
            if monitoring_config['enabled']:
                print(f"   ✅ Monitoring configured for {len(monitoring_config['health_checks'])} endpoints")
                print(f"   • Health checks: {len(monitoring_config['health_checks'])}")
                print(f"   • Performance monitors: {len(monitoring_config['performance_monitors'])}")
            
        except Exception as e:
            print(f"   ❌ Monitoring setup failed: {e}")
    
    print("\n🎉 Phase 4 features completed!")


if __name__ == "__main__":
    sys.exit(main())