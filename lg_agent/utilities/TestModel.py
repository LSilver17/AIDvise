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

import asyncio
from typing import Any, Callable, Dict, List, Sequence, Union
from langchain.messages import AIMessage
from langchain.tools import ToolRuntime
from langchain_classic.schema import BaseMessage, ChatResult
from langchain_classic.tools import BaseTool
from langchain_core.language_models import GenericFakeChatModel as _GenericFakeChatModel, SimpleChatModel
from langchain_core.outputs import ChatGeneration
from langchain_core.runnables import Runnable
from pydantic import PrivateAttr

class FakeChatModel(_GenericFakeChatModel):
    _bound_tools: Any = PrivateAttr(default=None)
    _bound_tool_choice: Any = PrivateAttr(default=None)
    _bound_tool_kwargs: Dict[str, Any] = PrivateAttr(default_factory=dict)
    _runtime_state: Any = PrivateAttr(default=None)
    _runtime_context: Any = PrivateAttr(default=None)
    _runtime_store: Any = PrivateAttr(default=None)
    _runtime_config: Dict[str, Any] = PrivateAttr(default_factory=dict)

    def bind_tools(self, tools, *, tool_choice=None, **kwargs):
        runtime_state = kwargs.pop("runtime_state", None)
        runtime_context = kwargs.pop("runtime_context", None)
        runtime_store = kwargs.pop("runtime_store", None)
        runtime_config = kwargs.pop("runtime_config", None)

        # GenericFakeChatModel doesn't execute tools, but callers expect this API.
        bound_model = self.model_copy(deep=True)
        bound_model._bound_tools = tools
        bound_model._bound_tool_choice = tool_choice
        bound_model._bound_tool_kwargs = kwargs
        bound_model._runtime_state = runtime_state
        bound_model._runtime_context = runtime_context
        bound_model._runtime_store = runtime_store
        bound_model._runtime_config = runtime_config or {}
        return bound_model

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: List[str] | None = None,
        run_manager: Any | None = None,
        **kwargs: Any,
    ) -> ChatResult:
        response = super()._generate(messages, stop=stop, run_manager=run_manager, **kwargs)

        if not response.generations:
            return response

        generation = response.generations[0]
        message = generation.message
        if not isinstance(message, AIMessage):
            return response

        tool_calls = getattr(message, "tool_calls", None) or []
        if not tool_calls or not self._bound_tools:
            return response

        executed_tool_calls: List[Dict[str, Any]] = []
        for tool_call in tool_calls:
            tool_name = tool_call.get("name")
            tool = self._get_bound_tool(tool_name)

            if tool is None:
                executed_tool_calls.append(
                    {
                        "name": tool_name,
                        "id": tool_call.get("id"),
                        "args": tool_call.get("args") or {},
                        "error": f'Tool "{tool_name}" is not bound to this fake model.',
                    }
                )
                continue

            executed_tool_calls.append(
                {
                    "name": tool_name,
                    "id": tool_call.get("id"),
                    "args": tool_call.get("args") or {},
                    "output": self._invoke_bound_tool(tool, tool_call),
                }
            )

        processed_message = message.model_copy(
            update={
                "additional_kwargs": {
                    **message.additional_kwargs,
                    "executed_tool_calls": executed_tool_calls,
                }
            }
        )
        processed_generation = generation.model_copy(update={"message": processed_message})
        return response.model_copy(update={"generations": [processed_generation]})

    def _get_bound_tool(self, tool_name: str) -> BaseTool | Callable[..., Any] | None:
        tools = self._bound_tools or []
        for tool in tools:
            if isinstance(tool, dict):
                candidate_name = tool.get("name")
            else:
                candidate_name = getattr(tool, "name", None) or getattr(tool, "__name__", None)

            if candidate_name == tool_name:
                return tool

        return None

    def _build_tool_runtime(self, tool_call_id: str | None) -> ToolRuntime:
        return ToolRuntime(
            state=self._runtime_state if self._runtime_state is not None else {},
            context=self._runtime_context,
            config=self._runtime_config,
            stream_writer=None,
            tool_call_id=tool_call_id,
            store=self._runtime_store,
        )

    def _inject_runtime_if_needed(self, tool: BaseTool | Callable[..., Any], tool_args: Dict[str, Any], tool_call_id: str | None) -> Dict[str, Any]:
        injected_keys = getattr(tool, "_injected_args_keys", frozenset())
        if "runtime" in injected_keys and "runtime" not in tool_args:
            return {**tool_args, "runtime": self._build_tool_runtime(tool_call_id)}
        return tool_args

    def _invoke_bound_tool(self, tool: BaseTool | Callable[..., Any], tool_call: Dict[str, Any]) -> Any:
        tool_args = tool_call.get("args") or {}
        tool_args = self._inject_runtime_if_needed(tool, tool_args, tool_call.get("id"))

        if isinstance(tool, BaseTool):
            try:
                return tool.invoke(tool_args)
            except NotImplementedError:
                return asyncio.run(tool.ainvoke(tool_args))

        if hasattr(tool, "invoke"):
            try:
                return tool.invoke(tool_args)
            except NotImplementedError:
                if hasattr(tool, "ainvoke"):
                    return asyncio.run(tool.ainvoke(tool_args))
                raise

        return tool(**tool_args) if isinstance(tool_args, dict) else tool(tool_args)

    async def _ainvoke_bound_tool(self, tool: BaseTool | Callable[..., Any], tool_call: Dict[str, Any]) -> Any:
        tool_args = tool_call.get("args") or {}
        tool_args = self._inject_runtime_if_needed(tool, tool_args, tool_call.get("id"))

        if isinstance(tool, BaseTool):
            return await tool.ainvoke(tool_args)

        if hasattr(tool, "ainvoke"):
            return await tool.ainvoke(tool_args)

        if hasattr(tool, "invoke"):
            return tool.invoke(tool_args)

        return tool(**tool_args) if isinstance(tool_args, dict) else tool(tool_args)

    def with_structured_output(self, schema, include_raw=False, **kwargs):
        class StructuredOutputModel(FakeChatModel):
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
        structured_model._runtime_state = self._runtime_state
        structured_model._runtime_context = self._runtime_context
        structured_model._runtime_store = self._runtime_store
        structured_model._runtime_config = self._runtime_config
        return structured_model

class MockToolCallingModel(SimpleChatModel):
    """A fake chat model that returns tool-calling AIMessages for LangGraph."""
    responses: List[Union[str, Dict[str, Any]]]
    i: int = 0

    def _generate(self, messages: List[BaseMessage], **kwargs: Any) -> ChatResult:
        # Cycle through scripted responses
        response = self.responses[self.i]
        self.i = (self.i + 1) % len(self.responses)

        if isinstance(response, str):
            message = AIMessage(content=response)
        else:
            # Create the AIMessage with tool calls
            message = AIMessage(
                content=response.get("content", ""),
                tool_calls=response.get("tool_calls", [])
            )
        return ChatResult(generations=[ChatGeneration(message=message)])

    @property
    def _llm_type(self) -> str: return "mock-tool-model"