# llm/openrouter_llm.py
import aiohttp
from typing import Optional, Dict
from .base_llm import BaseLLM, LLMConfig

class OpenRouterLLM(BaseLLM):
    """
    Implementation for calling OpenRouter-based LLM endpoints.
    """

    async def generate_text(self, prompt: str) -> str:
        # Construct request payload
        payload = {
            "prompt": prompt,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            # You might pass model name in the request, depending on OpenRouter's specs
            "model": self.config.model
        }

        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            # If OpenRouter requires a special vendor header, add it here
            # "HTTP-Vendor": "..."
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                url=self.config.endpoint,
                json=payload,
                headers=headers,
                timeout=30,
            ) as response:
                if response.status != 200:
                    body = await response.text()
                    raise RuntimeError(f"OpenRouter call failed. Status={response.status}, Body={body}")

                data = await response.json()
                # Adjust below to match actual OpenRouter JSON response shape
                return data.get("choices")[0].get("text", "")

    async def health_check(self) -> bool:
        """
        A simple check to see if OpenRouter is responding.
        """
        # Basic approach: attempt a quick call with a trivial prompt
        try:
            test_prompt = "Hello"
            _ = await self.generate_text(test_prompt)
            return True
        except Exception:
            return False
