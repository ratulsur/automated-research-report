import operator
from typing import Annotated, List, Optional
from langgraph.graph import MessagesState
from pydantic import BaseModel, Field, ConfigDict
from typing_extensions import TypedDict


# -------------------------
# Pydantic models
# -------------------------

class Section(BaseModel):
    model_config = ConfigDict(extra="ignore")

    title: str = Field(..., description="Section title")
    content: str = Field(..., description="Section content (markdown/text)")


class Analyst(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: str = Field(..., description="Name of the analyst persona")
    affiliation: str = Field(..., description="Organization or institute the analyst is associated with")
    role: str = Field(..., description="Role of the analyst in the research area")
    description: str = Field(..., description="Description of the analyst's focus, motives, concerns, and goals")

    # Often useful for interview prompts; safe default if LLM omits it
    goals: List[str] = Field(default_factory=list, description="List of concrete goals / focus areas for this analyst")


class Perspectives(BaseModel):
    model_config = ConfigDict(extra="ignore")

    analysts: List[Analyst] = Field(
        default_factory=list,
        description="A list of analyst personas (each with role/affiliation/description/goals)",
    )


class SearchQuery(BaseModel):
    model_config = ConfigDict(extra="ignore")

    search_query: Optional[str] = Field(None, description="Search query for retrieval/web search")


# -------------------------
# LangGraph State Schemas
# -------------------------

class GenerateAnalystsState(TypedDict, total=False):
    topic: str
    max_analysts: int
    human_analyst_feedback: str

    # Output of create_analyst node
    analysts: List[Analyst]


class InterviewState(MessagesState):
    # MessagesState already contains: messages: list
    max_num_turns: int

    # aggregated over turns
    context: Annotated[list, operator.add]

    # The current analyst persona running this interview
    analyst: Analyst

    # Interview transcript (string)
    interview: str

    # Sections created from this interview (aggregated)
    sections: Annotated[list, operator.add]


class ResearchGraphState(TypedDict, total=False):
    topic: str
    max_analysts: int
    human_analyst_feedback: str

    # Analyst personas produced by create_analyst
    analysts: List[Analyst]

    # Report artifacts (aggregated)
    sections: Annotated[list, operator.add]

    introduction: str
    content: str
    conclusion: str
    final_report: str