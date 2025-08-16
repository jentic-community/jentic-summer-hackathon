"""Main OpenAPI specification parser with validation and data extraction."""

import json
import yaml
from pathlib import Path
from typing import Dict, Any, Union
from urllib.parse import urlparse
import requests

from core.models import OpenAPISpec
from core.exceptions import ParseError, ValidationError
from core.types import OpenAPIVersion
from config.settings import get_settings
from parser.validator import SpecValidator
from parser.extractor import DataExtractor


class OpenAPIParser:
    """Parser for OpenAPI specifications with validation and data extraction.
    
    Supports loading from local files or remote URLs, validates the specification
    structure, and extracts data into structured models for analysis.
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.validator = SpecValidator()
        self.extractor = DataExtractor()
    
    def load(self, spec_path: Union[str, Path]) -> OpenAPISpec:
        """Load and parse OpenAPI specification from file or URL.
        
        Parameters
        ----------
        spec_path : Union[str, Path]
            Path to local file or URL to remote specification.
            
        Returns
        -------
        OpenAPISpec
            Parsed and validated OpenAPI specification data.
            
        Raises
        ------
        ParseError
            If the specification cannot be loaded or parsed.
        ValidationError
            If the specification structure is invalid.
        """
        spec_str = str(spec_path)
        
        try:
            if self._is_url(spec_str):
                raw_spec = self._load_from_url(spec_str)
            else:
                raw_spec = self._load_from_file(Path(spec_str))
            
            self.validator.validate(raw_spec)
            
            return self.extractor.extract(raw_spec)
            
        except (json.JSONDecodeError, yaml.YAMLError) as e:
            raise ParseError(f"Failed to parse specification: {e}", spec_str)
        except requests.RequestException as e:
            raise ParseError(f"Failed to fetch remote specification: {e}", spec_str)
        except Exception as e:
            raise ParseError(f"Unexpected error parsing specification: {e}", spec_str)
    
    def _is_url(self, spec_path: str) -> bool:
        """Check if the path is a URL.
        
        Parameters
        ----------
        spec_path : str
            Path to check.
            
        Returns
        -------
        bool
            True if the path is a URL, False otherwise.
        """
        try:
            result = urlparse(spec_path)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    def _load_from_file(self, file_path: Path) -> Dict[str, Any]:
        """Load specification from local file.
        
        Parameters
        ----------
        file_path : Path
            Path to the specification file.
            
        Returns
        -------
        Dict[str, Any]
            Raw specification data.
            
        Raises
        ------
        ParseError
            If file cannot be read or parsed.
        """
        if not file_path.exists():
            raise ParseError(f"File not found: {file_path}", str(file_path))
        
        if not file_path.is_file():
            raise ParseError(f"Path is not a file: {file_path}", str(file_path))
        
        file_size_mb = file_path.stat().st_size / (1024 * 1024)
        if file_size_mb > self.settings.max_spec_size_mb:
            raise ParseError(
                f"File too large: {file_size_mb:.1f}MB (max: {self.settings.max_spec_size_mb}MB)",
                str(file_path)
            )
        
        try:
            content = file_path.read_text(encoding='utf-8')
            
            if file_path.suffix.lower() in ['.yaml', '.yml']:
                return yaml.safe_load(content)
            elif file_path.suffix.lower() == '.json':
                return json.loads(content)
            else:
                try:
                    return yaml.safe_load(content)
                except yaml.YAMLError:
                    return json.loads(content)
                    
        except UnicodeDecodeError as e:
            raise ParseError(f"File encoding error: {e}", str(file_path))
        except (json.JSONDecodeError, yaml.YAMLError) as e:
            raise ParseError(f"Invalid format: {e}", str(file_path))
    
    def _load_from_url(self, url: str) -> Dict[str, Any]:
        """Load specification from remote URL.
        
        Parameters
        ----------
        url : str
            URL to the specification.
            
        Returns
        -------
        Dict[str, Any]
            Raw specification data.
            
        Raises
        ------
        ParseError
            If URL cannot be fetched or parsed.
        """
        if not self.settings.enable_remote_specs:
            raise ParseError("Remote specification loading is disabled", url)
        
        try:
            response = requests.get(
                url,
                timeout=self.settings.request_timeout,
                headers={'Accept': 'application/json, application/yaml, text/yaml'}
            )
            response.raise_for_status()
            
            content_length = len(response.content)
            max_size_bytes = self.settings.max_spec_size_mb * 1024 * 1024
            if content_length > max_size_bytes:
                raise ParseError(
                    f"Response too large: {content_length / (1024*1024):.1f}MB "
                    f"(max: {self.settings.max_spec_size_mb}MB)",
                    url
                )
            
            content_type = response.headers.get('content-type', '').lower()
            
            if 'json' in content_type:
                return response.json()
            elif any(t in content_type for t in ['yaml', 'yml']):
                return yaml.safe_load(response.text)
            else:
                try:
                    return response.json()
                except json.JSONDecodeError:
                    return yaml.safe_load(response.text)
                    
        except requests.RequestException as e:
            raise ParseError(f"Failed to fetch URL: {e}", url)
        except (json.JSONDecodeError, yaml.YAMLError) as e:
            raise ParseError(f"Invalid response format: {e}", url)
    
    def get_openapi_version(self, raw_spec: Dict[str, Any]) -> OpenAPIVersion:
        """Extract OpenAPI version from raw specification.
        
        Parameters
        ----------
        raw_spec : Dict[str, Any]
            Raw specification data.
            
        Returns
        -------
        OpenAPIVersion
            Detected OpenAPI version.
            
        Raises
        ------
        ValidationError
            If version cannot be determined or is unsupported.
        """
        if 'openapi' in raw_spec:
            version_str = str(raw_spec['openapi'])
            if version_str.startswith('3.0'):
                return OpenAPIVersion.V3_0
            elif version_str.startswith('3.1'):
                return OpenAPIVersion.V3_1
            else:
                raise ValidationError(f"Unsupported OpenAPI version: {version_str}")
        elif 'swagger' in raw_spec:
            raise ValidationError("Swagger 2.0 specifications are not supported")
        else:
            raise ValidationError("Cannot determine OpenAPI version")