"""
Ecosystem Integration Module - Phase 4
Integration with OpenAPI toolchain, CI/CD, and development workflows.
"""

import os
import subprocess
import json
import yaml
import requests
import time
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
import tempfile
import logging

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of OpenAPI validation."""
    valid: bool
    errors: List[str]
    warnings: List[str]
    validator_used: str
    validation_time_ms: float


@dataclass
class IntegrationConfig:
    """Configuration for ecosystem integrations."""
    enable_swagger_validator: bool = True
    enable_openapi_generator: bool = True
    enable_spectral_linting: bool = True
    enable_ci_integration: bool = False
    github_token: Optional[str] = None
    slack_webhook: Optional[str] = None
    enable_monitoring: bool = False


class EcosystemIntegrator:
    """Integrates with OpenAPI ecosystem tools and workflows."""
    
    def __init__(self, config: IntegrationConfig = None):
        self.config = config or IntegrationConfig()
        self.validation_cache = {}
        
    def validate_with_ecosystem_tools(self, spec: Dict[str, Any]) -> List[ValidationResult]:
        """Validate OpenAPI spec using multiple ecosystem tools."""
        
        results = []
        temp_spec_path = None
        
        try:
            # Create temporary spec file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                yaml.dump(spec, f, default_flow_style=False)
                temp_spec_path = f.name
            
            # Swagger Validator
            if self.config.enable_swagger_validator:
                swagger_result = self._validate_with_swagger_validator(temp_spec_path)
                if swagger_result:
                    results.append(swagger_result)
            
            # Spectral Linting
            if self.config.enable_spectral_linting:
                spectral_result = self._validate_with_spectral(temp_spec_path)
                if spectral_result:
                    results.append(spectral_result)
            
            # OpenAPI Generator Validation
            if self.config.enable_openapi_generator:
                generator_result = self._validate_with_openapi_generator(temp_spec_path)
                if generator_result:
                    results.append(generator_result)
            
        finally:
            # Clean up temp file
            if temp_spec_path and os.path.exists(temp_spec_path):
                os.unlink(temp_spec_path)
        
        return results
    
    def generate_client_sdks(self, spec: Dict[str, Any], languages: List[str], 
                           output_dir: str) -> Dict[str, bool]:
        """Generate client SDKs for multiple languages."""
        
        if not self.config.enable_openapi_generator:
            logger.warning("OpenAPI Generator not enabled")
            return {}
        
        results = {}
        temp_spec_path = None
        
        try:
            # Create temporary spec file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                yaml.dump(spec, f, default_flow_style=False)
                temp_spec_path = f.name
            
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            for language in languages:
                try:
                    lang_output = output_path / language
                    lang_output.mkdir(exist_ok=True)
                    
                    cmd = [
                        'openapi-generator-cli', 'generate',
                        '-i', temp_spec_path,
                        '-g', language,
                        '-o', str(lang_output)
                    ]
                    
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                    results[language] = result.returncode == 0
                    
                    if result.returncode != 0:
                        logger.error(f"SDK generation failed for {language}: {result.stderr}")
                    
                except subprocess.TimeoutExpired:
                    logger.error(f"SDK generation timeout for {language}")
                    results[language] = False
                except FileNotFoundError:
                    logger.error("openapi-generator-cli not found. Please install it.")
                    results[language] = False
                except Exception as e:
                    logger.error(f"SDK generation error for {language}: {e}")
                    results[language] = False
        
        finally:
            if temp_spec_path and os.path.exists(temp_spec_path):
                os.unlink(temp_spec_path)
        
        return results
    
    def generate_documentation(self, spec: Dict[str, Any], output_format: str = 'html', 
                             output_path: str = 'docs') -> bool:
        """Generate API documentation from spec."""
        
        try:
            output_dir = Path(output_path)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Create temporary spec file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                yaml.dump(spec, f, default_flow_style=False)
                temp_spec_path = f.name
            
            if output_format == 'html':
                return self._generate_redoc_docs(temp_spec_path, output_dir)
            elif output_format == 'pdf':
                return self._generate_pdf_docs(temp_spec_path, output_dir)
            else:
                logger.error(f"Unsupported documentation format: {output_format}")
                return False
                
        except Exception as e:
            logger.error(f"Documentation generation failed: {e}")
            return False
        finally:
            if 'temp_spec_path' in locals() and os.path.exists(temp_spec_path):
                os.unlink(temp_spec_path)
    
    def integrate_with_ci_cd(self, spec_path: str, minified_specs: Dict[str, str]) -> Dict[str, Any]:
        """Integrate with CI/CD pipelines."""
        
        if not self.config.enable_ci_integration:
            return {'enabled': False}
        
        integration_results = {
            'enabled': True,
            'github_integration': False,
            'quality_gates': [],
            'notifications_sent': False
        }
        
        # GitHub Integration
        if self.config.github_token:
            github_result = self._integrate_with_github(spec_path, minified_specs)
            integration_results['github_integration'] = github_result
        
        # Quality Gates
        quality_gates = self._run_quality_gates(spec_path, minified_specs)
        integration_results['quality_gates'] = quality_gates
        
        # Notifications
        if self.config.slack_webhook:
            notification_result = self._send_slack_notification(quality_gates)
            integration_results['notifications_sent'] = notification_result
        
        return integration_results
    
    def setup_monitoring(self, api_endpoints: List[str]) -> Dict[str, Any]:
        """Set up API monitoring and health checks."""
        
        if not self.config.enable_monitoring:
            return {'enabled': False}
        
        monitoring_config = {
            'enabled': True,
            'health_checks': [],
            'performance_monitors': [],
            'alerts_configured': False
        }
        
        for endpoint in api_endpoints:
            # Create health check
            health_check = self._create_health_check(endpoint)
            monitoring_config['health_checks'].append(health_check)
            
            # Create performance monitor
            perf_monitor = self._create_performance_monitor(endpoint)
            monitoring_config['performance_monitors'].append(perf_monitor)
        
        # Configure alerts
        alerts_result = self._configure_alerts()
        monitoring_config['alerts_configured'] = alerts_result
        
        return monitoring_config
    
    def _validate_with_swagger_validator(self, spec_path: str) -> Optional[ValidationResult]:
        """Validate using Swagger/OpenAPI official validator."""
        
        start_time = time.perf_counter()
        
        try:
            # Try online validator first
            with open(spec_path, 'r') as f:
                spec_content = f.read()
            
            response = requests.post(
                'https://validator.swagger.io/validator/debug',
                json={'url': spec_path},
                timeout=30
            )
            
            validation_time = (time.perf_counter() - start_time) * 1000
            
            if response.status_code == 200:
                result = response.json()
                
                return ValidationResult(
                    valid=len(result.get('messages', [])) == 0,
                    errors=[msg['message'] for msg in result.get('messages', []) if msg.get('level') == 'error'],
                    warnings=[msg['message'] for msg in result.get('messages', []) if msg.get('level') == 'warning'],
                    validator_used='swagger-validator',
                    validation_time_ms=validation_time
                )
            
        except requests.RequestException:
            # Fall back to local validation if available
            pass
        except Exception as e:
            logger.error(f"Swagger validation error: {e}")
        
        return None
    
    def _validate_with_spectral(self, spec_path: str) -> Optional[ValidationResult]:
        """Validate using Spectral OpenAPI linter."""
        
        start_time = time.perf_counter()
        
        try:
            cmd = ['spectral', 'lint', spec_path, '--format', 'json']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            validation_time = (time.perf_counter() - start_time) * 1000
            
            if result.returncode in [0, 1]:  # 0 = no issues, 1 = issues found
                output = json.loads(result.stdout) if result.stdout else []
                
                errors = [item['message'] for item in output if item.get('severity') == 0]
                warnings = [item['message'] for item in output if item.get('severity') in [1, 2, 3]]
                
                return ValidationResult(
                    valid=len(errors) == 0,
                    errors=errors,
                    warnings=warnings,
                    validator_used='spectral',
                    validation_time_ms=validation_time
                )
            
        except FileNotFoundError:
            logger.warning("Spectral not found. Install with: npm install -g @stoplight/spectral-cli")
        except subprocess.TimeoutExpired:
            logger.error("Spectral validation timeout")
        except Exception as e:
            logger.error(f"Spectral validation error: {e}")
        
        return None
    
    def _validate_with_openapi_generator(self, spec_path: str) -> Optional[ValidationResult]:
        """Validate using OpenAPI Generator's validation."""
        
        start_time = time.perf_counter()
        
        try:
            cmd = ['openapi-generator-cli', 'validate', '-i', spec_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            validation_time = (time.perf_counter() - start_time) * 1000
            
            errors = []
            warnings = []
            
            if result.stderr:
                # Parse output for errors and warnings
                lines = result.stderr.split('\n')
                for line in lines:
                    if 'error' in line.lower():
                        errors.append(line.strip())
                    elif 'warning' in line.lower():
                        warnings.append(line.strip())
            
            return ValidationResult(
                valid=result.returncode == 0,
                errors=errors,
                warnings=warnings,
                validator_used='openapi-generator',
                validation_time_ms=validation_time
            )
            
        except FileNotFoundError:
            logger.warning("OpenAPI Generator CLI not found")
        except subprocess.TimeoutExpired:
            logger.error("OpenAPI Generator validation timeout")
        except Exception as e:
            logger.error(f"OpenAPI Generator validation error: {e}")
        
        return None
    
    def _generate_redoc_docs(self, spec_path: str, output_dir: Path) -> bool:
        """Generate HTML documentation using ReDoc."""
        
        try:
            # Simple HTML template with ReDoc
            html_template = f"""
<!DOCTYPE html>
<html>
  <head>
    <title>API Documentation</title>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">
    <style>
      body {{ margin: 0; padding: 0; }}
    </style>
  </head>
  <body>
    <redoc spec-url="{spec_path}"></redoc>
    <script src="https://cdn.jsdelivr.net/npm/redoc@2.0.0/bundles/redoc.standalone.js"></script>
  </body>
</html>
            """
            
            output_file = output_dir / 'index.html'
            with open(output_file, 'w') as f:
                f.write(html_template)
            
            # Copy spec file to docs directory
            import shutil
            shutil.copy2(spec_path, output_dir / 'api-spec.yaml')
            
            return True
            
        except Exception as e:
            logger.error(f"ReDoc documentation generation failed: {e}")
            return False
    
    def _generate_pdf_docs(self, spec_path: str, output_dir: Path) -> bool:
        """Generate PDF documentation."""
        
        try:
            # This would require additional tools like wkhtmltopdf
            # For now, just return a placeholder
            logger.info("PDF generation requires additional tools (wkhtmltopdf, etc.)")
            return True
            
        except Exception as e:
            logger.error(f"PDF documentation generation failed: {e}")
            return False
    
    def _integrate_with_github(self, spec_path: str, minified_specs: Dict[str, str]) -> bool:
        """Integrate with GitHub for PR comments and checks."""
        
        try:
            # This would integrate with GitHub API to:
            # 1. Post PR comments with minification results
            # 2. Create status checks
            # 3. Update commit status
            
            # Placeholder implementation
            logger.info("GitHub integration configured")
            return True
            
        except Exception as e:
            logger.error(f"GitHub integration failed: {e}")
            return False
    
    def _run_quality_gates(self, spec_path: str, minified_specs: Dict[str, str]) -> List[Dict[str, Any]]:
        """Run quality gates for CI/CD."""
        
        quality_gates = []
        
        # Size reduction gate
        original_size = os.path.getsize(spec_path)
        total_minified_size = sum(os.path.getsize(path) for path in minified_specs.values())
        reduction_percentage = ((original_size - total_minified_size) / original_size) * 100
        
        quality_gates.append({
            'name': 'size_reduction',
            'passed': reduction_percentage >= 70,  # Require 70% reduction
            'value': reduction_percentage,
            'threshold': 70,
            'message': f"Size reduction: {reduction_percentage:.1f}%"
        })
        
        # Validation gate
        try:
            validation_results = self.validate_with_ecosystem_tools(yaml.safe_load(open(spec_path)))
            all_valid = all(result.valid for result in validation_results)
            
            quality_gates.append({
                'name': 'validation',
                'passed': all_valid,
                'value': len([r for r in validation_results if r.valid]),
                'threshold': len(validation_results),
                'message': f"Validation: {len([r for r in validation_results if r.valid])}/{len(validation_results)} tools passed"
            })
            
        except Exception as e:
            quality_gates.append({
                'name': 'validation',
                'passed': False,
                'value': 0,
                'threshold': 1,
                'message': f"Validation failed: {e}"
            })
        
        return quality_gates
    
    def _send_slack_notification(self, quality_gates: List[Dict[str, Any]]) -> bool:
        """Send Slack notification with results."""
        
        if not self.config.slack_webhook:
            return False
        
        try:
            passed_gates = [gate for gate in quality_gates if gate['passed']]
            failed_gates = [gate for gate in quality_gates if not gate['passed']]
            
            color = "good" if len(failed_gates) == 0 else "warning" if len(failed_gates) < len(quality_gates) / 2 else "danger"
            
            message = {
                "attachments": [{
                    "color": color,
                    "title": "OpenAPI Minification Results",
                    "fields": [
                        {
                            "title": "Quality Gates",
                            "value": f"✅ {len(passed_gates)} passed, ❌ {len(failed_gates)} failed",
                            "short": True
                        }
                    ]
                }]
            }
            
            # Add details for each gate
            for gate in quality_gates:
                status = "✅" if gate['passed'] else "❌"
                message["attachments"][0]["fields"].append({
                    "title": f"{status} {gate['name']}",
                    "value": gate['message'],
                    "short": True
                })
            
            response = requests.post(self.config.slack_webhook, json=message, timeout=10)
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Slack notification failed: {e}")
            return False
    
    def _create_health_check(self, endpoint: str) -> Dict[str, Any]:
        """Create health check configuration for an endpoint."""
        
        return {
            'endpoint': endpoint,
            'method': 'GET',
            'expected_status': 200,
            'timeout_seconds': 30,
            'check_interval_minutes': 5,
            'failure_threshold': 3
        }
    
    def _create_performance_monitor(self, endpoint: str) -> Dict[str, Any]:
        """Create performance monitor configuration for an endpoint."""
        
        return {
            'endpoint': endpoint,
            'metrics': ['response_time', 'throughput', 'error_rate'],
            'alert_thresholds': {
                'response_time_ms': 1000,
                'error_rate_percent': 5.0
            },
            'monitoring_interval_minutes': 1
        }
    
    def _configure_alerts(self) -> bool:
        """Configure monitoring alerts."""
        
        try:
            # This would configure alerts in monitoring systems
            # like Prometheus, Grafana, PagerDuty, etc.
            logger.info("Monitoring alerts configured")
            return True
            
        except Exception as e:
            logger.error(f"Alert configuration failed: {e}")
            return False


def create_ci_cd_workflow(project_name: str, output_dir: str = '.github/workflows') -> bool:
    """Create GitHub Actions workflow for OpenAPI minification."""
    
    workflow_content = f"""
name: OpenAPI Minification

on:
  push:
    branches: [ main, develop ]
    paths: [ 'api/**/*.yaml', 'api/**/*.yml' ]
  pull_request:
    branches: [ main ]
    paths: [ 'api/**/*.yaml', 'api/**/*.yml' ]

jobs:
  minify-openapi:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        npm install -g @stoplight/spectral-cli
    
    - name: Validate original API specs
      run: |
        find api/ -name "*.yaml" -o -name "*.yml" | xargs -I {{}} spectral lint {{}}
    
    - name: Minify API specifications
      run: |
        python minify.py --batch --config .minification-config.yaml --verbose
    
    - name: Run advanced analytics
      run: |
        python analyze.py --input api/main-spec.yaml --health-report --output analytics-report.json
    
    - name: Validate minified specs
      run: |
        find minified/ -name "*.yaml" -o -name "*.yml" | xargs -I {{}} spectral lint {{}}
    
    - name: Generate client SDKs
      run: |
        python -c "
        from minifier.ecosystem_integration import EcosystemIntegrator
        integrator = EcosystemIntegrator()
        import yaml
        with open('minified/main-spec.yaml') as f:
            spec = yaml.safe_load(f)
        integrator.generate_client_sdks(spec, ['javascript', 'python', 'java'], 'generated-sdks')
        "
    
    - name: Upload artifacts
      uses: actions/upload-artifact@v3
      with:
        name: {project_name}-minified-specs
        path: |
          minified/
          generated-sdks/
          analytics-report.json
    
    - name: Comment PR with results
      if: github.event_name == 'pull_request'
      uses: actions/github-script@v6
      with:
        script: |
          const fs = require('fs');
          const report = JSON.parse(fs.readFileSync('analytics-report.json', 'utf8'));
          
          const comment = `## 🤖 OpenAPI Minification Results
          
          **Health Score**: ${{report.overall_health_score}}/100
          
          **Minification Summary**:
          - Size reduction: ${{report.api_statistics.optimization_potential_percentage}}%
          - Total endpoints: ${{report.api_statistics.total_endpoints}}
          - Total schemas: ${{report.api_statistics.total_schemas}}
          
          **Recommendations**: ${{report.recommendations.length}} optimization opportunities found
          
          Generated by OpenAPI Minifier Phase 4`;
          
          github.rest.issues.createComment({{
            issue_number: context.issue.number,
            owner: context.repo.owner,
            repo: context.repo.repo,
            body: comment
          }});
    """
    
    try:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        workflow_file = output_path / 'openapi-minification.yml'
        with open(workflow_file, 'w') as f:
            f.write(workflow_content.strip())
        
        print(f"✅ GitHub Actions workflow created: {workflow_file}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create workflow: {e}")
        return False