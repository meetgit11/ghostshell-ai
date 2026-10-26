"""
Tests for GhostShell configuration.
"""

import os
from unittest.mock import patch


class TestConfig:
    def test_default_values(self):
        """Config should have sensible defaults when no env vars are set."""
        import importlib
        import config
        importlib.reload(config)

        assert config.OLLAMA_HOST == "http://localhost:11434"
        assert config.OLLAMA_MODEL == "llama3.2"
        assert config.FLASK_HOST == "127.0.0.1"
        assert config.FLASK_PORT == 5000
        assert config.FLASK_DEBUG is False
        assert config.MAX_COMMAND_LENGTH > 0
        assert config.MAX_THEME_LENGTH > 0
        assert config.OLLAMA_TIMEOUT >= 180
        assert config.OLLAMA_NUM_GPU == 0
        assert config.OLLAMA_NUM_CTX == 1024
        assert config.OLLAMA_MAX_TOKENS == 140

    @patch.dict(os.environ, {
        "OLLAMA_HOST": "http://myhost:9999",
        "OLLAMA_MODEL": "phi3",
        "OLLAMA_NUM_GPU": "2",
        "OLLAMA_NUM_CTX": "512",
        "OLLAMA_MAX_TOKENS": "100",
        "OLLAMA_TIMEOUT": "240",
        "FLASK_HOST": "0.0.0.0",
        "FLASK_PORT": "8080",
        "FLASK_DEBUG": "true",
    })
    def test_env_var_overrides(self):
        """Config should respect environment variable overrides."""
        import importlib
        import config
        importlib.reload(config)

        assert config.OLLAMA_HOST == "http://myhost:9999"
        assert config.OLLAMA_MODEL == "phi3"
        assert config.OLLAMA_NUM_GPU == 2
        assert config.OLLAMA_NUM_CTX == 512
        assert config.OLLAMA_MAX_TOKENS == 100
        assert config.OLLAMA_TIMEOUT == 240
        assert config.FLASK_HOST == "0.0.0.0"
        assert config.FLASK_PORT == 8080
        assert config.FLASK_DEBUG is True

    def test_debug_mode_default_off(self):
        """Debug mode must be OFF by default for production safety."""
        import importlib
        import config
        importlib.reload(config)
        assert config.FLASK_DEBUG is False
