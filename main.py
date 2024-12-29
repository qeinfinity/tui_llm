# main.py
import asyncio
import logging
from core.tool_interface import ToolingInterface
from llm.base_llm import LLMConfig
from llm.openrouter_llm import OpenRouterLLM  # or your chosen LLM class
from core.tool_registry import ToolRegistry
from tools.web_api_tool import WebAPITool

from logging_conf import setup_logging

# Configure your LLM (possibly load from env vars or config file)
OPENROUTER_API_KEY = ""
OPENROUTER_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
MODEL_NAME = "anthropic/claude-3.5-sonnet:beta"

setup_logging(logging.DEBUG)  # or INFO, WARNING, etc.

logger = logging.getLogger(__name__)

# ========== PROMPT TEMPLATES ==========

SYSTEM_PROMPT = """\
You are a system architecture assistant.
You respond with detailed, step-by-step solutions about software architecture.
"""

def build_prompt(user_message: str) -> str:
    return f"{SYSTEM_PROMPT}\nUser: {user_message}\nAssistant:"

# ========== MAIN ==========

async def main():
    setup_logging(logging.DEBUG)
    # Create the TUI interface
    tui = ToolingInterface()

    # Create our LLM config and instance
    config = LLMConfig(
        api_key=OPENROUTER_API_KEY,
        endpoint=OPENROUTER_ENDPOINT,
        model=MODEL_NAME,
        temperature=0.1,
        max_tokens=512
    )
    llm = OpenRouterLLM(config)



    # 4) Create Tool Registry & Register a sample tool
    registry = ToolRegistry()
    web_tool = WebAPITool()
    try:
        await registry.register_tool("WebAPITool", web_tool)
    except Exception as e:
        logging.error("Failed to register WebAPITool", exc_info=True)

    # 5) Welcome message
    tui.display_output("Welcome to the LLM-enabled Tooling Interface!", syntax_highlight=False)
    tui.display_output("Type 'exit' or press Ctrl+C to quit.\n", syntax_highlight=False)

    while True:
        try:
            # Use multiline input by default
            user_input = await tui.get_input(multiline=True)

            # Exit conditions
            if user_input.strip().lower() in ["exit", "quit"]:
                tui.display_output("Goodbye!", syntax_highlight=False)
                break

            # Check for slash commands
            if user_input.startswith("/tool"):
                # Example parse: /tool WebAPITool url=/users method=GET
                # Very basic splitting: /tool <ToolName> key=value ...
                parts = user_input.split()
                if len(parts) < 2:
                    tui.display_output("Usage: /tool <ToolName> <param1=value> <param2=value> ...")
                    continue

                tool_name = parts[1]
                kv_pairs = parts[2:]  # everything after the tool name

                # Build a dict of param -> value
                kwargs = {}
                for kv in kv_pairs:
                    if "=" in kv:
                        k, v = kv.split("=", 1)
                        kwargs[k] = v

                # Try to get the tool and run it
                tool = await registry.get_tool(tool_name)
                if not tool:
                    tui.display_output(f"No such tool: {tool_name}")
                    continue

                # We expect the tool to have parameters_class for validation
                try:
                    params = tool.parameters_class(**kwargs)
                except Exception as e:
                    tui.display_output(f"Parameter validation error: {e}")
                    continue

                # Validate & Execute
                is_valid = await tool.validate(params)
                if not is_valid:
                    tui.display_output("Tool parameters validation failed.")
                    continue

                result = await tool.execute(params)
                tui.display_output(f"Tool result: {result}", syntax_highlight=False)

            else:
                # Normal LLM call (with prompt template)
                prompt = build_prompt(user_input)
                response = await llm.generate_text(prompt)
                tui.display_output(response, syntax_highlight=False)

        except (EOFError, KeyboardInterrupt):
            tui.display_output("\nExiting. Goodbye!", syntax_highlight=False)
            break
        except Exception as e:
            # Graceful error handling
            logging.error("An unexpected error occurred in main loop.", exc_info=True)
            tui.display_output(f"Error: {str(e)}", syntax_highlight=False)


if __name__ == "__main__":
    asyncio.run(main())
