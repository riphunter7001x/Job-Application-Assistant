import os
import logging
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# Load API key from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    logging.error("GROQ_API_KEY is missing from environment variables.")
    raise EnvironmentError("GROQ_API_KEY is not set. Please check your .env file.")


try:
    llm_model = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0,
        max_tokens=None,
        timeout=30,  # Setting a reasonable timeout
        max_retries=2,
    )
    logging.info("LLM model initialized successfully.")
except Exception as e:
    logging.exception("Failed to initialize ChatGroq model.")
    raise
