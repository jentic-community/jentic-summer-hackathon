"""Application settings and configuration management."""

from functools import lru_cache
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class ScorecardSettings(BaseSettings):
    """Main application settings with environment variable support."""
    
    debug: bool = Field(False, env="SCORECARD_DEBUG")
    log_level: str = Field("INFO", env="SCORECARD_LOG_LEVEL")
    
    default_output_format: str = Field("html", env="SCORECARD_OUTPUT_FORMAT")
    default_threshold: int = Field(70, env="SCORECARD_THRESHOLD")
    
    enable_remote_specs: bool = Field(True, env="SCORECARD_ENABLE_REMOTE")
    request_timeout: int = Field(30, env="SCORECARD_REQUEST_TIMEOUT")
    max_spec_size_mb: int = Field(10, env="SCORECARD_MAX_SPEC_SIZE")
    
    cache_enabled: bool = Field(True, env="SCORECARD_CACHE_ENABLED")
    cache_ttl_seconds: int = Field(3600, env="SCORECARD_CACHE_TTL")
    
    report_template_dir: Optional[Path] = Field(None, env="SCORECARD_TEMPLATE_DIR")
    output_dir: Optional[Path] = Field(None, env="SCORECARD_OUTPUT_DIR")
    
    min_description_length: int = Field(10, env="SCORECARD_MIN_DESC_LENGTH")
    good_description_length: int = Field(50, env="SCORECARD_GOOD_DESC_LENGTH")
    max_parameters_per_operation: int = Field(10, env="SCORECARD_MAX_PARAMS")
    min_error_status_codes: int = Field(3, env="SCORECARD_MIN_ERROR_CODES")
    
    documentation_weight: float = Field(0.25, env="SCORECARD_DOC_WEIGHT")
    schemas_weight: float = Field(0.25, env="SCORECARD_SCHEMA_WEIGHT")
    errors_weight: float = Field(0.20, env="SCORECARD_ERROR_WEIGHT")
    usability_weight: float = Field(0.20, env="SCORECARD_USABILITY_WEIGHT")
    authentication_weight: float = Field(0.10, env="SCORECARD_AUTH_WEIGHT")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"
        
    def get_template_dir(self) -> Path:
        """Get template directory path, with fallback to default."""
        if self.report_template_dir and self.report_template_dir.exists():
            return self.report_template_dir
        return Path(__file__).parent.parent / "reporting" / "templates"
    
    def get_output_dir(self) -> Path:
        """Get output directory path, with fallback to current directory."""
        if self.output_dir:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            return self.output_dir
        return Path.cwd()
    
    def validate_weights(self) -> bool:
        """Validate that category weights sum to 1.0."""
        total = (
            self.documentation_weight +
            self.schemas_weight +
            self.errors_weight +
            self.usability_weight +
            self.authentication_weight
        )
        return abs(total - 1.0) < 0.001


@lru_cache()
def get_settings() -> ScorecardSettings:
    """Get cached application settings instance.
    
    Returns
    -------
    ScorecardSettings
        Configured settings instance with environment variables loaded.
    """
    return ScorecardSettings()