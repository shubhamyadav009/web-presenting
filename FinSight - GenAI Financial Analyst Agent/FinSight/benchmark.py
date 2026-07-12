#!/usr/bin/env python
"""
benchmark.py

Quick performance profiler to identify which operations are slow.

Usage:
  python benchmark.py          # Run all benchmarks
  python benchmark.py embed    # Test only embedding speed
  python benchmark.py ingest   # Test ingestion speed
  python benchmark.py llm      # Test LLM generation speed
"""

import sys
import time
import argparse
from pathlib import Path

if __package__ in (None, ""):
    project_root = Path(__file__).resolve().parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

from FinSight.app.config import settings

# Color output
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"


def benchmark_embeddings():
    """Test embedding generation speed."""
    print(f"\n{YELLOW}=== EMBEDDING BENCHMARK ==={RESET}")
    print("Testing both Ollama and HuggingFace embedders...\n")

    test_texts = [
        "Revenue increased by 25% year-over-year due to strong market demand.",
        "EBITDA margin improved to 18% from 15% in the previous period.",
        "Operating cash flow reached $500M, up 40% from last quarter.",
    ] * 3  # 9 texts

    # Test 1: Original Ollama embedder
    print("1️⃣ Testing ORIGINAL Ollama embedder (sequential)...")
    try:
        from FinSight.core.rag.embeddings import EmbeddingGenerator
        
        start = time.time()
        embedder_ollama = EmbeddingGenerator()
        init_time = time.time() - start
        
        start = time.time()
        result = embedder_ollama.generate_embeddings(test_texts)
        embed_time = time.time() - start
        
        rate_ollama = len(test_texts) / embed_time if embed_time > 0 else 0
        print(f"   Init: {init_time:.2f}s | Embed {len(test_texts)} texts: {embed_time:.2f}s ({rate_ollama:.1f} texts/sec)")
        print(f"   ⚠️  Sequential = SLOW for large batches (50-100 min for 1000 chunks)")
    except Exception as e:
        print(f"   ❌ Failed: {e}")

    # Test 2: Optimized embedder with HuggingFace
    print("\n2️⃣ Testing OPTIMIZED embedder (HuggingFace local)...")
    try:
        from FinSight.core.rag.embeddings_optimized import EmbeddingGeneratorOptimized
        
        start = time.time()
        embedder_hf = EmbeddingGeneratorOptimized(use_huggingface=True)
        init_time = time.time() - start
        
        start = time.time()
        result = embedder_hf.generate_embeddings(test_texts, show_progress=False)
        embed_time = time.time() - start
        
        rate_hf = len(test_texts) / embed_time if embed_time > 0 else 0
        provider_note = "HuggingFace" if embedder_hf.use_huggingface else "Ollama (parallel)"
        print(f"   Init: {init_time:.2f}s | Embed {len(test_texts)} texts: {embed_time:.2f}s ({rate_hf:.1f} texts/sec)")
        print(f"   ✓ Using {provider_note} — FAST for large batches")
        
        if rate_hf > 0 and rate_ollama > 0:
            speedup = rate_ollama / rate_hf
            print(f"\n   🚀 Speedup: {speedup:.1f}x faster than Ollama!")
    except Exception as e:
        print(f"   ❌ Failed: {e}")


def benchmark_pdf_parsing():
    """Test PDF parsing speed."""
    print(f"\n{YELLOW}=== PDF PARSING BENCHMARK ==={RESET}")
    
    from FinSight.services.parser_service import PDFParserService
    from pathlib import Path
    
    raw_dir = Path(settings.RAW_DATA_DIR)
    if not raw_dir.exists():
        print(f"No PDF directory at {raw_dir}")
        return
    
    pdf_files = list(raw_dir.glob("*.pdf"))[:1]  # Test with first PDF
    
    if not pdf_files:
        print(f"No PDF files found in {raw_dir}")
        return
    
    parser = PDFParserService()
    
    for pdf_file in pdf_files:
        print(f"\nParsing: {pdf_file.name}")
        start = time.time()
        try:
            docs = parser.parse_pdf(str(pdf_file))
            elapsed = time.time() - start
            print(f"   Parsed into {len(docs)} chunks in {elapsed:.2f}s")
            print(f"   Rate: {len(docs)/elapsed:.1f} chunks/sec")
        except Exception as e:
            print(f"   ❌ Error: {e}")


def benchmark_llm():
    """Test LLM generation speed."""
    print(f"\n{YELLOW}=== LLM BENCHMARK ==={RESET}")
    
    from FinSight.services.llm_service import LLMService
    
    try:
        llm = LLMService()
        
        prompt = (
            "Based on the financial data provided, what are the key investment risks? "
            "Respond in 2 sentences."
        )
        
        print(f"\nGenerating LLM response...")
        start = time.time()
        response = llm._generate(prompt)
        elapsed = time.time() - start
        
        print(f"   Prompt length: {len(prompt)} chars")
        print(f"   Response length: {len(response)} chars")
        print(f"   Time: {elapsed:.2f}s")
        print(f"   Response: {response[:100]}...")
        
        if elapsed > 30:
            print(f"   ⚠️  LLM generation is SLOW ({elapsed:.1f}s) — consider using faster model")
        else:
            print(f"   ✓ LLM generation is reasonable ({elapsed:.1f}s)")
    except Exception as e:
        print(f"   ❌ Error: {e}")


def benchmark_rag_query():
    """Test end-to-end query speed."""
    print(f"\n{YELLOW}=== RAG QUERY BENCHMARK ==={RESET}")
    
    from FinSight.core.rag.pipeline import RAGPipeline
    
    try:
        pipeline = RAGPipeline()
        
        query = "What were the key revenue drivers this year?"
        
        print(f"\nProcessing query: '{query}'")
        start = time.time()
        result = pipeline.run_query(query)
        elapsed = time.time() - start
        
        print(f"   Total time: {elapsed:.2f}s")
        print(f"   Answer: {result.get('answer', 'N/A')[:100]}...")
        
        if elapsed > 30:
            print(f"   ⚠️  Query is SLOW ({elapsed:.1f}s) — check bottleneck above")
        else:
            print(f"   ✓ Query speed is acceptable")
    except Exception as e:
        print(f"   ❌ Error: {e}")


def main():
    parser = argparse.ArgumentParser(description="FinSight Performance Benchmark")
    parser.add_argument(
        "test",
        nargs="?",
        default="all",
        choices=["all", "embed", "pdf", "llm", "query"],
        help="Which benchmark to run"
    )
    
    args = parser.parse_args()
    
    print(f"\n{GREEN}FinSight Performance Benchmark{RESET}")
    print(f"Configured provider: {settings.LLM_PROVIDER}")
    print(f"Embedding model: {settings.EMBEDDING_MODEL}")
    print(f"LLM model: {settings.LLM_MODEL}")
    
    if args.test in ("all", "embed"):
        benchmark_embeddings()
    
    if args.test in ("all", "pdf"):
        benchmark_pdf_parsing()
    
    if args.test in ("all", "llm"):
        benchmark_llm()
    
    if args.test in ("all", "query"):
        benchmark_rag_query()
    
    print(f"\n{GREEN}Benchmark Complete{RESET}\n")
    print("💡 Recommendations:")
    print("   1. If embeddings are slow: Use HuggingFace local (install sentence-transformers)")
    print("   2. If PDF parsing is slow: Use --mode processed (skip parsing)")
    print("   3. If LLM is slow: Use faster model (mistral vs llama2-70b)")
    print("   4. See PERFORMANCE_OPTIMIZATION.md for detailed guide")


if __name__ == "__main__":
    main()
