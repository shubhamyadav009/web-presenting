"""
ingest_data.py

Unified script to process PDFs into embeddings and index them.

Modes:
  pdf        - Parse PDFs using configured embedder (default, slower but uses your model)
  pdf-fast   - Parse PDFs using HuggingFace sentence-transformers (faster)
  processed  - Load from pre-processed JSON files (fastest, skips problematic PDFs)

Usage:
  python ingest_data.py                    # Default: pdf mode
  python ingest_data.py --mode pdf         # Explicit pdf mode
  python ingest_data.py --mode pdf-fast    # Fast mode
  python ingest_data.py --mode processed   # From processed JSON files
"""

import sys
import argparse
import json
from pathlib import Path
from dotenv import load_dotenv

# Allow running this module directly from nested paths
if __package__ in (None, ""):
    project_root = Path(__file__).resolve().parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

load_dotenv()

from FinSight.app.config import settings
from FinSight.services.parser_service import PDFParserService
from FinSight.services.vector_db_service import VectorDBService
from FinSight.utils.logger import get_logger

logger = get_logger(__name__)

# Try to import optional HuggingFace embeddings
try:
    from sentence_transformers import SentenceTransformer
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False


def ingest_pdf_default():
    """
    Ingest PDFs using configured embedder (likely Ollama or OpenAI)
    """
    from FinSight.core.rag.embeddings import EmbeddingGenerator
    
    parser = PDFParserService()
    embedder = EmbeddingGenerator()
    vector_db = VectorDBService()
    
    raw_data_path = Path(settings.RAW_DATA_DIR)
    
    if not raw_data_path.exists():
        logger.error(f"Raw data directory not found: {raw_data_path}")
        return
    
    pdf_files = list(raw_data_path.glob("*.pdf"))
    
    if not pdf_files:
        logger.warning(f"No PDF files found in {raw_data_path}")
        return
    
    logger.info(f"Found {len(pdf_files)} PDF files to process")
    all_documents = []
    
    # Process each PDF
    for pdf_file in pdf_files:
        try:
            logger.info(f"Processing: {pdf_file.name}")
            documents = parser.parse_pdf(str(pdf_file))
            
            if documents:
                all_documents.extend(documents)
                logger.info(f"  [OK] Extracted {len(documents)} chunks from {pdf_file.name}")
                
                filename = pdf_file.stem
                parser.save_processed_data(documents, filename)
                logger.info(f"  [OK] Saved processed data to data/processed/{filename}.json")
            else:
                logger.warning(f"  [WARN] No text extracted from {pdf_file.name}")
            
        except KeyboardInterrupt:
            logger.warning("Processing interrupted by user")
            break
        except Exception as e:
            logger.error(f"Error processing {pdf_file.name}: {type(e).__name__} - {str(e)[:100]}")
            logger.info(f"  [SKIP] Continuing with indexing successful PDFs...")
            continue
    
    if not all_documents:
        logger.error("No documents to index")
        return
    
    logger.info(f"\nTotal documents extracted: {len(all_documents)}")
    logger.info("Generating embeddings...")
    
    try:
        if not embedder:
            logger.error("Embedding generator not available")
            return
        
        embeddings = embedder.generate_embeddings([doc["content"] for doc in all_documents])
        logger.info(f"[OK] Generated {len(embeddings)} embeddings")
        
        logger.info("Indexing documents in vector database...")
        vector_db.add_documents(all_documents, embeddings)
        logger.info(f"[OK] Successfully indexed {len(all_documents)} documents")
        
    except Exception as e:
        logger.error(f"Error during embedding/indexing: {type(e).__name__} - {str(e)}")
        return
    
    _print_success(all_documents)


def ingest_pdf_fast():
    """
    Ingest PDFs using HuggingFace sentence-transformers (faster)
    """
    if not HAS_SENTENCE_TRANSFORMERS:
        logger.error("sentence-transformers is required for fast ingestion")
        logger.info("Install with: pip install sentence-transformers")
        return
    
    parser = PDFParserService()
    vector_db = VectorDBService()
    
    raw_data_path = Path(settings.RAW_DATA_DIR)
    
    if not raw_data_path.exists():
        logger.error(f"Raw data directory not found: {raw_data_path}")
        return
    
    pdf_files = list(raw_data_path.glob("*.pdf"))
    
    if not pdf_files:
        logger.warning(f"No PDF files found in {raw_data_path}")
        return
    
    logger.info(f"Found {len(pdf_files)} PDF files to process")
    logger.info("Using HuggingFace sentence-transformers for fast embedding generation")
    
    all_documents = []
    
    for pdf_file in pdf_files:
        try:
            logger.info(f"Processing: {pdf_file.name}")
            documents = parser.parse_pdf(str(pdf_file))
            
            if documents:
                all_documents.extend(documents)
                logger.info(f"  [OK] Extracted {len(documents)} chunks from {pdf_file.name}")
                
                filename = pdf_file.stem
                parser.save_processed_data(documents, filename)
                logger.info(f"  [OK] Saved processed data to data/processed/{filename}.json")
            else:
                logger.warning(f"  [!] No text extracted from {pdf_file.name}")
            
        except KeyboardInterrupt:
            logger.warning("Processing interrupted by user")
            break
        except Exception as e:
            logger.error(f"Error processing {pdf_file.name}: {type(e).__name__} - {str(e)[:100]}")
            logger.info(f"  [SKIP] Continuing with indexing successful PDFs...")
            continue
    
    if not all_documents:
        logger.error("No documents to index")
        return
    
    logger.info(f"\nTotal documents extracted: {len(all_documents)}")
    logger.info("Loading embedding model...")
    
    try:
        logger.info("Loading 'all-MiniLM-L6-v2' model...")
        embedder = SentenceTransformer('all-MiniLM-L6-v2')
        logger.info("[OK] Model loaded. Generating embeddings for all chunks...")
        
        texts = [doc["content"] for doc in all_documents]
        embeddings = embedder.encode(texts, show_progress_bar=True, convert_to_numpy=False)
        
        logger.info(f"[OK] Generated {len(embeddings)} embeddings")
        logger.info("Indexing documents in vector database...")
        vector_db.add_documents(all_documents, embeddings)
        logger.info(f"[OK] Successfully indexed {len(all_documents)} documents")
        
    except Exception as e:
        logger.error(f"Error during embedding/indexing: {type(e).__name__} - {str(e)}")
        return
    
    _print_success(all_documents)


def ingest_from_processed():
    """
    Load already-processed JSON files and create embeddings (fast, skips problematic PDFs)
    """
    if not HAS_SENTENCE_TRANSFORMERS:
        logger.error("sentence-transformers is required for processed ingestion")
        logger.info("Install with: pip install sentence-transformers")
        return
    
    vector_db = VectorDBService()
    processed_path = Path(settings.PROCESSED_DATA_DIR)
    
    all_documents = []
    
    # Load processed JSON files
    json_files = list(processed_path.glob("*.json"))
    logger.info(f"Found {len(json_files)} processed JSON files")
    
    for json_file in json_files:
        try:
            logger.info(f"Loading: {json_file.name}")
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    all_documents.extend(data)
                    logger.info(f"  [OK] Loaded {len(data)} documents from {json_file.name}")
        except Exception as e:
            logger.error(f"Error loading {json_file.name}: {e}")
            continue
    
    if not all_documents:
        logger.error("No documents found in processed data")
        return
    
    logger.info(f"\nTotal documents to index: {len(all_documents)}")
    logger.info("Loading embedding model...")
    
    try:
        embedder = SentenceTransformer('all-MiniLM-L6-v2')
        logger.info("[OK] Model loaded. Generating embeddings...")
        
        texts = [doc["content"] for doc in all_documents]
        embeddings = embedder.encode(texts, show_progress_bar=True, convert_to_numpy=False, batch_size=32)
        
        logger.info(f"[OK] Generated {len(embeddings)} embeddings")
        logger.info("Indexing documents in vector database...")
        
        vector_db.add_documents(all_documents, embeddings)
        logger.info(f"[OK] Successfully indexed {len(all_documents)} documents")
        
    except Exception as e:
        logger.error(f"Error: {type(e).__name__} - {str(e)}")
        import traceback
        traceback.print_exc()
        return
    
    _print_success(all_documents)


def _print_success(documents):
    """Print success message"""
    logger.info("\n" + "="*60)
    logger.info("Data ingestion completed successfully!")
    logger.info("="*60)
    logger.info(f"Total documents indexed: {len(documents)}")
    logger.info(f"Your RAG pipeline is ready to use!")
    logger.info("\nYou can now:")
    logger.info("  - Run: streamlit run app/streamlit_app.py")
    logger.info("  - Or: python -m uvicorn app.api:app --reload")


def main():
    """Main entry point with CLI argument parsing"""
    parser = argparse.ArgumentParser(
        description="Ingest PDFs or processed data into vector database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python ingest_data.py                    # Default: pdf mode
  python ingest_data.py --mode pdf-fast    # Fast mode with HuggingFace
  python ingest_data.py --mode processed   # From pre-processed JSON
        """
    )
    
    parser.add_argument(
        "--mode",
        choices=["pdf", "pdf-fast", "processed"],
        default="pdf",
        help="Ingestion mode (default: pdf)"
    )
    
    args = parser.parse_args()
    
    logger.info(f"Starting ingestion in '{args.mode}' mode...")
    
    if args.mode == "pdf":
        ingest_pdf_default()
    elif args.mode == "pdf-fast":
        ingest_pdf_fast()
    elif args.mode == "processed":
        ingest_from_processed()


if __name__ == "__main__":
    main()
