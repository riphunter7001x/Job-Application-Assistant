
from src.utils import ResumeResponse
from src.prompt import prompt_template

def parser_agent(state):
    resume_path = state["resume_file"]
    job_description = state["job_description"]
    
    resume_content = extract_from_doc(resume_path)
    
    structured_response = llm_model.with_structured_output(ResumeResponse)
    response = structured_response.invoke(
        prompt_template.format(
            text=resume_content, 
            job_description=job_description
        )
    ).model_dump()
    
    # Update the state with the response
    return {
        **state,  # Preserve existing state
        "score_and_details": response  # Add or update score_and_details
    }