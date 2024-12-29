# tools/web_api_tool.py
import logging
import aiohttp
from typing import Any, Dict
from pydantic import BaseModel
from core.base_tool import BaseTool, ToolParameters
import urllib.parse

logger = logging.getLogger(__name__)

class WebAPIToolParameters(ToolParameters):
    url: str               # Full, absolute URL (e.g. "https://example.com/foo")
    method: str = "GET"    # "GET", "POST", "PUT", "DELETE", etc.
    headers: Dict[str, str] = {}
    body: Dict[str, Any] = {}

class WebAPITool(BaseTool):
    """
    A generic tool that can make HTTP requests to any fully qualified URL.
    """
    parameters_class = WebAPIToolParameters

    async def execute(self, params: WebAPIToolParameters) -> Any:
        logger.info(f"Executing WebAPITool request: {params.method} {params.url}")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method=params.method,
                    url=params.url,
                    headers=params.headers,
                    json=params.body
                ) as response:
                    # Raise aiohttp.ClientResponseError on 4xx/5xx
                    response.raise_for_status()
                    return await response.json()
        except aiohttp.ClientError as e:
            logger.error(f"HTTP request failed: {e}", exc_info=True)
            return {"error": str(e)}

    async def validate(self, params: WebAPIToolParameters) -> bool:
        """
        Validate that `url` is a FULLY QUALIFIED URL.
        (Has scheme and netloc.)
        """
        try:
            parsed = urllib.parse.urlparse(params.url)
            return bool(parsed.scheme and parsed.netloc)
        except Exception as e:
            logger.error(f"Validation failed: {e}", exc_info=True)
            return False

    def get_schema(self) -> Dict[str, Any]:
        return self.parameters_class.schema()

    async def health_check(self) -> bool:
        """
        Minimal 'health check'—just say True for now or try
        a HEAD request to see if the domain is reachable.
        """
        # For a truly generic tool, we can't guess a single URL to check,
        # so let's just say "always healthy" or do something minimal.
        return True

    @property
    def capabilities(self) -> Dict[str, Any]:
        return {
            "requires_network": True,
            "async_compatible": True,
            "tool_type": "web_api_generic"
        }
