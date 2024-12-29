# core/tool_interface.py
import asyncio
from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style
from prompt_toolkit.formatted_text import HTML
from rich.console import Console
from rich.syntax import Syntax

class ToolingInterface:
    """
    A class that manages user interaction in the terminal (TUI).
    """

    def __init__(self):
        self.session = PromptSession()
        self.console = Console()
        self.style = Style.from_dict({
            'prompt': 'ansicyan bold',
            'input': 'ansiwhite',
            'output': 'ansigreen',
        })

    async def get_input(self, multiline: bool = False) -> str:
        """
        Prompt user for input, optionally multiline.
        """
        if multiline:
            return await self.session.prompt_async(
                HTML("<prompt>>> </prompt>"),
                multiline=True,
                style=self.style,
                prompt_continuation=lambda width, line_number, is_soft_wrap:
                    HTML('<prompt>... </prompt>')
            )
        return await self.session.prompt_async(
            HTML("<prompt>> </prompt>"),
            style=self.style
        )

    def display_output(self, content: str, syntax_highlight: bool = False):
        """
        Display text in the terminal. If syntax_highlight is True,
        we'll render it with Python syntax highlighting.
        """
        if syntax_highlight:
            syntax = Syntax(content, "python", theme="monokai", line_numbers=False)
            self.console.print(syntax)
        else:
            self.console.print(content)
