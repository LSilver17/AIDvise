"""
Copyright 2026 Luca Silver

Initializes language models for different agent nodes and modes (production or testing).

Functions:
- `_load_model_config`: Loads model configuration from model_select.json.
- `_normalize_model_name`: Normalizes model names by converting to lowercase and replacing hyphens with underscores.
- `_s_planning_testing_model`: Creates a fake testing model for the student planning node.
- `_a_planning_testing_model`: Creates a fake testing model for the advisor planning node.
- `_s_db_testing_model`: Creates a fake testing model for the student database helper node.
- `_a_db_testing_model`: Creates a fake testing model for the advisor database helper node.
- `_s_web_testing_model`: Creates a fake testing model for the student web helper node.
- `_a_web_testing_model`: Creates a fake testing model for the advisor web helper node.
- `_insertion_testing_model`: Creates a fake testing model for the insertion helper node.
- `_alerts_testing_model`: Creates a fake testing model for the alerts agent node.
- `_create_model`: Factory function that creates appropriate chat models based on model name and node type.

Modules Initialized:
- `planning_llm`: Language model for planning nodes.
- `db_llm`: Language model for database helper nodes.
- `web_llm`: Language model for web search helper nodes.
- `insertion_llm`: Language model for insertion helper nodes.
- `alerts_llm`: Language model for alerts agent nodes.
"""

import os, sys

# adds utilities directory to system path if not already there
PARENT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PARENT_DIR not in sys.path:
    sys.path.append(PARENT_DIR)

# adds root directory to system path if not already there
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import AIMessage, ToolCall
from langchain_openai import ChatOpenAI
from langchain_openrouter import ChatOpenRouter
from utilities.TestModel import GenericFakeChatModel
import json

load_dotenv()

def _load_model_config() -> tuple[dict, str]:
    with open(os.path.join(ROOT_DIR, "model_select.json"), "r", encoding="utf-8") as f:
        model_select = json.load(f)
    mode = model_select.get("mode")
    models = model_select.get(mode)
    return models, mode


def _normalize_model_name(model_name: str) -> str:
    return model_name.strip().lower().replace("-", "_")


def _s_planning_testing_model() -> GenericFakeChatModel:
    return GenericFakeChatModel(
        messages=iter(
            [
                AIMessage(
                    content=json.dumps(
                        {
                            "requires_database": True,
                            "requires_web_search": True,
                            "requires_insertion": True,
                            "answer": "",
                            "info_needed_db": (
                                "Find the CSC 212 course details and identify Spring 2026 "
                                "CSC 212 sections taught by Prof. Nguyen."
                            ),
                            "info_needed_web": (
                                "Find current public guidance on CSC 212 preparation and "
                                "academic planning recommendations."
                            ),
                            "info_to_insert": (
                                "Student is interested in Machine Learning and wants to "
                                "track CSC 212 section 1."
                            ),
                        }
                    )
                ),
                AIMessage(
                    content=json.dumps(
                        {
                            "requires_database": False,
                            "requires_web_search": False,
                            "requires_insertion": False,
                            "answer": (
                                "From the database and web results, the advisor can summarize "
                                "CSC 212 details, confirm Spring 2026 section options, and "
                                "share up-to-date planning guidance. The student interest and "
                                "tracked section request were also processed."
                            ),
                            "info_needed_db": "",
                            "info_needed_web": "",
                            "info_to_insert": "",
                        }
                    )
                ),
                AIMessage(
                    content=json.dumps(
                        {
                            "requires_database": False,
                            "requires_web_search": False,
                            "requires_insertion": False,
                            "answer": (
                                "Testing fallback: enough information has been collected to "
                                "answer without additional helper calls."
                            ),
                            "info_needed_db": "",
                            "info_needed_web": "",
                            "info_to_insert": "",
                        }
                    )
                ),
            ]
        )
    )


def _a_planning_testing_model() -> GenericFakeChatModel:
    return GenericFakeChatModel(
        messages=iter(
            [
                AIMessage(
                    content=json.dumps(
                        {
                            "requires_database": True,
                            "requires_web_search": True,
                            "answer": "",
                            "info_needed_db": (
                                "Find the advisor-facing academic records relevant to CSC 212 "
                                "for Spring 2026 planning."
                            ),
                            "info_needed_web": (
                                "Find current policy and transfer/advising references relevant "
                                "to CSC 212 guidance."
                            ),
                        }
                    )
                ),
                AIMessage(
                    content=json.dumps(
                        {
                            "requires_database": False,
                            "requires_web_search": False,
                            "answer": (
                                "From the gathered database and web information, the advisor "
                                "can provide a complete recommendation for CSC 212 planning."
                            ),
                            "info_needed_db": "",
                            "info_needed_web": "",
                        }
                    )
                ),
                AIMessage(
                    content=json.dumps(
                        {
                            "requires_database": False,
                            "requires_web_search": False,
                            "answer": (
                                "Advisor test fallback: enough information is available to "
                                "answer without additional helper calls."
                            ),
                            "info_needed_db": "",
                            "info_needed_web": "",
                        }
                    )
                ),
            ]
        )
    )


def _s_db_testing_model() -> GenericFakeChatModel:
    return GenericFakeChatModel(
        messages=iter(
            [
                AIMessage(
                    content="Testing database helper tool usage.",
                    tool_calls=[
                        ToolCall(name="course_query_by_code", args={"course_code": "CSC 212"}, id="1"),
                        ToolCall(
                            name="course_query_by_title",
                            args={"course_title": "Intro to Software Engineering"},
                            id="2",
                        ),
                        ToolCall(
                            name="course_filter",
                            args={
                                "filters": {
                                    "terms": [{"year": 2026, "season": "Spring", "number": None}],
                                    "departments": ["CSC"],
                                    "credits": {"condition": ">=", "credits": 3},
                                }
                            },
                            id="3",
                        ),
                        ToolCall(
                            name="section_filter",
                            args={
                                "filters": {
                                    "terms": [{"year": 2026, "season": "Spring", "number": None}],
                                    "course_codes": ["CSC 212"],
                                }
                            },
                            id="4",
                        ),
                        ToolCall(name="student_basic_info", args={}, id="5"),
                        ToolCall(name="student_course_history", args={}, id="6"),
                    ],
                ),
                AIMessage(
                    content="Testing database helper tool usage, part two.",
                    tool_calls=[
                        ToolCall(name="student_interests", args={}, id="7"),
                        ToolCall(name="student_tracked_sections", args={}, id="8"),
                        ToolCall(
                            name="program_requirements",
                            args={"program_name": "Computer Science Transfer"},
                            id="9",
                        ),
                        ToolCall(name="upcoming_events", args={}, id="10"),
                        ToolCall(name="event_dates", args={"event_name": "AI Career Panel"}, id="11"),
                    ],
                ),
                AIMessage(
                    content=(
                        "Database lookup complete: CSC 212, student information, program "
                        "requirements, and event data were retrieved."
                    )
                ),
                AIMessage(content="Database fallback: no additional database actions are needed."),
            ]
        )
    )


def _a_db_testing_model() -> GenericFakeChatModel:
    return GenericFakeChatModel(
        messages=iter(
            [
                AIMessage(
                    content="Testing advisor database helper tool usage.",
                    tool_calls=[
                        ToolCall(name="course_query_by_code", args={"course_code": "CSC 212"}, id="1"),
                        ToolCall(
                            name="course_query_by_title",
                            args={"course_title": "Intro to Software Engineering"},
                            id="2",
                        ),
                        ToolCall(
                            name="course_filter",
                            args={
                                "filters": {
                                    "terms": [{"year": 2026, "season": "Spring", "number": None}],
                                    "departments": ["CSC"],
                                    "credits": {"condition": ">=", "credits": 3},
                                }
                            },
                            id="3",
                        ),
                        ToolCall(
                            name="section_filter",
                            args={
                                "filters": {
                                    "terms": [{"year": 2026, "season": "Spring", "number": None}],
                                    "course_codes": ["CSC 212"],
                                }
                            },
                            id="4",
                        ),
                        ToolCall(
                            name="get_student_id_by_name",
                            args={"student_name": "Alice Johnson"},
                            id="5",
                        ),
                        ToolCall(name="student_basic_info", args={"student_id": 1}, id="6"),
                        ToolCall(name="student_course_history", args={"student_id": 1}, id="7"),
                    ],
                ),
                AIMessage(
                    content="Testing advisor database helper tool usage, part two.",
                    tool_calls=[
                        ToolCall(name="student_interests", args={"student_id": 1}, id="8"),
                        ToolCall(name="student_tracked_sections", args={"student_id": 1}, id="9"),
                        ToolCall(
                            name="program_requirements",
                            args={"program_name": "Computer Science Transfer"},
                            id="10",
                        ),
                        ToolCall(name="upcoming_events", args={}, id="11"),
                        ToolCall(
                            name="event_dates",
                            args={"event_name": "Software Design Interview Prep"},
                            id="12",
                        ),
                    ],
                ),
                AIMessage(
                    content=(
                        "Advisor database lookup complete: CSC 212, student lookup, program "
                        "requirements, and event data were retrieved."
                    )
                ),
                AIMessage(content="Advisor database fallback: no additional database actions are needed."),
            ]
        )
    )


def _s_web_testing_model() -> GenericFakeChatModel:
    return GenericFakeChatModel(
        messages=iter(
            [
                AIMessage(
                    content="Testing web helper tool usage.",
                    tool_calls=[
                        ToolCall(
                            name="web_search",
                            args={
                                "query": (
                                    "CSC 212 preparation guidance and academic planning recommendations"
                                )
                            },
                            id="1",
                        )
                    ],
                ),
                AIMessage(
                    content=(
                        "Web search complete: current guidance relevant to CSC 212 preparation "
                        "and academic planning was collected."
                    )
                ),
                AIMessage(content="Web fallback: no additional web searches are needed."),
            ]
        )
    )


def _a_web_testing_model() -> GenericFakeChatModel:
    return GenericFakeChatModel(
        messages=iter(
            [
                AIMessage(
                    content="Testing advisor web helper tool usage.",
                    tool_calls=[
                        ToolCall(
                            name="web_search",
                            args={
                                "query": (
                                    "current advisor guidance for CSC 212, transfer policy, and "
                                    "planning recommendations"
                                )
                            },
                            id="1",
                        )
                    ],
                ),
                AIMessage(
                    content=(
                        "Advisor web search complete: relevant advising policy and planning "
                        "guidance was retrieved."
                    )
                ),
                AIMessage(content="Advisor web fallback: no additional web searches are needed."),
            ]
        )
    )


def _insertion_testing_model() -> GenericFakeChatModel:
    return GenericFakeChatModel(
        messages=iter(
            [
                AIMessage(
                    content="Testing insertion helper tool usage.",
                    tool_calls=[
                        ToolCall(name="insert_student_interest", args={"interest": "Machine Learning"}, id="1"),
                        ToolCall(
                            name="insert_student_tracked_section",
                            args={"course_code": "CSC 212", "section_id": "1"},
                            id="2",
                        ),
                    ],
                ),
                AIMessage(
                    content=(
                        "Insertion complete: student interest and tracked CSC 212 section data "
                        "were processed."
                    )
                ),
                AIMessage(content="Insertion fallback: no additional insertions are needed."),
            ]
        )
    )


def _alerts_testing_model() -> GenericFakeChatModel:
    return GenericFakeChatModel(
        messages=iter(
            [
                AIMessage(
                    content=json.dumps(
                        {
                            "relivent_events": [
                                {"ID": 12, "Urgency": 5},
                                {"ID": 27, "Urgency": 3},
                            ]
                        }
                    )
                ),
                AIMessage(
                    content=json.dumps(
                        {
                            "relivent_events": [],
                        }
                    )
                ),
            ]
        )
    )


def _create_model(model_name: str, node_name: str):
    normalized = _normalize_model_name(model_name)

    match normalized:
        case "sonnet_4_6":
            if env := os.getenv("ANTHROPIC_API_KEY"):
                return ChatAnthropic(model="claude-sonnet-4-6", temperature=0.2)
            else:
                raise ValueError("ANTHROPIC_API_KEY not found in environment variables.")
        case "gpt_4o":
            if env := os.getenv("OPENAI_API_KEY"):
                return ChatOpenAI(model="gpt-4o", temperature=0.2)
            else:
                raise ValueError("OPENAI_API_KEY not found in environment variables.")
        case "free":
            if env := os.getenv("OPENROUTER_API_KEY"):
                return ChatOpenRouter(model="openrouter/free", temperature=0.2)
            else:
                raise ValueError("OPENROUTER_API_KEY not found in environment variables.")
        case "student_test":
            if node_name == "planning":
                return _s_planning_testing_model()
            if node_name == "db":
                return _s_db_testing_model()
            if node_name == "web":
                return _s_web_testing_model()
            if node_name == "insertion":
                return _insertion_testing_model()
            if node_name == "alerts":
                return _alerts_testing_model()
            raise ValueError(f"Unknown student testing node: {node_name}")
        case "advisor_test":
            if node_name == "planning":
                return _a_planning_testing_model()
            if node_name == "db":
                return _a_db_testing_model()
            if node_name == "web":
                return _a_web_testing_model()
            if node_name == "insertion":
                return _insertion_testing_model()
            if node_name == "alerts":
                return _alerts_testing_model()
            raise ValueError(f"Unknown advisor testing node: {node_name}")
        case _:
            raise ValueError(f"Model '{model_name}' not supported for advisor {node_name} node.")


model_select, mode = _load_model_config()

planning_llm = _create_model(model_select["planning"], "planning")
db_llm = _create_model(model_select["db"], "db")
web_llm = _create_model(model_select["web"], "web")
insertion_llm = _create_model(model_select["insertion"], "insertion")
alerts_llm = _create_model(model_select["alerts"], "alerts")
