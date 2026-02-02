"""
Nurture - Utils Module
======================

Utility functions and helpers including LLM integration.

Supported LLM Providers:
- Groq (FREE & ultra-fast - recommended!)
- OpenAI
- Ollama (local)
- Mock (testing)
"""

from nurture.utils.logger import Logger, get_logger
from nurture.utils.helpers import clamp, normalize_scores
from nurture.utils.llm_interface import (
    LLMConfig,
    LLMInterface,
    MockLLM,
    OpenAILLM,
    LocalLLM,
    GroqLLM,
    LLMFactory,
    create_llm_generator,
)

__all__ = [
    "Logger",
    "get_logger",
    "clamp",
    "normalize_scores",
    "LLMConfig",
    "LLMInterface",
    "MockLLM",
    "OpenAILLM",
    "LocalLLM",
    "GroqLLM",
    "LLMFactory",
    "create_llm_generator",
]

