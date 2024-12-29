# core/base_tool.py
from abc import ABC, abstractmethod
from typing import Any, Dict
from pydantic import BaseModel

class ToolParameters(BaseModel):
    """
    Base class for tool parameters.
    Subclasses will define specific fields as needed.
    """
    class Config:
        extra = "forbid"  # Disallow extra fields to keep strict validation


class BaseTool(ABC):
    """
    An abstract base class defining the core interface for all tools.
    """

    @abstractmethod
    async def execute(self, params: ToolParameters) -> Any:
        """
        Execute the tool with given parameters.
        Must be implemented in each derived tool.
        """
        pass

    @abstractmethod
    async def validate(self, params: ToolParameters) -> bool:
        """
        Validate the given parameters before execution.
        """
        pass

    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """
        Return the JSON schema of the parameters for documentation.
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """
        Return True if the tool is available/working, otherwise False.
        """
        pass

    @property
    @abstractmethod
    def capabilities(self) -> Dict[str, Any]:
        """
        Return a dictionary describing the tool's capabilities.
        Could include 'requires_network', 'async_compatible', etc.
        """
        pass
