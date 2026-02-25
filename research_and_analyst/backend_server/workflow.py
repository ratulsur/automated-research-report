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
        
    def _search_web(self, state: InterviewState):
        """
        responsible for generating search query and searching the web usign Tavily
        """  

        try:
            self.logger.info("searching web and generating answer")
            structure_llm = self.llm.with_structured_output(SearchQuery)
            search_prompt = GENERATE_SEARCH_QUERY.render()
            search_query = structure_llm.invoke([SystemMessage(content=search_prompt)] + state["messages"])
            self.logger.info("Performing Tavily web search", query = search_query.search_query)
            search_docs = self.tavily_search.invoke(search_query.search_query)

            if not search_docs:
                self.logger.warning("No search results found")
                return { "context": ["[No search results found.]"]}
            formatted = "\n\n---\n\n".join(
                [doc.get("content", "") for doc in search_docs]
            )
            return {"context": [formatted]}
        except Exception as e:
            self.logger.error("Error during web search", error = str(e))
            raise ResearchAnalystException("failed during web search execution", e)
        
    def _generate_answer(self, state: InterviewState):
            """
            use the analyst's context to generate an expert response
            """
            analyst = state["analyst"]
            messages = state["messages"]
            context = state.get("context", ["[no context available.]"])

            try:
                self.logger.info("generating expert answer", analyst = analyst.name)
                system_prompt = GENERATE_ANSWERS.render(goals = analyst.persona, context = context)
                answer = self.llm.invoke([SystemMessage(content=system_prompt)] + messages)
                answer.name = "expert"
                self.logger.info("Expert answer generated successfully", preview = answer.content[:200])
                return {"messages": [answer]}
            except Exception as e:
                self.logger.error("Error generating answer", error = (e))
                raise ResearchAnalystException("Failed to generate expert answer", e)
            
    def _save_interview(self, state:InterviewState):
        """
        save the entire history between the analyst and the expert
        
        """

        messages = state["messages"]

        try:
            interview = get_buffer_string(messages)
            self.logger.info("messages saved", message_count = len(messages))
            return {"interview": interview}
        except Exception as e:
            self.logger.error("messages not saved", error = (e))
            raise ResearchAnalystException( "failed to save", e)
        
    def _write_section(self, state: InterviewState):
        """
        writes the report based on the data saved by the interview saver
        """

        context = state.get["context", ["[No context available]"]]
        analyst = state["analyst"]

        try:
            self.logger.info("generated report section", analyst = analyst.name)
            system_prompt = WRITE_SECTION.render(focus = analyst.description)
            section = 
            
        


    