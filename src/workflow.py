from typing_extensions import Annotated, TypedDict, NotRequired, Optional
from pathlib import Path
from typing import Dict, Any
from langgraph.graph import StateGraph, END, START
from src.agents import ats_analysis_agent, cold_mail_writer_agent, email_finder_agent

class AgentState(TypedDict):
    job_description: str
    resume_file: Path
    resume_content: Optional[str]
    ats_analysis_agent: Optional[Dict[str, Any]]
    email_finder_agent: Optional[Dict[str, Any]]
    cold_mail_writer_agent: Optional[Dict[str, Any]]

# demo example
# state = AgentState(
#     job_description=jd3,
#     resume_file=Path("Aditya_Varpe_AI_Engineer_Resume (5).pdf")
# )

workflow = StateGraph(AgentState)

# add nodes first
workflow.add_node("ats_analysis", ats_analysis_agent)
workflow.add_node("cold_mail_writer", cold_mail_writer_agent)
workflow.add_node("email_finder", email_finder_agent)

# Connect agents with edges
workflow.add_edge(START, "ats_analysis")
workflow.add_edge("ats_analysis", "cold_mail_writer")
workflow.add_edge("cold_mail_writer", "email_finder")
workflow.add_edge("email_finder", END)


# Compile the graph
graph = workflow.compile()