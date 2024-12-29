# core/tool_registry.py
import logging
from typing import Dict, Optional
from .base_tool import BaseTool

logger = logging.getLogger(__name__)

class ToolRegistrationError(Exception):
    pass

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}

    async def register_tool(self, name: str, tool: BaseTool):
        # Example health check call
        if not await tool.health_check():
            logger.error(f"Tool {name} failed health check.")
            raise ToolRegistrationError(f"Tool {name} failed health check.")
        self._tools[name] = tool
        logger.info(f"Successfully registered tool: {name}")

    async def get_tool(self, name: str) -> Optional[BaseTool]:
        tool = self._tools.get(name)
        # Optionally re-check health if needed:
        # if tool and not await tool.health_check():
        #     return None
        return tool

    def list_tools(self) -> Dict[str, Dict]:
        """
        Returns a summary of all registered tools.
        """
        return {
            name: {
                "capabilities": tool.capabilities,
                "schema": tool.get_schema()
            }
            for name, tool in self._tools.items()
        }
        
