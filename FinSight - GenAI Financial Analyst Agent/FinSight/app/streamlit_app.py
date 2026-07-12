import streamlit as st
import requests
import os

# This file defines the Streamlit UI only.
# It is launched from main.py, not directly.
# To launch: python main.py streamlit

# -------------------------------
# CONFIG
# -------------------------------
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")

st.set_page_config(
    page_title="FinSight",
    layout="wide"
)

# -------------------------------
# TITLE
# -------------------------------
st.title("📊 FinSight – AI Financial Analyst")
st.markdown("Analyze annual reports, compare companies, and generate insights.")


def load_backend_status():
    try:
        response = requests.get(f"{API_BASE_URL}/status", timeout=10)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.Timeout:
        return None
    except requests.exceptions.ConnectionError:
        return None
    except Exception:
        return None
    return None

# -------------------------------
# SIDEBAR - FILE UPLOAD
# -------------------------------
st.sidebar.header("📂 Upload Financial Reports")

status_data = load_backend_status()
st.sidebar.subheader("🛠️ System Status")
if status_data:
    embedding_ready = status_data.get("embedding_ready", status_data.get("openai_embedding_ready", False))
    llm_ready = status_data.get("llm_ready", status_data.get("openai_llm_ready", False))

    st.sidebar.write(f"Provider: {status_data.get('llm_provider', 'unknown')}")
    st.sidebar.write(f"LLM Model: {status_data.get('llm_model', 'unknown')}")
    st.sidebar.write(f"Embedding Model: {status_data.get('embedding_model', 'unknown')}")
    st.sidebar.write(
        f"Embedding API: {'Ready' if embedding_ready else 'Not Ready'}"
    )
    st.sidebar.write(
        f"LLM API: {'Ready' if llm_ready else 'Not Ready'}"
    )
    st.sidebar.write(f"Indexed Chunks: {status_data.get('indexed_chunks', 0)}")
else:
    st.sidebar.warning("Backend status unavailable")

if st.sidebar.button("🔄 Reconnect Backend"):
    status_data = load_backend_status()
    if status_data:
        st.sidebar.success("Backend reconnected ✅")
        st.rerun()
    else:
        st.sidebar.error("Failed to reconnect. Backend may be offline.")

if st.sidebar.button("Reindex Existing PDFs"):
    try:
        st.sidebar.info("⏳ Reindexing... This may take several minutes...")
        response = requests.post(f"{API_BASE_URL}/reindex", timeout=600)  # 10 minute timeout
        if response.status_code == 200:
            payload = response.json()
            st.sidebar.success(payload.get("message", "Reindex complete"))
            st.sidebar.info(f"Indexed {payload.get('chunks_indexed', 0)} chunks")
            status_data = load_backend_status()
        else:
            st.sidebar.error("Reindex failed ❌")
    except requests.exceptions.Timeout:
        st.sidebar.error("Reindex timed out - check backend logs")
    except Exception as e:
        st.sidebar.error(f"Error: {str(e)}")

uploaded_files = st.sidebar.file_uploader(
    "Upload PDF files",
    type=["pdf"],
    accept_multiple_files=True
)

if st.sidebar.button("Upload Files"):
    if uploaded_files:
        files = [("files", (file.name, file, "application/pdf")) for file in uploaded_files]

        try:
            st.sidebar.info("⏳ Uploading and indexing... This may take a few minutes...")
            response = requests.post(f"{API_BASE_URL}/upload", files=files, timeout=300)  # 5 minute timeout

            if response.status_code == 200:
                payload = response.json()
                st.sidebar.success("Files uploaded successfully ✅")
                st.sidebar.info(
                    f"Indexed {payload.get('chunks_indexed', 0)} new chunks"
                )
                status_data = load_backend_status()
            else:
                st.sidebar.error("Upload failed ❌")

        except requests.exceptions.Timeout:
            st.sidebar.error("Upload timed out - files may still be processing")
        except Exception as e:
            st.sidebar.error(f"Error: {str(e)}")
    else:
        st.sidebar.warning("Please upload at least one PDF")

# -------------------------------
# TABS
# -------------------------------
tab1, tab2 = st.tabs(["💬 Ask Questions", "⚔️ Compare Companies"])

# ===============================
# TAB 1: QUERY SYSTEM
# ===============================
with tab1:
    st.subheader("💬 Ask Financial Questions")

    user_query = st.text_input("Enter your question")

    if st.button("Get Answer"):
        if user_query:
            try:
                st.info("🔄 Processing query... This may take 1-2 minutes (LLM is generating response)...")
                
                response = requests.post(
                    f"{API_BASE_URL}/query",
                    params={"question": user_query},
                    timeout=180  # 3 minutes - LLM inference can be slow
                )

                if response.status_code == 200:
                    data = response.json()

                    st.markdown("### 🧠 Answer")
                    st.write(data["answer"])
                    st.caption(f"Source: {data.get('answer_source', 'unknown')}")

                    st.markdown("### 🔍 Citations")
                    if data["citations"]:
                        for cite in data["citations"]:
                            st.write(f"- {cite}")
                    else:
                        st.write("No citations available yet")

                else:
                    st.error(f"Query failed with status {response.status_code}")
                    st.error(f"Response: {response.text[:200]}")

            except requests.exceptions.Timeout:
                st.error("❌ Query timed out! The LLM took too long to respond. Try a simpler question or restart the app.")
            except requests.exceptions.ConnectionError:
                st.error("❌ Backend disconnected! The API server may have crashed. Please refresh and try again.")
            except Exception as e:
                st.error(f"Error: {str(e)}")
        else:
            st.warning("Please enter a question")

# ===============================
# TAB 2: COMPANY COMPARISON
# ===============================
with tab2:
    st.subheader("⚔️ Compare Companies")

    col1, col2 = st.columns(2)

    with col1:
        company_a = st.text_input("Company A")

    with col2:
        company_b = st.text_input("Company B")

    if st.button("Compare"):
        if company_a and company_b:
            try:
                st.info("🔄 Comparing companies... This may take 1-2 minutes...")
                
                response = requests.post(
                    f"{API_BASE_URL}/compare",
                    params={
                        "company_a": company_a,
                        "company_b": company_b
                    },
                    timeout=180  # 3 minutes timeout
                )

                if response.status_code == 200:
                    data = response.json()

                    st.markdown("### 📊 Comparison Analysis")
                    st.write(data["analysis"])

                    st.markdown("### 🏁 Final Verdict")
                    st.success(data["verdict"])

                else:
                    st.error(f"Comparison failed with status {response.status_code}")

            except requests.exceptions.Timeout:
                st.error("❌ Comparison timed out! The LLM took too long. Try again with simpler companies.")
            except requests.exceptions.ConnectionError:
                st.error("❌ Backend disconnected! Please refresh the page.")
            except Exception as e:
                st.error(f"Error: {str(e)}")
        else:
            st.warning("Enter both company names")

# -------------------------------
# FOOTER
# -------------------------------
st.markdown("---")
st.caption("Built with ❤️ using GenAI | FinSight")