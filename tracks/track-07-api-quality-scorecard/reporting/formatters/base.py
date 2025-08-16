"""Base formatter class for report generation."""

from abc import ABC, abstractmethod
from typing import Dict, Any
from core.models import ScoringResult


class BaseFormatter(ABC):
    """Abstract base class for all report formatters."""
    
    def __init__(self):
        self.template_vars = {}
    
    @abstractmethod
    def format(self, result: ScoringResult, detailed: bool = False) -> str:
        """Format scoring result into specific output format.
        
        Parameters
        ----------
        result : ScoringResult
            Scoring result to format.
        detailed : bool, optional
            Whether to include detailed information, by default False.
            
        Returns
        -------
        str
            Formatted report content.
        """
        pass
    
    @abstractmethod
    def get_file_extension(self) -> str:
        """Get file extension for this format.
        
        Returns
        -------
        str
            File extension (e.g., 'html', 'json', 'md').
        """
        pass
    
    @abstractmethod
    def get_content_type(self) -> str:
        """Get MIME content type for this format.
        
        Returns
        -------
        str
            MIME content type.
        """
        pass
    
    def prepare_template_vars(self, result: ScoringResult, detailed: bool = False) -> Dict[str, Any]:
        """Prepare template variables for rendering.
        
        Parameters
        ----------
        result : ScoringResult
            Scoring result to extract data from.
        detailed : bool, optional
            Whether to include detailed information, by default False.
            
        Returns
        -------
        Dict[str, Any]
            Template variables dictionary.
        """
        vars_dict = {
            'result': result,
            'overall_score': result.overall_score,
            'quality_grade': result.quality_grade,
            'category_scores': result.category_scores,
            'metrics': result.metrics,
            'recommendations': result.recommendations,
            'analysis_timestamp': result.analysis_timestamp,
            'spec_info': result.spec_info,
            'critical_issues': result.critical_issues_count,
            'high_issues': result.high_issues_count,
            'detailed': detailed
        }
        
        vars_dict.update({
            'documentation_score': result.category_scores.documentation,
            'schemas_score': result.category_scores.schemas,
            'errors_score': result.category_scores.errors,
            'usability_score': result.category_scores.usability,
            'authentication_score': result.category_scores.authentication
        })
        
        vars_dict.update({
            'documentation_percentage': (result.category_scores.documentation / 25) * 100,
            'schemas_percentage': (result.category_scores.schemas / 25) * 100,
            'errors_percentage': (result.category_scores.errors / 20) * 100,
            'usability_percentage': (result.category_scores.usability / 20) * 100,
            'authentication_percentage': (result.category_scores.authentication / 10) * 100
        })
        
        if detailed and 'category_details' in result.spec_info:
            vars_dict['category_details'] = result.spec_info['category_details']
        
        return vars_dict
    
    def get_score_color(self, score: int, max_score: int) -> str:
        """Get color class/code based on score percentage.
        
        Parameters
        ----------
        score : int
            Actual score.
        max_score : int
            Maximum possible score.
            
        Returns
        -------
        str
            Color identifier (success, warning, danger, etc.).
        """
        if max_score == 0:
            return 'success'
        
        percentage = (score / max_score) * 100
        
        if percentage >= 80:
            return 'success'
        elif percentage >= 60:
            return 'warning'
        else:
            return 'danger'
    
    def get_severity_color(self, severity: str) -> str:
        """Get color for recommendation severity.
        
        Parameters
        ----------
        severity : str
            Severity level.
            
        Returns
        -------
        str
            Color identifier.
        """
        severity_colors = {
            'critical': 'danger',
            'high': 'danger',
            'medium': 'warning',
            'low': 'info',
            'info': 'secondary'
        }
        return severity_colors.get(severity.lower(), 'secondary')
    
    def format_timestamp(self, timestamp) -> str:
        """Format timestamp for display.
        
        Parameters
        ----------
        timestamp : datetime
            Timestamp to format.
            
        Returns
        -------
        str
            Formatted timestamp string.
        """
        return timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')
    
    def truncate_text(self, text: str, max_length: int = 100) -> str:
        """Truncate text to specified length.
        
        Parameters
        ----------
        text : str
            Text to truncate.
        max_length : int, optional
            Maximum length, by default 100.
            
        Returns
        -------
        str
            Truncated text with ellipsis if needed.
        """
        if not text or len(text) <= max_length:
            return text
        
        return text[:max_length - 3] + '...'