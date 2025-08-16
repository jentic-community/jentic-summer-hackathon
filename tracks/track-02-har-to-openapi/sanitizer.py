#!/usr/bin/env python3
"""
HAR File Sanitizer

Removes sensitive information from HAR files to make them safe for sharing.
"""

import json
import re
import argparse
import sys
from typing import Dict, Any, List, Tuple

# Patterns for detecting and replacing sensitive data
SENSITIVE_PATTERNS = [
    # Authentication tokens
    (r'Bearer [A-Za-z0-9\-._~+/]+=*', 'Bearer {{API_TOKEN}}'),
    (r'Basic [A-Za-z0-9+/]+=*', 'Basic {{BASIC_AUTH_TOKEN}}'),
    
    # API keys in various formats
    (r'api_key=[A-Za-z0-9\-_]+', 'api_key={{API_KEY}}'),
    (r'apikey=[A-Za-z0-9\-_]+', 'apikey={{API_KEY}}'),
    (r'key=[A-Za-z0-9\-_]{20,}', 'key={{API_KEY}}'),
    
    # Session identifiers
    (r'session=[A-Za-z0-9\-_]+', 'session={{SESSION_ID}}'),
    (r'sessionid=[A-Za-z0-9\-_]+', 'sessionid={{SESSION_ID}}'),
    (r'JSESSIONID=[A-Za-z0-9\-_]+', 'JSESSIONID={{SESSION_ID}}'),
    
    # Tokens and secrets
    (r'token=[A-Za-z0-9\-._~+/]+=*', 'token={{TOKEN}}'),
    (r'access_token=[A-Za-z0-9\-._~+/]+=*', 'access_token={{ACCESS_TOKEN}}'),
    (r'refresh_token=[A-Za-z0-9\-._~+/]+=*', 'refresh_token={{REFRESH_TOKEN}}'),
    
    # Personal information
    (r'"email":\s*"[^"]+@[^"]+"', '"email": "{{USER_EMAIL}}"'),
    (r'"user_id":\s*"?\d+"?', '"user_id": "{{USER_ID}}"'),
    (r'"phone":\s*"[^"]+"', '"phone": "{{PHONE_NUMBER}}"'),
    (r'"password":\s*"[^"]+"', '"password": "{{PASSWORD}}"'),
    
    # Credit card and sensitive numbers
    (r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b', '{{CREDIT_CARD}}'),
    (r'\b\d{3}-\d{2}-\d{4}\b', '{{SSN}}'),
    
    # IP addresses (sometimes sensitive)
    (r'\b(?:\d{1,3}\.){3}\d{1,3}\b', '{{IP_ADDRESS}}'),
    
    # Long hexadecimal strings (likely IDs or tokens)
    (r'\b[a-f0-9]{32,}\b', '{{HEX_ID}}'),
]

# Headers that should be removed or sanitized
SENSITIVE_HEADERS = {
    'authorization': 'Authorization: {{AUTH_HEADER}}',
    'cookie': 'Cookie: {{COOKIES}}',
    'x-api-key': 'X-API-Key: {{API_KEY}}',
    'x-auth-token': 'X-Auth-Token: {{AUTH_TOKEN}}',
    'x-csrf-token': 'X-CSRF-Token: {{CSRF_TOKEN}}',
}

def sanitize_string(text: str, patterns: List[Tuple[str, str]]) -> str:
    """Apply sanitization patterns to a string."""
    if not text:
        return text
    
    for pattern, replacement in patterns:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    return text

def sanitize_headers(headers: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Sanitize request/response headers."""
    sanitized = []
    
    for header in headers:
        name = header.get('name', '').lower()
        value = header.get('value', '')
        
        if name in SENSITIVE_HEADERS:
            # Replace with placeholder
            sanitized.append({
                'name': header['name'],  # Keep original case
                'value': SENSITIVE_HEADERS[name].split(': ', 1)[1]
            })
        elif name.startswith('x-') and ('auth' in name or 'token' in name or 'key' in name):
            # Sanitize custom auth headers
            sanitized.append({
                'name': header['name'],
                'value': '{{CUSTOM_AUTH_HEADER}}'
            })
        else:
            # Apply general sanitization patterns
            sanitized.append({
                'name': header['name'],
                'value': sanitize_string(value, SENSITIVE_PATTERNS)
            })
    
    return sanitized

def sanitize_har_file(har_data: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitize an entire HAR file."""
    sanitized_har = har_data.copy()
    
    # Sanitize each entry
    entries = sanitized_har.get('log', {}).get('entries', [])
    sanitized_entries = []
    
    for entry in entries:
        sanitized_entry = entry.copy()
        
        # Sanitize request
        request = sanitized_entry.get('request', {})
        if 'headers' in request:
            request['headers'] = sanitize_headers(request['headers'])
        if 'url' in request:
            request['url'] = sanitize_string(request['url'], SENSITIVE_PATTERNS)
        if 'queryString' in request:
            for param in request['queryString']:
                param['value'] = sanitize_string(param['value'], SENSITIVE_PATTERNS)
        if 'postData' in request and 'text' in request['postData']:
            request['postData']['text'] = sanitize_string(
                request['postData']['text'], 
                SENSITIVE_PATTERNS
            )
        
        # Sanitize response
        response = sanitized_entry.get('response', {})
        if 'headers' in response:
            response['headers'] = sanitize_headers(response['headers'])
        if 'content' in response and 'text' in response['content']:
            response['content']['text'] = sanitize_string(
                response['content']['text'], 
                SENSITIVE_PATTERNS
            )
        
        sanitized_entries.append(sanitized_entry)
    
    sanitized_har['log']['entries'] = sanitized_entries
    return sanitized_har

def main():
    parser = argparse.ArgumentParser(description='Sanitize HAR files by removing sensitive information')
    parser.add_argument('input_file', help='Input HAR file to sanitize')
    parser.add_argument('output_file', help='Output file for sanitized HAR')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be sanitized without saving')
    
    args = parser.parse_args()
    
    # Load HAR file
    try:
        with open(args.input_file, 'r', encoding='utf-8') as f:
            har_data = json.load(f)
    except Exception as e:
        print(f"❌ Error loading HAR file: {e}")
        sys.exit(1)
    
    # Perform sanitization
    original_count = len(har_data.get('log', {}).get('entries', []))
    sanitized_har = sanitize_har_file(har_data)
    sanitized_count = len(sanitized_har.get('log', {}).get('entries', []))
    
    if args.dry_run:
        print("🔍 DRY RUN - No files will be modified")
        print(f"Original entries: {original_count}")
        print(f"Entries to process: {sanitized_count}")
        print("✅ Sensitive data would be replaced with placeholders")
    else:
        # Save sanitized file
        try:
            with open(args.output_file, 'w', encoding='utf-8') as f:
                json.dump(sanitized_har, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Sanitized HAR file saved to: {args.output_file}")
            print(f"📊 Processed {sanitized_count} entries")
            print("⚠️  IMPORTANT: Review the output file manually for any remaining sensitive data")
            
        except Exception as e:
            print(f"❌ Error saving sanitized file: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()