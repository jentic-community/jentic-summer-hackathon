"""Configuration management for Discord Bot using Pydantic."""

import os
from typing import Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class BotConfig(BaseSettings):
    """Bot configuration with validation using Pydantic.

    Attributes
    ----------
    discord_bot_token : str
        Discord bot token for authentication.
    bot_prefix : str
        Command prefix for the bot (default: "!").
    bot_description : str
        Description of the bot.
    jentic_agent_api_key : str
        Jentic Agent API key for Standard Agent access.
    openai_api_key : Optional[str]
        OpenAI API key for GPT models.
    anthropic_api_key : Optional[str]
        Anthropic API key for Claude models.
    gemini_api_key : Optional[str]
        Google Gemini API key.
    llm_model : str
        Default LLM model to use (default: "gpt-4").
    log_level : str
        Logging level (default: "INFO").
    log_format : str
        Log format string.
    log_date_format : str
        Log date format string.
    command_timeout : int
        Command timeout in seconds (default: 30).
    max_message_length : int
        Maximum message length (default: 2000).
    enable_dm_commands : bool
        Enable commands in DMs (default: True).
    """

    discord_bot_token: str = Field(..., description="Discord bot token")
    bot_prefix: str = Field(default="!", description="Command prefix for the bot")
    bot_description: str = Field(
        default="AI Agent Discord Bot powered by Standard Agent and Jentic",
        description="Bot description",
    )

    jentic_agent_api_key: str = Field(..., description="Jentic Agent API key")

    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    anthropic_api_key: Optional[str] = Field(default=None, description="Anthropic API key")
    gemini_api_key: Optional[str] = Field(default=None, description="Gemini API key")
    llm_model: str = Field(default="gpt-4", description="Default LLM model to use")

    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format string",
    )
    log_date_format: str = Field(default="%Y-%m-%d %H:%M:%S", description="Log date format")

    command_timeout: int = Field(default=30, description="Command timeout in seconds")
    max_message_length: int = Field(default=2000, description="Maximum message length")
    enable_dm_commands: bool = Field(default=True, description="Enable commands in DMs")

    model_config = {
        "env_file": os.path.join(os.path.dirname(__file__), ".env"),
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }

    @field_validator("bot_prefix")
    @classmethod
    def validate_prefix(cls, v):
        """Validate bot prefix.

        Parameters
        ----------
        v : str
            The prefix value to validate.

        Returns
        -------
        str
            The validated prefix.

        Raises
        ------
        ValueError
            If prefix is empty or longer than 5 characters.
        """
        if not v or len(v) > 5:
            raise ValueError("Bot prefix must be 1-5 characters long")
        return v

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v):
        """Validate log level.

        Parameters
        ----------
        v : str
            The log level to validate.

        Returns
        -------
        str
            The validated log level in uppercase.

        Raises
        ------
        ValueError
            If log level is not valid.
        """
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of: {', '.join(valid_levels)}")
        return v.upper()

    @field_validator("llm_model")
    @classmethod
    def validate_llm_model(cls, v):
        """Validate LLM model.

        Parameters
        ----------
        v : str
            The model name to validate.

        Returns
        -------
        str
            The validated model name.
        """
        valid_models = [
            "gpt-4",
            "gpt-4-turbo",
            "gpt-3.5-turbo",
            "claude-3-opus",
            "claude-3-sonnet",
            "claude-3-haiku",
            "gemini-pro",
            "gemini-pro-vision",
        ]
        if v not in valid_models:
            pass
        return v

    def validate_llm_keys(self) -> bool:
        """Validate that at least one LLM API key is provided.

        Returns
        -------
        bool
            True if validation passes.

        Raises
        ------
        ValueError
            If no LLM API keys are provided.
        """
        llm_keys = [self.openai_api_key, self.anthropic_api_key, self.gemini_api_key]
        if not any(llm_keys):
            raise ValueError("At least one LLM API key must be provided")
        return True

    def get_active_llm_provider(self) -> Optional[str]:
        """Get the active LLM provider based on available keys.

        Returns
        -------
        Optional[str]
            The active provider name ('openai', 'anthropic', 'gemini') or None.
        """
        if self.openai_api_key and self.llm_model.startswith("gpt"):
            return "openai"
        elif self.anthropic_api_key and self.llm_model.startswith("claude"):
            return "anthropic"
        elif self.gemini_api_key and self.llm_model.startswith("gemini"):
            return "gemini"
        elif self.openai_api_key:
            return "openai"
        elif self.anthropic_api_key:
            return "anthropic"
        elif self.gemini_api_key:
            return "gemini"
        return None


def load_config() -> BotConfig:
    """Load and validate configuration.

    Returns
    -------
    BotConfig
        The loaded and validated configuration.

    Raises
    ------
    ValueError
        If configuration loading or validation fails.
    """
    try:
        config = BotConfig()
        config.validate_llm_keys()
        return config
    except Exception as e:
        raise ValueError(f"Configuration error: {e}")


def get_config() -> BotConfig:
    """Get singleton configuration instance.

    Returns
    -------
    BotConfig
        The singleton configuration instance.
    """
    if not hasattr(get_config, "_config"):
        get_config._config = load_config()
    return get_config._config


__all__ = ["BotConfig", "load_config", "get_config"]
