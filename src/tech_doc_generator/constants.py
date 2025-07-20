"""
Constants for the Technology Document Generator application.

This module contains all application-wide constants to improve maintainability
and avoid magic numbers/strings throughout the codebase.
"""

from typing import Final

# LLM Configuration
DEFAULT_LLM_MODEL: Final[str] = "gpt-4.1-nano"
DEFAULT_MAX_TOKENS: Final[int] = 2000
DEFAULT_DOCUMENT_MAX_TOKENS: Final[int] = 4000
DEFAULT_TEMPERATURE: Final[float] = 0.7

# Search Configuration
DEFAULT_MAX_SEARCH_RESULTS: Final[int] = 3
SEARCH_REQUEST_TIMEOUT: Final[int] = 10
SEARCH_DELAY_BETWEEN_QUERIES: Final[float] = 1.0

# Document Generation
MIN_DOCUMENT_LENGTH: Final[int] = 100
MAX_TECHNOLOGIES_PER_REQUEST: Final[int] = 10

# Retry Configuration
DEFAULT_RETRY_SETTINGS: Final[dict] = {
    'prepare': 1,
    'outline': 2,
    'research': 2,
    'merge': 1,
    'write': 3
}

DEFAULT_WAIT_TIMES: Final[dict] = {
    'prepare': 1,
    'outline': 1,
    'research': 2,
    'merge': 1,
    'write': 1
}

# Flow Configuration
DEFAULT_TIMEOUT_SECONDS: Final[int] = 120

# Logging
DEFAULT_LOG_LEVEL: Final[str] = "INFO"

# File Extensions
MARKDOWN_EXTENSION: Final[str] = ".md"
YAML_EXTENSION: Final[str] = ".yaml"

# API Headers
DEFAULT_USER_AGENT: Final[str] = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
)

# Search URLs
DUCKDUCKGO_SEARCH_URL: Final[str] = "https://duckduckgo.com/html/"
