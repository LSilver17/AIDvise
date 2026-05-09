"""
Copyright 2026 Luca Silver

Extended fake chat model for testing that adds tool binding and structured output support.

Classes:
- `GenericFakeChatModel`: Extends LangChain's fake chat model with tool binding and structured output capabilities.
  - `bind_tools`: Binds tools to the model for simulating tool-calling scenarios during testing.
  - `with_structured_output`: Enables structured JSON output that matches a provided Pydantic schema.

Purpose:
- Provides a test double for LangChain chat models that allows simulating tool calls and structured responses
  without making actual API calls, enabling faster and cheaper testing of agent graphs and workflows.
"""

from typing import Any, Dict

from langchain_core.language_models import GenericFakeChatModel as _GenericFakeChatModel
from pydantic import PrivateAttr


class GenericFakeChatModel(_GenericFakeChatModel):
    _bound_tools: Any = PrivateAttr(default=None)
    _bound_tool_choice: Any = PrivateAttr(default=None)
    _bound_tool_kwargs: Dict[str, Any] = PrivateAttr(default_factory=dict)

    def bind_tools(self, tools, *, tool_choice=None, **kwargs):
        # GenericFakeChatModel doesn't execute tools, but callers expect this API.
        bound_model = self.model_copy(deep=True)
        bound_model._bound_tools = tools
        bound_model._bound_tool_choice = tool_choice
        bound_model._bound_tool_kwargs = kwargs
        return bound_model

    def with_structured_output(self, schema, include_raw=False, **kwargs):
        class StructuredOutputModel(GenericFakeChatModel):
            _schema: Any = PrivateAttr(default=None)

            def invoke(self, *args, **kwargs):
                response = super().invoke(*args, **kwargs)
                schema = self._schema
                if schema is None:
                    raise ValueError("Structured output schema was not configured.")

                content = response.content
                if hasattr(schema, "model_validate_json"):
                    return schema.model_validate_json(content)
                return schema.parse_raw(content)

        structured_model = StructuredOutputModel(messages=self.messages)
        structured_model._schema = schema
        structured_model._bound_tools = self._bound_tools
        structured_model._bound_tool_choice = self._bound_tool_choice
        structured_model._bound_tool_kwargs = self._bound_tool_kwargs
        return structured_model
