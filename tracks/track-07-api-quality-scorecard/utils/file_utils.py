"""File I/O utilities for the scorecard."""

import json
import yaml
from pathlib import Path
from typing import Dict, Any, Union
from ..core.exceptions import ParseError


class FileUtils:
    """Utility class for file operations."""
    
    @staticmethod
    def load_yaml_or_json(file_path: Union[str, Path]) -> Dict[str, Any]:
        """Load YAML or JSON file automatically detecting format.
        
        Parameters
        ----------
        file_path : Union[str, Path]
            Path to the file to load.
            
        Returns
        -------
        Dict[str, Any]
            Loaded data structure.
            
        Raises
        ------
        ParseError
            If file cannot be loaded or parsed.
        """
        path = Path(file_path)
        
        if not path.exists():
            raise ParseError(f"File not found: {path}", str(path))
        
        try:
            content = path.read_text(encoding='utf-8')
            
            if path.suffix.lower() in ['.yaml', '.yml']:
                return yaml.safe_load(content)
            elif path.suffix.lower() == '.json':
                return json.loads(content)
            else:
                try:
                    return yaml.safe_load(content)
                except yaml.YAMLError:
                    return json.loads(content)
                    
        except (json.JSONDecodeError, yaml.YAMLError) as e:
            raise ParseError(f"Invalid file format: {e}", str(path))
        except UnicodeDecodeError as e:
            raise ParseError(f"File encoding error: {e}", str(path))
    
    @staticmethod
    def save_json(data: Dict[str, Any], file_path: Union[str, Path], indent: int = 2) -> None:
        """Save data as JSON file.
        
        Parameters
        ----------
        data : Dict[str, Any]
            Data to save.
        file_path : Union[str, Path]
            Path to save file to.
        indent : int, optional
            JSON indentation, by default 2.
        """
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, default=str, ensure_ascii=False)
    
    @staticmethod
    def save_yaml(data: Dict[str, Any], file_path: Union[str, Path]) -> None:
        """Save data as YAML file.
        
        Parameters
        ----------
        data : Dict[str, Any]
            Data to save.
        file_path : Union[str, Path]
            Path to save file to.
        """
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
    
    @staticmethod
    def ensure_directory(dir_path: Union[str, Path]) -> Path:
        """Ensure directory exists, creating it if necessary.
        
        Parameters
        ----------
        dir_path : Union[str, Path]
            Directory path to ensure.
            
        Returns
        -------
        Path
            Path object for the directory.
        """
        path = Path(dir_path)
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @staticmethod
    def get_file_size_mb(file_path: Union[str, Path]) -> float:
        """Get file size in megabytes.
        
        Parameters
        ----------
        file_path : Union[str, Path]
            Path to the file.
            
        Returns
        -------
        float
            File size in MB.
        """
        path = Path(file_path)
        if not path.exists():
            return 0.0
        
        return path.stat().st_size / (1024 * 1024)
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Check if string is a valid URL.
        
        Parameters
        ----------
        url : str
            URL string to validate.
            
        Returns
        -------
        bool
            True if valid URL, False otherwise.
        """
        from urllib.parse import urlparse
        
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False