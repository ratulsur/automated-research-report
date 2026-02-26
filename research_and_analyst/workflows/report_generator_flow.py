import os
import sys
import re
from datetime import datetime
from typing import Optional
from langgraph.types import Send
from jinja2 import Template
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_community.tools.tavily_search import TavilySearchResults
from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from langgraph.checkpoint.memory import MemorySaver
from research_and_analyst.schemas.models import Perspectives, GenerateAnalystsState, ResearchGraphState
from research_and_analyst.utils.model_loader import ModelLoader
from research_and_analyst.workflows.interview_workflow import InterviewGraphBuilder
from research_and_analyst.prompt_library.prompt_locator import CREATE_ANALYSIS_PROMPT, INTRO_CONCLUSION_INSTRUCTIONS, REPORT_WRITER_INSTRUCTIONS

from research_and_analyst.log.logger import CustomLogger
from research_and_analyst.exception.custom_exception import ResearchAnalystException



class AutonomousReportGenerator:
    """
    handles end-to-end autonomous report generation
    """
    def __init__(self, llm):
        self.llm = llm
        self.memory = MemorySaver()
        tavily_search = TavilySearchResults(tavily_api_key = os.getenv("TAVILY_API_KEY")
                                            ) 
        self.logger = CustomLogger.bind(module = "AutonomousReportGenerator")

    def create_analyst(self, state:GenerateAnalystsState):
        topic = state["topic"]
        max_analyst = state["max_analysts"]
        human_analyst_feedback = state["human_analysts_feedback"]

        try:
            self.logger.info("initiated persona creating", topic = topic)
            structured_llm = self.llm.with_structured_output(Perspectives)
            system_prompt = CREATE_ANALYSIS_PROMPT.render(
                topic = topic, max_analysts = max_analyst,
                human_analyst_feedback = human_analyst_feedback
            )
            analysts = structured_llm.invoke(
                [SystemMessage(content=system_prompt),
                 HumanMessage(content=f"generate a set of analysts"),
                ]
            )

        except Exception as e:
            self.logger.error("Failed to generate set of analysts", error = (e))
            raise ResearchAnalystException("check your code Bonita!", e)
        
    def human_feedback(self):
        """
        await node for human feedback
        """
        try:
            self.logger.info("awaiting human feedback")

        except Exception as e:
            self.logger.error("error in feedbacl stage", error =(e))
            raise ResearchAnalystException("sorry buddy! you are mistaken", e)
        
    def write_report(self, state: ResearchGraphState):
        """
        compile all sections into one single comprehensive report
        """
        sections = state.get("sections", [])
        topic = state.get("topic", "")

        try:
            if not sections:
                sections = ["no sections generated - please check"]
                self.logger.info("report writing genertaed", topic = topic)
                system_prompt = REPORT_WRITER_INSTRUCTIONS.render(topic = topic)
                report = self.llm.invoke([SystemMessage(content=system_prompt),
                                          HumanMessage(content= "\n\n". join(sections))
                                          ])
                self.logger.info("Report generated successfully")
                return {"content":report.content}
        except Exception as e:
            self.logger.error("report generation failed", error = (e))
            raise ResearchAnalystException("check your code darling", e)
        
        



