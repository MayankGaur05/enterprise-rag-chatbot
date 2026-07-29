import os
import streamlit as st
import httpx 
from loguru import logger
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

logger.remove()
logger.add(
sink=lambda msg: print(msg, end=""),
level=os.getenv("LOG_LEVEL", "INFO").upper(),
format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:<8} | frontend:{function}:{line} | {message}",
)

DEFAULT_BACKEND_URL = os.getenv("BACKEND_BASE_URL", "http://127.0.0.1:8000")

st.title("Enterprise RAG Chatbot")

st.write("Welcome to the Enterprise RAG Chatbot! This application allows you to interact with a Retrieval-Augmented Generation (RAG) model for enterprise use cases.")

st.write("You can ask questions, retrieve information, and get responses based on the knowledge embedded in the RAG model.")

st.caption("Note: This is a demo application. Please ensure you have the necessary permissions and access to the underlying data sources when using this chatbot in a production environment.")

backend_url = st.text_input("Backend URL:", value=DEFAULT_BACKEND_URL)



def check_api_health(backend_url):
    try:
        logger.info(f"Health check initiated. backend_url={backend_url}")
        st.info("Checking API health...")
        endpoint = backend_url.rstrip("/") + "/health"
        response = httpx.get(endpoint, timeout=5.0)
        response.raise_for_status()
        data = response.json()
        if response.status_code == 200:
            st.success("API is healthy")
            st.write("Status:", data.get("status", "N/A"))
            st.write("Service:", data.get("service", "N/A"))
            st.write("Timestamp:", data.get("timestamp", "N/A"))
        logger.info(f"Health check success: status={data.get('status')}, service={data.get('service')}")
    except httpx.ConnectError:
        logger.error(f"Connection error occurred while trying to reach the API. backend_url={backend_url}")
        st.error("Connection error occurred while trying to reach the API")
    except httpx.TimeoutException:
        logger.error(f"Request to the API timed out. backend_url={backend_url}")
        st.error("Request to the API timed out")
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error occurred: {e.response.status_code} - {e.response.text}. backend_url={backend_url}")
        st.error(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
    except httpx.RequestError:
        logger.error(f"Failed to connect to the API. backend_url={backend_url}")
        st.error("Failed to connect to the API")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}. backend_url={backend_url}")
        st.error(f"An unexpected error occurred: {str(e)}")

if st.button("Check API Health"):
    if not backend_url.strip():
        st.warning("Please enter a backend URL.")
    else:
        check_api_health(backend_url)