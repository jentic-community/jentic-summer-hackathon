"""
Tests for the bot configuration module.
"""

import os
import pytest
from unittest.mock import patch, MagicMock
from pydantic import ValidationError

from config import BotConfig, load_config, get_config


class TestBotConfig:
    """Test cases for BotConfig class."""
    
    def test_config_with_valid_data(self):
        """Test configuration with valid data."""
        config_data = {
            'discord_bot_token': 'test_token_123',
            'jentic_agent_api_key': 'test_jentic_key',
            'openai_api_key': 'test_openai_key',
            'bot_prefix': '!',
            'bot_description': 'Test bot',
            'llm_model': 'gpt-4',
            'log_level': 'INFO'
        }
        
        config = BotConfig(**config_data)
        
        assert config.discord_bot_token == 'test_token_123'
        assert config.jentic_agent_api_key == 'test_jentic_key'
        assert config.openai_api_key == 'test_openai_key'
        assert config.bot_prefix == '!'
        assert config.llm_model == 'gpt-4'
        assert config.log_level == 'INFO'
    
    def test_config_missing_required_fields(self):
        """Test configuration with missing required fields."""
        # Clear environment variables to ensure validation fails
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValidationError):
                BotConfig()
    
    def test_config_invalid_prefix(self):
        """Test configuration with invalid prefix."""
        config_data = {
            'discord_bot_token': 'test_token',
            'jentic_agent_api_key': 'test_key',
            'openai_api_key': 'test_openai',
            'bot_prefix': '!!!!!!',  # Too long
        }
        
        with pytest.raises(ValidationError):
            BotConfig(**config_data)
    
    def test_config_invalid_log_level(self):
        """Test configuration with invalid log level."""
        config_data = {
            'discord_bot_token': 'test_token',
            'jentic_agent_api_key': 'test_key',
            'openai_api_key': 'test_openai',
            'log_level': 'INVALID_LEVEL'
        }
        
        with pytest.raises(ValidationError):
            BotConfig(**config_data)
    
    def test_config_defaults(self):
        """Test configuration default values."""
        config_data = {
            'discord_bot_token': 'test_token',
            'jentic_agent_api_key': 'test_key',
            'openai_api_key': 'test_openai'
        }
        
        config = BotConfig(**config_data)
        
        assert config.bot_prefix == '!'
        assert config.llm_model == 'gpt-4'
        assert config.log_level == 'INFO'
        assert config.command_timeout == 30
        assert config.enable_dm_commands is True
    
    def test_get_active_llm_provider_openai(self):
        """Test getting active LLM provider for OpenAI."""
        config_data = {
            'discord_bot_token': 'test_token',
            'jentic_agent_api_key': 'test_key',
            'openai_api_key': 'test_openai',
            'llm_model': 'gpt-4'
        }
        
        config = BotConfig(**config_data)
        assert config.get_active_llm_provider() == 'openai'
    
    def test_get_active_llm_provider_anthropic(self):
        """Test getting active LLM provider for Anthropic."""
        config_data = {
            'discord_bot_token': 'test_token',
            'jentic_agent_api_key': 'test_key',
            'anthropic_api_key': 'test_anthropic',
            'llm_model': 'claude-3-opus'
        }
        
        config = BotConfig(**config_data)
        assert config.get_active_llm_provider() == 'anthropic'
    
    def test_get_active_llm_provider_gemini(self):
        """Test getting active LLM provider for Gemini."""
        config_data = {
            'discord_bot_token': 'test_token',
            'jentic_agent_api_key': 'test_key',
            'gemini_api_key': 'test_gemini',
            'llm_model': 'gemini-pro'
        }
        
        config = BotConfig(**config_data)
        assert config.get_active_llm_provider() == 'gemini'
    
    def test_get_active_llm_provider_none(self):
        """Test getting active LLM provider when none available."""
        # Clear environment variables to ensure no API keys are loaded
        with patch.dict(os.environ, {}, clear=True):
            config_data = {
                'discord_bot_token': 'test_token',
                'jentic_agent_api_key': 'test_key'
            }
            
            config = BotConfig(**config_data)
            assert config.get_active_llm_provider() is None
    
    def test_validate_llm_keys_success(self):
        """Test LLM key validation success."""
        config_data = {
            'discord_bot_token': 'test_token',
            'jentic_agent_api_key': 'test_key',
            'openai_api_key': 'test_openai'
        }
        
        config = BotConfig(**config_data)
        assert config.validate_llm_keys() is True
    
    def test_validate_llm_keys_failure(self):
        """Test LLM key validation failure."""
        # Clear environment variables to ensure no API keys are loaded
        with patch.dict(os.environ, {}, clear=True):
            config_data = {
                'discord_bot_token': 'test_token',
                'jentic_agent_api_key': 'test_key'
            }
            
            config = BotConfig(**config_data)
            with pytest.raises(ValueError, match="At least one LLM API key must be provided"):
                config.validate_llm_keys()


class TestConfigLoading:
    """Test cases for configuration loading functions."""
    
    @patch.dict(os.environ, {
        'DISCORD_BOT_TOKEN': 'test_discord_token',
        'JENTIC_AGENT_API_KEY': 'test_jentic_key',
        'OPENAI_API_KEY': 'test_openai_key',
        'BOT_PREFIX': '!',
        'LLM_MODEL': 'gpt-4'
    })
    def test_load_config_from_env(self):
        """Test loading configuration from environment variables."""
        config = load_config()
        
        assert config.discord_bot_token == 'test_discord_token'
        assert config.jentic_agent_api_key == 'test_jentic_key'
        assert config.openai_api_key == 'test_openai_key'
        assert config.bot_prefix == '!'
        assert config.llm_model == 'gpt-4'
    
    @patch.dict(os.environ, {
        'DISCORD_BOT_TOKEN': 'test_token',
        'JENTIC_AGENT_API_KEY': 'test_key'
    }, clear=True)
    def test_load_config_missing_llm_key(self):
        """Test loading configuration with missing LLM key."""
        with pytest.raises(ValueError, match="Configuration error"):
            load_config()
    
    @patch('config.load_config')
    def test_get_config_singleton(self, mock_load_config):
        """Test that get_config returns singleton instance."""
        mock_config = MagicMock()
        mock_load_config.return_value = mock_config
        
        # Clear any existing cached config
        if hasattr(get_config, '_config'):
            delattr(get_config, '_config')
        
        # First call should load config
        config1 = get_config()
        assert config1 == mock_config
        assert mock_load_config.call_count == 1
        
        # Second call should return cached config
        config2 = get_config()
        assert config2 == mock_config
        assert config2 is config1
        assert mock_load_config.call_count == 1  # Should not be called again


if __name__ == '__main__':
    pytest.main([__file__])