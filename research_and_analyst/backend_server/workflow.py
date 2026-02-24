from langgraph.graph import START, END
from langchain_core.messages import HumanMessage, SystemMessage, get_buffer_string
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Send
from research_and_analyst.schemas.models import InterviewState, SearchQuery
from research_and_analyst.prompt_library.prompt_locator import (
    ANALYST_ASK_QUESTIONS,
    GENERATE_SEARCH_QUERY,
    GENERATE_ANSWERS,
    WRITE_SECTION
)
from research_and_analyst.log.logger import CustomLogger
from research_and_analyst.exception.custom_exception import ResearchAnalystException

class InterviewGraphBuilder:
    """
    this class is responsible for performing the following:
    1. generating expert level questions.
    2. performing web-search for gathering the answers of those questions.
    3. expert generating answers based on the gathered data.
    4. saving the asnwers.
    5. generating a summarized answer.
    """
    def __init__(self, llm, tavily_search):
        self.llm = llm
        self.tavily_search = tavily_search
        self.memory = MemorySaver()
        self.logger = CustomLogger.bind(module = "InterviewGraphBuilder")

    def _generate_questions(self, state: InterviewState):
        """
        this generates the first question based on the analysts's persona.
        """
        analyst = state["analyst"]
        messages = state["messages"]

        try:
            self.logger.info("generatign analyst question", analyst = analyst.name)
            system_prompt = ANALYST_ASK_QUESTIONS.render(goals = analyst.persona)
            question = self.llm.invoke([SystemMessage(content = system_prompt)] + messages)
            self.logger.info("Question generated successfully", question_preview = question.content[:200])
            return {"messages": [question]}
        except Exception as e:
            self.logger.error("Error generating analyst's question", error = str(e))
            raise ResearchAnalystException("Failed to generate question", e)
        
 
    