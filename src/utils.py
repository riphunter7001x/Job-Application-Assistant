from pydantic import BaseModel, Field
from pathlib import Path
import fitz  # PyMuPDF
import docx
import requests  
import webbrowser
import urllib.parse
from src.model import llm_model
from src.prompt import cold_mail_prompt
import os
from typing import Dict, Union
from dotenv import load_dotenv
from typing import List


load_dotenv()  


# Load API key from environment variable
HUNTER_API_KEY = os.getenv("HUNTER_API_KEY")


class ColdEmailResponse(BaseModel):
    subject: str = Field(
        ..., 
        description="The subject line of the cold email response."
    )
    main_body: str = Field(
        ..., 
        description="The main content of the cold email response."
    )


class ResumeResponse(BaseModel):
    """Response containing resume analysis results."""

    company_name: str = Field(
        description="Name of the company the job is for. If not mentioned, return <null>"
    )
    job_ID: str = Field(
        description="JOB ID if mentioned in Job description. If not mentioned, return <null>"
    )
    job_description_match_score: int = Field(
        description="Match score between the resume and job description, ranging from 0 to 100."
    )
    missing_keywords: List[str] = Field(
        description="Keywords missing from the resume that are present in the job description."
    )
    matching_keywords: List[str] = Field(
        description="Keywords present in both the resume and job description."
    )
    resume_edit_suggestions: str = Field(
        description="Integrate relevant keywords from the job description into my resume, but maintain a natural flow. Do this without keyword stuffing."
    )

def generate_cold_email(resume_content: str, job_description: str) -> Dict[str, str]:
    """
    Uses an LLM to generate a cold email based on the provided resume and job description.
    
    Args:
        resume_content (str): The content of the user's resume.
        job_description (str): The job description.

    Returns:
        dict: A structured response containing the generated cold email.
    """
    try:
        structure_output = llm_model.with_structured_output(ColdEmailResponse)
        response = structure_output.invoke(
            cold_mail_prompt.format(resume_content=resume_content, job_description=job_description)
        ).model_dump()
        return response
    except Exception as e:
        return {"error": f"Failed to generate cold email: {str(e)}"}

def get_company_info(company_name: str) -> Dict[str, Union[str, list]]:
    """
    Fetches company email addresses and domain information from the Hunter.io API.

    Args:
        company_name (str): The name of the company to search for.

    Returns:
        dict: A dictionary containing email addresses and the domain if found, or an error message.
    """
    if not HUNTER_API_KEY:
        raise ValueError("Hunter.io API key not found. Please set HUNTER_API_KEY as an environment variable.")

    url = f"https://api.hunter.io/v2/domain-search?company={company_name}&api_key={HUNTER_API_KEY}"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx and 5xx)
        
        result = response.json()
        if not isinstance(result, dict):
            return {"error": "Invalid API response format."}
        
        domain = result.get("data", {}).get("domain")
        if domain:
            emails = [email.get("value", "") for email in result["data"].get("emails", []) if "value" in email]
            return {"emails": emails, "domain": domain}
        else:
            return {"error": "Organization details not found!"}
    
    except requests.exceptions.Timeout:
        return {"error": "Request timed out. Please try again later."}
    except requests.exceptions.HTTPError as http_err:
        return {"error": f"HTTP error occurred: {http_err}"}
    except requests.exceptions.ConnectionError:
        return {"error": "Network connection error. Please check your internet connection."}
    except requests.exceptions.RequestException as req_err:
        return {"error": f"Request failed: {req_err}"}
    except KeyError as key_err:
        return {"error": f"Missing expected data in API response: {key_err}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

import smtplib
import urllib.parse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email_smtp(sender_email, sender_password, email_list, subject, body):
    """
    Sends cold emails using SMTP.
    """
    smtp_server = "smtp.gmail.com"  # Change if using Outlook, Yahoo, etc.
    smtp_port = 587

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Secure connection
        server.login(sender_email, sender_password)

        for recipient in email_list:
            msg = MIMEMultipart()
            msg["From"] = sender_email
            msg["To"] = recipient
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain"))

            server.sendmail(sender_email, recipient, msg.as_string())

        server.quit()
        return "Emails sent successfully!"
    except Exception as e:
        return f"Error sending emails: {str(e)}"

import urllib.parse

def launch_email_client(template, email_list, subject):
    """
    Generates a mailto link to open the email client with prefilled details.
    """
    recipient_emails = ",".join(email_list)  # Combine emails into a single string
    subject_encoded = urllib.parse.quote(subject)  # URL encode the subject
    body_encoded = urllib.parse.quote(template)  # URL encode the body

    # Create the mailto link
    mailto_link = f"mailto:{recipient_emails}?subject={subject_encoded}&body={body_encoded}"

    # Return a clickable button that opens the email client
    return f'<a href="{mailto_link}" target="_blank"><button style="padding:10px 20px; background-color:#4CAF50; color:white; border:none; border-radius:5px; cursor:pointer;">Open Email Client</button></a>'


def extract_from_doc(file_path: Path) -> str:
    if file_path.suffix.lower() == ".pdf":
        doc = fitz.open(file_path)
        text = "\n".join([page.get_text("text") for page in doc])
        return text
    
    if file_path.suffix.lower() == ".docx":
        doc = docx.Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text

    raise ValueError("Unsupported file format. Only PDF and DOCX are supported.")
