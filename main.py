import streamlit as st
import pandas as pd
import tempfile
import os
from pathlib import Path
from src.workflow import AgentState, graph
from src.utils import launch_email_client,send_email_smtp

st.set_page_config(page_title="Job Application Assistant", layout="wide")

# Custom styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        margin-top: 1.5rem;
        margin-bottom: 0.75rem;
    }
    .score-box {
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    .good-score {
        background-color: #d4edda;
        color: #155724;
    }
    .medium-score {
        background-color: #fff3cd;
        color: #856404;
    }
    .bad-score {
        background-color: #f8d7da;
        color: #721c24;
    }
    .info-box {
        background-color: #e2f0fd;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">Job Application Assistant</div>', unsafe_allow_html=True)

st.markdown("""
Upload your resume and paste a job description to:
<ul>
<li>Get an ATS compatibility score</li>
<li>See matched and missing keywords</li>
<li>Get personalized resume suggestions</li>
<li>Generate cold email templates</li>
</ul>
</div>
""", unsafe_allow_html=True)

# File upload for resume
st.markdown('<div class="section-header">Upload Your Resume</div>', unsafe_allow_html=True)
resume_file = st.file_uploader("Upload your resume (PDF or DOCX)", type=["pdf", "docx"])

# Job description input
st.markdown('<div class="section-header">Enter Job Description</div>', unsafe_allow_html=True)
job_description = st.text_area("Paste the job description here", height=200)

# Process button
if st.button("Analyze Application"):
    if resume_file is not None and job_description:
        st.info("Processing your application... Please wait.")
        
        # Save the uploaded file to a temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{resume_file.name.split('.')[-1]}") as tmp_file:
            tmp_file.write(resume_file.getvalue())
            resume_path = tmp_file.name
        
        try:
            # Process with the existing workflow
            state = AgentState({
                "job_description": job_description,
                "resume_file": Path(resume_path)
            })
            
            response = graph.invoke(state)
            
            # Extract information from the response
            ats_score = response.get("ats_analysis_agent", {}).get("job_description_match_score", 0)
            matched_keywords = response.get("ats_analysis_agent", {}).get("matching_keywords", [])
            missing_keywords = response.get("ats_analysis_agent", {}).get("missing_keywords", [])
            company_name = response.get("ats_analysis_agent", {}).get("company_name", "Unknown Company")
            edit_suggestions = response.get("ats_analysis_agent", {}).get("resume_edit_suggestions", [])
            
            cold_mail_subject = response.get("cold_mail_writer_agent", {}).get("subject", "")
            cold_mail_body = response.get("cold_mail_writer_agent", {}).get("main_body", "")
            potential_emails = response.get("email_finder_agent", {}).get("emails", [])
            
            # Display results in tabs
            tab1, tab2, tab3 = st.tabs(["ATS Analysis", "Resume Suggestions", "Cold Email Generator"])
            
            with tab1:
                # ATS Score with visual representation
                score_class = "good-score" if ats_score >= 80 else "medium-score" if ats_score >= 60 else "bad-score"
                st.markdown(f'<div class="section-header">ATS Compatibility Score</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="score-box {score_class}"><h1>{ats_score}%</h1></div>', unsafe_allow_html=True)
                
                # Company identification
                st.markdown(f'<div class="section-header">Company Identified</div>', unsafe_allow_html=True)
                st.markdown(f"<h3>{company_name}</h3>", unsafe_allow_html=True)
                
                # Keywords analysis
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown('<div class="section-header">Matched Keywords</div>', unsafe_allow_html=True)
                    if matched_keywords:
                        for keyword in matched_keywords:
                            st.markdown(f"✅ {keyword}")
                    else:
                        st.write("No keywords matched.")
                
                with col2:
                    st.markdown('<div class="section-header">Missing Keywords</div>', unsafe_allow_html=True)
                    if missing_keywords:
                        for keyword in missing_keywords:
                            st.markdown(f"❌ {keyword}")
                    else:
                        st.write("No missing keywords.")
            
            with tab2:
                st.markdown('<div class="section-header">Resume Edit Suggestions</div>', unsafe_allow_html=True)
                if edit_suggestions:
                        st.markdown(edit_suggestions)
                        st.divider()
                else:
                    st.write("No suggestions available.")
            
            with tab3:
                st.markdown('<div class="section-header">Cold Email Generator</div>', unsafe_allow_html=True)
                
                # Display potential emails if available
                if potential_emails:
                    st.markdown('<div class="section-header">Potential Contacts</div>', unsafe_allow_html=True)
                    email_df = pd.DataFrame({"Email": potential_emails})
                    st.dataframe(email_df)
                else:
                    st.warning("No potential email contacts found.")
                
                # Display email template
                st.markdown('<div class="section-header">Email Template</div>', unsafe_allow_html=True)
                st.markdown(f"**Subject:** {cold_mail_subject}")
                st.text_area("Email Body", value=cold_mail_body, height=300)
                
                if potential_emails:
                    if st.button("Open Email Client"):
                        mailto_script = launch_email_client(cold_mail_body, potential_emails, cold_mail_subject)
                        st.markdown(mailto_script, unsafe_allow_html=True)
                
            # Clean up the temporary file
            os.unlink(resume_path)
            
        except Exception as e:
            st.error(f"An error occurred during processing: {str(e)}")
    else:
        st.warning("Please upload your resume and enter a job description to continue.")

# Footer
st.markdown("---")
st.markdown("© 2025 Job Application Assistant | Powered by AI")