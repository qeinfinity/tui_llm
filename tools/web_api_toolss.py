# tools/web_api_tool.py
import logging
import aiohttp
import urllib.parse
from typing import Any, Dict
from pydantic import BaseModel
from core.base_tool import BaseTool, ToolParameters

logger = logging.getLogger(__name__)

class WebAPIToolParameters(ToolParameters):
    url: str
    method: str = "GET"
    headers: Dict[str, str] = {}
    body: Dict[str, Any] = {}

class WebAPITool(BaseTool):
    # Optional: a class-level reference to parameters for convenience
    parameters_class = WebAPIToolParameters

    def __init__(self, base_url: str = ""):
        self.base_url = base_url

    async def execute(self, params: WebAPIToolParameters) -> Any:
        """
        Makes an HTTP request to the specified URL (with base_url prepended).
        """
        # Merge user-provided URL with base_url
        full_url = urllib.parse.urljoin(self.base_url, params.url)

        logger.info(f"Executing WebAPITool: {params.method} {full_url}")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method=params.method,
                    url=full_url,
                    headers=params.headers,
                    json=params.body
                ) as response:
                    response.raise_for_status()
                    return await response.json()
        except aiohttp.ClientError as e:
            logger.error(f"HTTP request failed: {e}", exc_info=True)
            return {"error": str(e)}

    async def validate(self, params: WebAPIToolParameters) -> bool:
        """Simple URL validation."""
        try:
            url = urllib.parse.urlparse(params.url)
            return all([url.scheme, url.netloc])
        except Exception as e:
            logger.error(f"Validation failed: {e}", exc_info=True)
            return False

    def get_schema(self) -> Dict[str, Any]:
        """Return the JSON schema for parameters."""
        return self.parameters_class.schema()

    async def health_check(self) -> bool:
        """A trivial health check that returns True if base_url is valid."""
        # For demonstration, just check if base_url is parseable
        if not self.base_url:
            return True  # Let’s say it's optional
        try:
            url = urllib.parse.urlparse(self.base_url)
            return bool(url.scheme and url.netloc)
        except:
            return False

    @property
    def capabilities(self) -> Dict[str, Any]:
        return {
            "requires_network": True,
            "async_compatible": True,
            "tool_type": "web_api"
        }
