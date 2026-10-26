"""
GhostShell Configuration

All settings are configurable via environment variables.
No secrets are hardcoded. No remote AI services are used.
"""

import os


# Ollama settings
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2")
# Number of GPU layers to offload (-1: Ollama auto, 0: CPU only, >0: specific layers)
# Default to 0 (CPU) for cross-platform stability and to avoid Vulkan crashes on integrated graphics
OLLAMA_NUM_GPU = int(os.environ.get("OLLAMA_NUM_GPU", "0"))

# Flask settings
FLASK_HOST = os.environ.get("FLASK_HOST", "127.0.0.1")
FLASK_PORT = int(os.environ.get("FLASK_PORT", "5000"))
FLASK_DEBUG = os.environ.get("FLASK_DEBUG", "false").lower() in ("true", "1", "yes")

# Input validation limits
MAX_COMMAND_LENGTH = 500
MAX_THEME_LENGTH = 300

# Context window size (reduced from default 4096 to 1024 for speed & low memory footprint on CPU)
OLLAMA_NUM_CTX = int(os.environ.get("OLLAMA_NUM_CTX", "1024"))

# Max tokens to generate per response (prevents runaway generation on CPU)
OLLAMA_MAX_TOKENS = int(os.environ.get("OLLAMA_MAX_TOKENS", "140"))

# Ollama request timeout (seconds) — generous cushion for local CPU inference
OLLAMA_TIMEOUT = int(os.environ.get("OLLAMA_TIMEOUT", "180"))
