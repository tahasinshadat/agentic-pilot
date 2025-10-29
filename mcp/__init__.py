"""
MCP (Model Context Protocol) Module
Provides tool schemas and execution for Gemini.
"""

from .tool_schemas import (
    get_tool_schemas,
    get_tool_schema,
    format_tools_for_gemini,
)

from .tool_execution import (
    init_executor,
    initialize,
    execute_tool,
    cleanup,
)

__all__ = [
    "get_tool_schemas",
    "get_tool_schema",
    "format_tools_for_gemini",
    "init_executor",
    "initialize",
    "execute_tool",
    "cleanup",
]
