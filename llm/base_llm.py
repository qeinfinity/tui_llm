# llm/base_llm.py
from abc import ABC, abstractmethod
from typing import Any, Optional, Dict
from pydantic import BaseModel, Field, validator

class LLMConfig(BaseModel):
    """
    Configuration for a generic LLM backend.
    Extend or override fields as needed for each provider.
    """
    api_key: str = Field(..., description="API key for the LLM provider")
    endpoint: str = Field(..., description="Base URL/endpoint for the API")
    model: str = Field(..., description="Model name or identifier")
    temperature: float = Field(0.7, ge=0, le=2, description="Sampling temperature")
    max_tokens: int = Field(512, ge=1, description="Max tokens in the response")

    # If you have provider-specific fields, you can include them here
    # or define a separate specialized config model that inherits from LLMConfig.

    @validator("api_key")
    def ensure_api_key_not_empty(cls, value):
        if not value.strip():
            raise ValueError("API key must not be empty.")
        return value

class BaseLLM(ABC):
    """
    Abstract base class defining the interface for calling LLMs.
    """

    def __init__(self, config: LLMConfig):
        self.config = config

    @abstractmethod
    async def generate_text(self, prompt: str) -> str:
        """
        Send a prompt to the LLM and return the generated text.
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """
        Verify LLM availability (e.g., a quick test call).
        """
        pass
