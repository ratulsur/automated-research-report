import operator
from typing import Annotated, List, Any
from langgraph.graph import MessagesState
from pydantic import BaseModel, Field
from typing_extensions import TypedDict

class Section(BaseModel):
    title: str
    content: str

class Analyst(BaseModel):
    name: str = Field(description="name of the analyst")
    affiliation: str = Field(description="institute to which the analyst is associated with")
    role: str = Field(description="role of the analyst in the given area of the research")
    description :str = Field(description="description of the research area of the analyst's focus, goals, concerns and motives")

class Perspectives(BaseModel):
    analysts: str = Field(description=" a comprehensive list of analysts with their roles and desciptions")


class SearchQuery(BaseModel):
    search_query: str = Field(None, description="search query for retrieval.")


class GenerateAnalystsState(TypedDict):
    topic: str 
    max_analysts: int
    human_analysts_feedback: str
    analyst: List[Analyst]

class InterviewState(MessagesState):
    max_num_turns: int
    context: Annotated[list, operator.add]
    analyst: Analyst
    interview: str
    sections: list

class ResearchGraphState(TypedDict):
    topic: str
    max_analysts: int
    human_analyst_feedback: str
    analysts: List[Any] = Field(default_factory=list)
    analyst: List[Analyst]
    sections: Annotated[list, operator.add]
    introduction: str
    content: str
    conclusion: str
    final_report: str

    
