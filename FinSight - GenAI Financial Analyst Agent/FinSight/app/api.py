from fastapi import FastAPI, UploadFile, File, HTTPException
from typing import List
import os
import shutil
import sys
from pathlib import Path

# Allow running this module directly (python api.py) from nested paths.
if __package__ in (None, ""):
    project_root: Path = Path(__file__).resolve().parents[2]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

from FinSight.core.rag.pipeline import RAGPipeline
from FinSight.services.parser_service import PDFParserService
from FinSight.app.config import settings

# Initialize FastAPI app
app = FastAPI(
    title="FinSight API",
    description="AI-Powered Financial Due Diligence Assistant",
    version="1.0.0"
)

# Define upload directory
UPLOAD_DIR = "data/raw"
os.makedirs(UPLOAD_DIR, exist_ok=True)

rag_pipeline = RAGPipeline()
pdf_parser = PDFParserService()


def _index_pdf_files(file_paths: List[str], reset_first: bool = False) -> int:
    if reset_first:
        rag_pipeline.vector_db.reset()

    total_chunks = 0

    for file_path in file_paths:
        documents = pdf_parser.parse_pdf(file_path)
        total_chunks += len(documents)

        if rag_pipeline.embedder:
            embeddings: List[List[float]] = rag_pipeline.embedder.generate_embeddings(
                [doc["content"] for doc in documents]
            )
        else:
            embeddings = []

        rag_pipeline.vector_db.add_documents(documents, embeddings)

    return total_chunks


def _raw_pdf_paths() -> List[str]:
    return [
        os.path.join(UPLOAD_DIR, name)
        for name in os.listdir(UPLOAD_DIR)
        if name.lower().endswith(".pdf") and os.path.isfile(os.path.join(UPLOAD_DIR, name))
    ]


# If persisted index/docstore is empty but raw PDFs exist, bootstrap indexing.
if len(rag_pipeline.vector_db.documents) == 0:
    existing_pdf_files: List[str] = _raw_pdf_paths()
    if existing_pdf_files:
        _index_pdf_files(existing_pdf_files, reset_first=True)


# -------------------------------
# Health Check
# -------------------------------
@app.get("/")
def health_check() -> dict[str, str]:
    return {"status": "FinSight API is running 🚀"}


@app.get("/status")
def app_status():
    embedding_error: str = ""
    llm_error: str = ""

    if rag_pipeline.embedder and hasattr(rag_pipeline.embedder, "last_error"):
        embedding_error: str = rag_pipeline.embedder.last_error

    if rag_pipeline.llm and hasattr(rag_pipeline.llm, "last_error"):
        llm_error: str = rag_pipeline.llm.last_error

    return {
        "llm_provider": settings.LLM_PROVIDER,
        "llm_model": settings.LLM_MODEL,
        "embedding_model": settings.EMBEDDING_MODEL,
        "embedding_ready": rag_pipeline.embedder is not None,
        "llm_ready": rag_pipeline.llm is not None,
        "indexed_chunks": len(rag_pipeline.vector_db.documents),
        "vector_index_ready": rag_pipeline.vector_db.index is not None,
        "embedding_last_error": embedding_error,
        "llm_last_error": llm_error
    }


@app.post("/reindex")
def reindex_documents():
    try:
        file_paths: List[str] = _raw_pdf_paths()
        if not file_paths:
            return {
                "message": "No PDF files found in data/raw.",
                "files": [],
                "chunks_indexed": 0
            }

        chunks_indexed: int = _index_pdf_files(file_paths, reset_first=True)
        return {
            "message": "Reindex completed successfully",
            "files": [os.path.basename(path) for path in file_paths],
            "chunks_indexed": chunks_indexed
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------
# Upload PDF Endpoint
# -------------------------------
@app.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    saved_files = []
    total_chunks = 0

    try:
        for file in files:
            if not file.filename.endswith(".pdf"):
                raise HTTPException(status_code=400, detail="Only PDF files are allowed")

            file_path = os.path.join(UPLOAD_DIR, file.filename)

            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            total_chunks += _index_pdf_files([file_path], reset_first=False)
            saved_files.append(file.filename)

        return {
            "message": "Files uploaded successfully",
            "files": saved_files,
            "chunks_indexed": total_chunks
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------
# Query Endpoint
# -------------------------------
@app.post("/query")
async def query_system(question: str):
    try:
        result = rag_pipeline.run_query(question)

        return {
            "question": question,
            "answer": result.get("answer", "No answer generated."),
            "citations": result.get("citations", []),
            "answer_source": result.get("source", "unknown")
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------
# Compare Companies Endpoint (Placeholder)
# -------------------------------
@app.post("/compare")
async def compare_companies(company_a: str, company_b: str) -> dict[str, str]:
    """
    This will later connect to finance comparator
    """
    try:
        return {
            "company_a": company_a,
            "company_b": company_b,
            "analysis": "Comparison logic not implemented yet.",
            "verdict": "Pending"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))