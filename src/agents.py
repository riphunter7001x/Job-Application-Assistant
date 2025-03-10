import logging
from typing import Dict, Union
from src.utils import extract_from_doc, ResumeResponse, get_company_info, generate_cold_email
from src.model import llm_model
from src.prompt import prompt_template

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def ats_analysis_agent(state):
    """
    Analyzes the resume against the job description and extracts ATS-related insights.
    """
    try:
        resume_path = state.get("resume_file")
        job_description = state.get("job_description")
        
        if not resume_path or not job_description:
            raise ValueError("Missing resume file or job description.")
        
        resume_content = extract_from_doc(resume_path)
        structured_response = llm_model.with_structured_output(ResumeResponse)
        response = structured_response.invoke(
            prompt_template.format(text=resume_content, job_description=job_description)
        ).model_dump()
        
        state["resume_content"] = resume_content
        state["ats_analysis_agent"] = response
        return state
    except ValueError as ve:
        logging.error(f"ValueError: {ve}")
        return {"error": str(ve)}
    except Exception as e:
        logging.exception("Unexpected error in ats_analysis_agent")
        return {"error": "Internal server error in ATS analysis."}

def email_finder_agent(state):
    """
    Extracts company details and fetches email addresses using an external API.
    """
    try:
        company_name = state.get("ats_analysis_agent", {}).get("company_name", "").strip()
        
        if not company_name or company_name.lower() == "<not found>":
            raise ValueError("Organization details not found.")
        
        response = get_company_info(company_name)
        state["email_finder_agent"] = response
        return state
    except ValueError as ve:
        logging.warning(f"ValueError: {ve}")
        return {"error": str(ve)}
    except Exception as e:
        logging.exception("Unexpected error in email_finder_agent")
        return {"error": "Internal server error in email lookup."}

def cold_mail_writer_agent(state):
    """
    Generates a cold email based on the resume and job description.
    """
    try:
        job_description = state.get("job_description", "").strip()
        resume_content = state.get("resume_content", "").strip()
        
        if not job_description or not resume_content:
            raise ValueError("Job description or resume content is missing.")
        
        cold_mail = generate_cold_email(resume_content, job_description)
        state["cold_mail_writer_agent"] = cold_mail
        return state
    except ValueError as ve:
        logging.warning(f"ValueError: {ve}")
        return {"error": str(ve)}
    except Exception as e:
        logging.exception("Unexpected error in cold_mail_writer_agent")
        return {"error": "Internal server error in cold mail generation."}