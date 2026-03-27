"""
BaseTool: The abstract base class for all DevToolkit plugins.

To add a new tool, create a new file in devtoolkit/tools/ and define
a class that inherits from BaseTool. DevToolkit will auto-discover it.
"""

from abc import ABC, abstractmethod
import argparse


class BaseTool(ABC):
    """
    Abstract base class for all DevToolkit plugins.

    Every tool must implement:
        - name (str): The CLI subcommand name (e.g. "timer", "weather")
        - description (str): A short description shown in help text
        - run(args): The main logic of the tool

    Optional:
        - add_arguments(parser): Add argparse arguments specific to this tool
    """

    # Subclasses must define these class-level attributes
    name: str = ""
    description: str = ""

    @abstractmethod
    def run(self, args: argparse.Namespace) -> None:
        """Execute the tool with the given parsed arguments."""
        ...

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        """
        Add tool-specific arguments to the subcommand parser.
        Override this method to add your own arguments.
        """
        pass

    def __repr__(self) -> str:
        return f"<Tool: {self.name}>"
