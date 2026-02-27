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
        
    def write_introduction(self, state: ResearchGraphState):
        """
        writes the introduction part of the report
        """  
        topic = state["topic"]
        section = state["sections"]
        formatted_str_sections = "\n\n".join([f"{s}" for s in section])

        try:
            self.logger.info("generating the introductions", topic = topic)
            system_prompt = INTRO_CONCLUSION_INSTRUCTIONS.render(topic = topic, formatted_str_sections = formatted_str_sections)
            intro = self.llm.invoke([SystemMessage(content=system_prompt),
                                     HumanMessage(content="write the introduction part of the report")
                                     ])
            self.logger.info("Introduction generated", length = len(intro.content))
            return {"introduction": intro.content}
        except Exception as e:
            self.logger.error("some error occurred", error = (e))
            raise ResearchAnalystException("check your code buddy", e)
        
    def write_conclusion(self, state: ResearchGraphState):
        """
        writes the conclusion of the report
        """

        section = state["sections"]
        topic = state["topic"]

        try:
            self.logger.info("generated the conclusion", topic = topic)
            formatted_str_sections = "\n\n".join([f"{s}" for s in section])
            system_prompt = INTRO_CONCLUSION_INSTRUCTIONS.render(topic = topic, formatted_str_sections = formatted_str_sections)
            conclusion = self.llm.invoke([SystemMessage(content = system_prompt),
                                          HumanMessage(content="write report conclusion")
                                          ])
            self.logger.info("successfully generated the conclusion", length = len(conclusion.content))
            return{"conclusion":conclusion.content}
        except Exception as e:
            self.logger.error("failed to generate the conclusion", error = (e))
            raise ResearchAnalystException("hmmm...not there exactly", e)
        
    def finalize_report(self, state: ResearchGraphState):
        """
        finalizes the report and writes the final piece
        """

        content = state["content"]

        try:
            self.logger.info("finalises the report")
            if content.startswith("## Insights"):
                content = content.strip("## Insights")

            sources = None

            if "## Sources" in content:
                try:
                    content, sources = content.split("\n## Sources\n")
                except Exception as e:
                    self.logger.error("compilation failed", error = (e))
                    raise ResearchAnalystException("check code bruh!", e)
                
                final_report = (
                    state["introduction"] + "\n\n---\n\n" +
                    content + "\n\n---\n\n"+
                    state["conclusion"]
                )
                if sources:
                    final_report += "\n\## Sources\n" + sources

                self.logger.info("Voila!")
                return{"final_report": final_report}
        except Exception as e:
            self.logger.error("failed process", error = (e))
            raise ResearchAnalystException("heartbreak for you bruh!", e)
        
    def save_report(self, final_report:str, topic: str, format: str = "docx"):
        """
        saves the DOCX or PDF in respective subfolder
        """

        try:
            self.logger.info("saving report", topic = topic, format = format)
            timestamp = datetime.now().strftime("%d%m%Y_%H%M%S")
            safe_topic = re.sub(r'[\\/*?:"<>]', "_", topic)
            base_name = f"{safe_topic.replace(' ', '_')}_{timestamp}"

            

        
            

        


