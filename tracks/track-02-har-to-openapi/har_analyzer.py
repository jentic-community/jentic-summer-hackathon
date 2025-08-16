#!/usr/bin/env python3
"""
HAR File Analyzer for API Discovery

This script analyzes HTTP Archive (HAR) files to identify API patterns
and generate insights for OpenAPI specification creation.
"""

import json
import sys
import argparse
from urllib.parse import urlparse, parse_qs
from collections import defaultdict, Counter
from typing import List, Dict, Any
import re

def load_har_file(filepath: str) -> Dict[str, Any]:
    """Load and parse HAR file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading HAR file: {e}")
        sys.exit(1)

def extract_api_candidates(har_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract potential API calls from HAR data."""
    entries = har_data['log']['entries']
    api_candidates = []
    
    for entry in entries:
        request = entry['request']
        response = entry['response']
        
        # Filter criteria for API-like requests
        is_api_candidate = (
            # JSON content type
            'json' in response.get('content', {}).get('mimeType', '').lower() or
            # API in URL path
            '/api/' in request['url'].lower() or
            # AJAX/XHR requests
            any(h['name'].lower() == 'x-requested-with' for h in request['headers']) or
            # Non-GET methods often indicate API usage
            request['method'] in ['POST', 'PUT', 'PATCH', 'DELETE'] or
            # Common API patterns in URL
            re.search(r'/(v\d+|rest|graphql|api)/', request['url'], re.IGNORECASE)
        )
        
        if is_api_candidate:
            api_candidates.append({
                'url': request['url'],
                'method': request['method'],
                'status': response['status'],
                'headers': {h['name']: h['value'] for h in request['headers']},
                'query_params': {p['name']: p['value'] for p in request.get('queryString', [])},
                'request_body': request.get('postData', {}).get('text', ''),
                'response_body': response.get('content', {}).get('text', ''),
                'response_type': response.get('content', {}).get('mimeType', ''),
                'response_size': response.get('content', {}).get('size', 0),
                'timing': entry.get('time', 0)
            })
    
    return api_candidates

def analyze_url_patterns(api_calls: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze URL patterns to identify endpoints."""
    patterns = defaultdict(list)
    base_urls = Counter()
    
    for call in api_calls:
        parsed = urlparse(call['url'])
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        base_urls[base_url] += 1
        
        # Normalize path for pattern recognition
        path = parsed.path
        # Replace likely ID patterns with placeholder
        normalized_path = re.sub(r'/\d+(?=/|$)', '/{id}', path)
        normalized_path = re.sub(r'/[a-f0-9]{8,}(?=/|$)', '/{id}', normalized_path)
        
        pattern_key = f"{call['method']} {normalized_path}"
        patterns[pattern_key].append(call)
    
    return {
        'patterns': dict(patterns),
        'base_urls': dict(base_urls),
        'most_common_base': base_urls.most_common(1)[0] if base_urls else None
    }

def analyze_authentication(api_calls: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze authentication patterns."""
    auth_patterns = {
        'bearer_tokens': 0,
        'api_keys': 0,
        'basic_auth': 0,
        'cookies': 0,
        'custom_headers': set()
    }
    
    for call in api_calls:
        headers = call['headers']
        
        # Check for common auth patterns
        for header_name, header_value in headers.items():
            header_lower = header_name.lower()
            
            if header_lower == 'authorization':
                if header_value.startswith('Bearer'):
                    auth_patterns['bearer_tokens'] += 1
                elif header_value.startswith('Basic'):
                    auth_patterns['basic_auth'] += 1
            elif header_lower == 'cookie':
                auth_patterns['cookies'] += 1
            elif 'api' in header_lower and 'key' in header_lower:
                auth_patterns['api_keys'] += 1
                auth_patterns['custom_headers'].add(header_name)
            elif header_lower.startswith('x-api'):
                auth_patterns['custom_headers'].add(header_name)
    
    auth_patterns['custom_headers'] = list(auth_patterns['custom_headers'])
    return auth_patterns

def generate_openapi_skeleton(analysis: Dict[str, Any], api_calls: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate basic OpenAPI specification skeleton."""
    base_url = analysis['most_common_base'][0] if analysis['most_common_base'] else 'https://api.example.com'
    
    openapi_spec = {
        'openapi': '3.0.0',
        'info': {
            'title': 'Discovered API',
            'description': 'API specification reverse-engineered from HAR analysis',
            'version': '1.0.0',
            'x-jentic-source-url': base_url.replace('api.', '').replace('//api', '//')
        },
        'servers': [
            {
                'url': base_url,
                'description': 'API server discovered from HAR analysis'
            }
        ],
        'paths': {},
        'components': {
            'schemas': {},
            'securitySchemes': {}
        }
    }
    
    # Add security schemes based on detected auth patterns
    auth_analysis = analyze_authentication(api_calls)
    if auth_analysis['bearer_tokens'] > 0:
        openapi_spec['components']['securitySchemes']['BearerAuth'] = {
            'type': 'http',
            'scheme': 'bearer',
            'description': 'Bearer token authentication'
        }
    
    if auth_analysis['api_keys'] > 0:
        openapi_spec['components']['securitySchemes']['ApiKeyAuth'] = {
            'type': 'apiKey',
            'in': 'header',
            'name': 'X-API-Key',
            'description': 'API key authentication'
        }
    
    # Generate path stubs
    for pattern, calls in analysis['patterns'].items():
        method, path = pattern.split(' ', 1)
        
        if path not in openapi_spec['paths']:
            openapi_spec['paths'][path] = {}
        
        # Basic operation structure
        operation = {
            'summary': f'{method} {path}',
            'description': f'Endpoint discovered from HAR analysis ({len(calls)} calls observed)',
            'responses': {
                '200': {
                    'description': 'Successful response',
                    'content': {
                        'application/json': {
                            'schema': {
                                'type': 'object',
                                'description': 'Response schema to be defined based on actual responses'
                            }
                        }
                    }
                }
            }
        }
        
        # Add parameters if detected
        sample_call = calls[0]
        if sample_call['query_params']:
            operation['parameters'] = []
            for param_name, param_value in sample_call['query_params'].items():
                operation['parameters'].append({
                    'name': param_name,
                    'in': 'query',
                    'required': False,
                    'schema': {'type': 'string'},
                    'example': param_value,
                    'description': f'Parameter discovered in HAR analysis'
                })
        
        openapi_spec['paths'][path][method.lower()] = operation
    
    return openapi_spec

def print_analysis_report(analysis: Dict[str, Any], auth_analysis: Dict[str, Any], api_calls: List[Dict[str, Any]]):
    """Print comprehensive analysis report."""
    print("=" * 60)
    print("🔍 HAR FILE ANALYSIS REPORT")
    print("=" * 60)
    
    # Summary statistics
    print(f"\n📊 SUMMARY STATISTICS")
    print(f"Total API calls analyzed: {len(api_calls)}")
    print(f"Unique endpoint patterns: {len(analysis['patterns'])}")
    print(f"Base URLs discovered: {len(analysis['base_urls'])}")
    
    if analysis['most_common_base']:
        print(f"Primary API base URL: {analysis['most_common_base'][0]} ({analysis['most_common_base'][1]} calls)")
    
    # Base URLs
    print(f"\n🌐 DISCOVERED BASE URLS")
    for base_url, count in sorted(analysis['base_urls'].items(), key=lambda x: x[1], reverse=True):
        print(f"  {base_url}: {count} calls")
    
    # Endpoint patterns
    print(f"\n🛣️  ENDPOINT PATTERNS")
    for pattern, calls in sorted(analysis['patterns'].items()):
        status_codes = Counter(call['status'] for call in calls)
        status_summary = ', '.join(f"{code}: {count}" for code, count in status_codes.items())
        print(f"  {pattern}")
        print(f"    Calls: {len(calls)}, Status codes: {status_summary}")
        
        # Show sample query parameters
        sample_params = calls[0]['query_params']
        if sample_params:
            print(f"    Sample params: {dict(list(sample_params.items())[:3])}")
    
    # Authentication analysis
    print(f"\n🔐 AUTHENTICATION ANALYSIS")
    print(f"Bearer tokens detected: {auth_analysis['bearer_tokens']} calls")
    print(f"API keys detected: {auth_analysis['api_keys']} calls")
    print(f"Basic auth detected: {auth_analysis['basic_auth']} calls")
    print(f"Cookie auth detected: {auth_analysis['cookies']} calls")
    
    if auth_analysis['custom_headers']:
        print(f"Custom auth headers: {', '.join(auth_analysis['custom_headers'])}")
    
    # Response analysis
    print(f"\n📄 RESPONSE ANALYSIS")
    response_types = Counter(call['response_type'] for call in api_calls if call['response_type'])
    for content_type, count in response_types.most_common():
        print(f"  {content_type}: {count} responses")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS")
    print("1. Focus on endpoints with successful responses (2xx status codes)")
    print("2. Prioritize JSON endpoints for easier documentation")
    print("3. Document authentication requirements found in the analysis")
    print("4. Test endpoints manually to understand parameter behavior")
    print("5. Look for pagination patterns in list endpoints")
    
    if len(analysis['patterns']) > 10:
        print("6. Consider grouping similar endpoints for documentation efficiency")
    
    print(f"\n📝 NEXT STEPS")
    print("1. Create OpenAPI specification using the skeleton generated")
    print("2. Add detailed parameter descriptions and examples")
    print("3. Define response schemas based on actual response data")
    print("4. Test the specification with Arazzo Runner")
    print("5. Sanitize any sensitive data before submission")

def main():
    parser = argparse.ArgumentParser(description='Analyze HAR files for API discovery')
    parser.add_argument('har_file', help='Path to HAR file to analyze')
    parser.add_argument('--output', '-o', help='Output file for OpenAPI skeleton (optional)')
    parser.add_argument('--format', choices=['yaml', 'json'], default='yaml', help='Output format')
    
    args = parser.parse_args()
    
    # Load and analyze HAR file
    print(f"🔍 Analyzing HAR file: {args.har_file}")
    har_data = load_har_file(args.har_file)
    
    # Extract API candidates
    api_calls = extract_api_candidates(har_data)
    
    if not api_calls:
        print("❌ No API calls found in HAR file. Check the capture or filtering criteria.")
        return
    
    # Perform analysis
    url_analysis = analyze_url_patterns(api_calls)
    auth_analysis = analyze_authentication(api_calls)
    
    # Print report
    print_analysis_report(url_analysis, auth_analysis, api_calls)
    
    # Generate OpenAPI skeleton if requested
    if args.output:
        openapi_spec = generate_openapi_skeleton(url_analysis, api_calls)
        
        try:
            if args.format == 'yaml':
                import yaml
                with open(args.output, 'w') as f:
                    yaml.dump(openapi_spec, f, default_flow_style=False, sort_keys=False)
            else:
                with open(args.output, 'w') as f:
                    json.dump(openapi_spec, f, indent=2)
            
            print(f"\n✅ OpenAPI skeleton saved to: {args.output}")
            print("📝 Remember to:")
            print("   - Add detailed descriptions and examples")
            print("   - Define proper response schemas")
            print("   - Validate the specification")
            print("   - Remove any sensitive data")
            
        except Exception as e:
            print(f"❌ Error saving OpenAPI skeleton: {e}")

if __name__ == "__main__":
    main()