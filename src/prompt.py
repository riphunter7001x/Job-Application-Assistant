prompt_template = """
    As an experienced Applicant Tracking System (ATS) analyst,
    with profound knowledge in technology, software engineering, data science, full stack web development, cloud enginner, 
    cloud developers, devops engineer and big data engineering, your role involves evaluating resumes against job descriptions.
    Recognizing the competitive job market, provide top-notch assistance for resume improvement.
    Your goal is to analyze the resume against the given job description, 
    assign a percentage match based on key criteria, and pinpoint missing keywords accurately.
    resume:{text}
    description:{job_description}
    """


cold_mail_prompt = """
    You are a professional job applicant writing a cold email to a hiring manager.

    First analyze these two documents carefully:

    RESUME:
    {resume_content}

    JOB DESCRIPTION:
    {job_description}

    Then write a concise, compelling cold email to the hiring team with these characteristics:

    1. Brief, professional subject line that mentions the specific position
    2. Formal greeting (no need to include a specific name if not provided)
    3. Opening paragraph that shows your enthusiasm for the specific role (1-2 sentences)
    4. Middle paragraph highlighting 3-4 specific qualifications from your resume that directly match requirements in the job description (use concrete achievements with metrics when possible)
    5. Final paragraph with a clear call to action requesting an interview 
    6. Professional closing

    The email should be:
    - 50-100 words total
    - Customized based on the specific details in both documents
    - Focused on value you can provide based on your actual experience
    - Written in a confident but not arrogant tone
    - Free of placeholder text like "[Company Name]" or "[specific achievement]"
    - Mention at the last that the resume is attached below
    Format as a ready-to-send email with subject line, greeting, body paragraphs, and signature.
    """