import os
import sys
from pathlib import Path
from typing import List, Dict

from pdfplumber.pdf import PDF

# Allow running this module directly (python parser_service.py) from nested paths.
if __package__ in (None, ""):
    project_root: Path = Path(__file__).resolve().parents[2]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

try:
    import pdfplumber
except ImportError:
    raise ImportError(
        "pdfplumber is required. Install with `pip install pdfplumber`"
    )

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

try:
    from FinSight.app.config import settings
except ModuleNotFoundError:
    from app.config import settings


class PDFParserService:
    """
    Handles PDF parsing, text extraction, and chunking using pdfplumber
    """

    def __init__(self) -> None:
        self.chunk_size: int = settings.CHUNK_SIZE
        self.chunk_overlap: int = settings.CHUNK_OVERLAP

    # -------------------------------
    # Main function: Parse PDF
    # -------------------------------
    def parse_pdf(self, file_path: str) -> List[Dict]:
        """
        Extract text from PDF and return chunked documents with metadata.
        Tries pdfplumber first, then falls back to pypdf for difficult PDFs.
        """

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        filename: str = os.path.basename(file_path)

        # Primary parser: pdfplumber (usually better layout extraction).
        try:
            documents = self._parse_with_pdfplumber(file_path, filename)
            if documents:
                return documents
            print(f"[WARN] pdfplumber extracted no text for {filename}. Trying pypdf fallback.", file=sys.stderr)
        except KeyboardInterrupt:
            print(f"[WARN] Interrupted while processing {filename}", file=sys.stderr)
            raise
        except Exception as exc:
            print(f"[WARN] pdfplumber failed for {filename}: {type(exc).__name__}. Trying pypdf fallback.", file=sys.stderr)

        # Fallback parser: pypdf (more tolerant for some PDFs).
        return self._parse_with_pypdf(file_path, filename)

    def _parse_with_pdfplumber(self, file_path: str, filename: str) -> List[Dict]:
        documents = []

        with pdfplumber.open(file_path) as pdf:
            total_pages: int = len(pdf.pages)

            for page_num, page in enumerate(pdf.pages, 1):
                try:
                    text: str = page.extract_text()
                    if text and text.strip():
                        chunks: List[str] = self._chunk_text(text)
                        for chunk in chunks:
                            documents.append({
                                "content": chunk,
                                "metadata": {
                                    "source": filename,
                                    "page": page_num
                                }
                            })
                except Exception as exc:
                    print(
                        f"[WARN] pdfplumber page {page_num}/{total_pages} failed: {type(exc).__name__}",
                        file=sys.stderr,
                    )
                    continue

        return documents

    def _parse_with_pypdf(self, file_path: str, filename: str) -> List[Dict]:
        if PdfReader is None:
            print(
                "[WARN] pypdf is not installed. Install with `pip install pypdf`.",
                file=sys.stderr,
            )
            return []

        documents = []

        try:
            reader = PdfReader(file_path)
            total_pages: int = len(reader.pages)
            for page_num, page in enumerate(reader.pages, 1):
                try:
                    text: str = page.extract_text() or ""
                    if text.strip():
                        chunks: List[str] = self._chunk_text(text)
                        for chunk in chunks:
                            documents.append({
                                "content": chunk,
                                "metadata": {
                                    "source": filename,
                                    "page": page_num
                                }
                            })
                except Exception as exc:
                    print(
                        f"[WARN] pypdf page {page_num}/{total_pages} failed: {type(exc).__name__}",
                        file=sys.stderr,
                    )
                    continue
        except KeyboardInterrupt:
            print(f"[WARN] Interrupted while processing {filename}", file=sys.stderr)
            raise
        except Exception as exc:
            print(f"[WARN] pypdf failed for {filename}: {type(exc).__name__}", file=sys.stderr)
            return []

        return documents

    # -------------------------------
    # Chunking logic
    # -------------------------------
    def _chunk_text(self, text: str) -> List[str]:
        """
        Splits text into overlapping chunks
        """

        chunks = []
        start = 0
        text_length: int = len(text)

        while start < text_length:
            end: int = start + self.chunk_size
            chunk: str = text[start:end]

            if chunk.strip():  # avoid empty chunks
                chunks.append(chunk)

            start += self.chunk_size - self.chunk_overlap

        return chunks

    # -------------------------------
    # Save processed chunks (optional)
    # -------------------------------
    def save_processed_data(self, documents: List[Dict], filename: str) -> None:
        """
        Save processed chunks to file (for debugging or reuse)
        """

        import json

        save_path: str = os.path.join(settings.PROCESSED_DATA_DIR, f"{filename}.json")

        os.makedirs(settings.PROCESSED_DATA_DIR, exist_ok=True)

        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(documents, f, indent=2, ensure_ascii=False)

    # -------------------------------
    # Process multiple PDFs
    # -------------------------------
    def parse_multiple_pdfs(self, file_paths: List[str]) -> List[Dict]:
        """
        Process multiple PDF files
        """

        all_documents = []

        for path in file_paths:
            docs = self.parse_pdf(path)
            all_documents.extend(docs)

        return all_documents