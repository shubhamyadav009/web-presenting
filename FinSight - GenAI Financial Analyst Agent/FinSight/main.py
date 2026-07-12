"""
main.py

Entry point for FinSight - GenAI Financial Analyst Agent.
Supports both CLI and Streamlit web UI modes.
Usage:
  - CLI mode:       python main.py
  - Streamlit mode: python main.py streamlit
"""

from logging import Logger
import sys
import argparse
import os
import time
from pathlib import Path
from dotenv import load_dotenv
import requests
# Allow running this module directly (python main.py) from nested paths.
if __package__ in (None, ""):
    project_root: Path = Path(__file__).resolve().parents[1]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

from FinSight.core.rag.pipeline import RAGPipeline
from FinSight.utils.helpers import (
    validate_query,
    clean_text,
    is_financial_query
)
from FinSight.utils.logger import get_logger

# ----------------------------
# Load Environment Variables
# ----------------------------

load_dotenv()

# ----------------------------
# Initialize Logger
# ----------------------------

logger: Logger = get_logger(__name__)


API_HOST: str = os.getenv("API_HOST", "127.0.0.1")
API_PORT: int = int(os.getenv("API_PORT", "8000"))
API_BASE_URL: str = os.getenv("API_BASE_URL", f"http://{API_HOST}:{API_PORT}")


def is_backend_running() -> bool:
    """
    Checks whether FastAPI backend responds on /status.
    """
    try:
        response = requests.get(f"{API_BASE_URL}/status", timeout=2)
        return response.status_code == 200
    except Exception:
        return False


def launch_backend():
    """
    Launches FastAPI backend if not already running.
    Returns process handle only when this function starts a new backend process.
    """
    import subprocess

    if is_backend_running():
        logger.info("Backend already running.")
        return None

    logger.info("Starting backend API server with uvicorn.")
    
    # Get project root (parent of this file's directory)
    project_root = Path(__file__).resolve().parent.parent
    
    # Prepare environment with PYTHONPATH set
    env = os.environ.copy()
    env["PYTHONPATH"] = str(project_root)
    
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "FinSight.app.api:app",
            "--host",
            API_HOST,
            "--port",
            str(API_PORT),
            "--log-level",
            "info",
        ],
        cwd=str(project_root),
        env=env
        # Note: NOT capturing stdout/stderr to avoid blocking
    )

    # Wait briefly for startup so Streamlit can show live status immediately.
    print("Waiting for backend to start...")
    for attempt in range(40):  # Up to 20 seconds
        if process.poll() is not None:
            logger.error(f"Backend process exited (exit code {process.returncode})")
            return None
            
        if is_backend_running():
            logger.info("Backend API server is ready.")
            print("✓ Backend is ready!")
            return process
        
        time.sleep(0.5)

    logger.warning("Backend API server did not become ready in expected time.")
    print("⚠ Backend took longer than expected to start, but it may still be starting in background...")
    return process


# ----------------------------
# Initialize RAG Pipeline
# ----------------------------

def initialize_pipeline() -> RAGPipeline:
    """
    Initializes the RAG pipeline.
    """
    try:
        rag = RAGPipeline()
        logger.info("RAG Pipeline initialized successfully.")
        return rag

    except Exception as e:
        logger.error(f"Failed to initialize RAG pipeline: {str(e)}")
        raise


# ----------------------------
# Process Query
# ----------------------------

def process_query(rag: RAGPipeline, query: str) -> str:
    """
    Validates and processes user query through RAG pipeline.
    """

    try:
        # Validate input
        validate_query(query)

        # Clean query
        query = clean_text(query)

        # Check if finance-related
        if not is_financial_query(query):
            logger.warning("Non-financial query detected.")

        logger.info(f"Processing query: {query}")

        # Run RAG pipeline
        result = rag.run_query(query)
        return result.get("answer", "")

    except ValueError as ve:
        logger.error(f"Validation error: {str(ve)}")
        return str(ve)

    except Exception as e:
        error_msg = str(e) if str(e) else type(e).__name__
        logger.error(f"Error processing query: {error_msg}", exc_info=True)
        return "Something went wrong while processing your request."


# ----------------------------
# CLI Interface
# ----------------------------

def run_cli() -> None:
    """
    Runs command-line interface for user interaction.
    """

    rag: RAGPipeline = initialize_pipeline()

    print("\n📊 Welcome to FinSight - GenAI Financial Analyst")
    print("Type 'exit' to quit.\n")

    while True:
        try:
            user_query: str = input("💬 Enter your query: ")

            if user_query.lower() in ["exit", "quit"]:
                print("👋 Exiting FinSight. Goodbye!")
                break

            response: str = process_query(rag, user_query)

            print("\n📈 Analysis:")
            print(response)
            print("-" * 50)

        except KeyboardInterrupt:
            print("\n👋 Exiting FinSight. Goodbye!")
            break


def run_streamlit() -> None:
    """
    Launches the Streamlit web UI.
    """
    import subprocess
    
    streamlit_app: Path = Path(__file__).parent / "app" / "streamlit_app.py"
    
    logger.info(f"Launching Streamlit app from {streamlit_app}")
    print(f"\n🚀 Launching FinSight Streamlit interface...")
    print(f"   App URL: http://localhost:8501\n")
    print(f"   Backend URL: {API_BASE_URL}\n")

    backend_process = launch_backend()
    if not is_backend_running():
        print("⚠️ Backend status unavailable. Please verify API dependencies/config.")
    
    try:
        streamlit_env = os.environ.copy()
        streamlit_env["API_BASE_URL"] = API_BASE_URL

        subprocess.run(
            [sys.executable, "-m", "streamlit", "run", str(streamlit_app)],
            check=False,
            env=streamlit_env
        )
    except Exception as e:
        logger.error(f"Error launching Streamlit: {e}")
        print(f"❌ Failed to launch Streamlit: {e}")
        print("Make sure Streamlit is installed: pip install streamlit")
    finally:
        if backend_process and backend_process.poll() is None:
            logger.info("Stopping backend API server.")
            backend_process.terminate()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="FinSight - GenAI Financial Analyst Agent"
    )
    parser.add_argument(
        "mode",
        nargs="?",
        default="streamlit",
        choices=["cli", "streamlit"],
        help="Launch mode: 'cli' for command-line interface, 'streamlit' for web UI (default: streamlit)"
    )
    
    args: argparse.Namespace = parser.parse_args()
    
    if args.mode == "streamlit":
        run_streamlit()
    else:
        run_cli()