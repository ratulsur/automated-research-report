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

    
