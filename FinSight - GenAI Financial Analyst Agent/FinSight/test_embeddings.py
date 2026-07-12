#!/usr/bin/env python
"""Test embeddings and queries"""
import sys
from pathlib import Path

# Setup path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

print("=" * 60)
print("TESTING EMBEDDINGS AND QUERIES")
print("=" * 60)

# Test 1: Check Ollama
print("\n1️⃣ Checking Ollama API...")
try:
    import requests
    resp = requests.get('http://127.0.0.1:11434/api/tags', timeout=5)
    if resp.status_code == 200:
        data = resp.json()
        models = data.get('models', [])
        print(f"   ✓ Ollama running with {len(models)} models")
        for m in models[:2]:
            print(f"     - {m.get('name')}")
    else:
        print(f"   ✗ Ollama returned status {resp.status_code}")
except Exception as e:
    print(f"   ✗ Ollama not available: {e}")

# Test 2: Check embedder
print("\n2️⃣ Testing EmbeddingGeneratorOptimized...")
try:
    from FinSight.core.rag.embeddings_optimized import EmbeddingGeneratorOptimized
    emb = EmbeddingGeneratorOptimized(use_huggingface=True)
    print(f"   ✓ Initialized. Using HuggingFace: {emb.use_huggingface}")
    
    # Try to generate embedding
    embedding = emb.generate_query_embedding("test query")
    if embedding and len(embedding) > 0:
        print(f"   ✓ Generated embedding (length: {len(embedding)})")
    else:
        print(f"   ✗ Embedding is empty")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 3: Check Vector DB
print("\n3️⃣ Checking Vector Database...")
try:
    from FinSight.services.vector_db_service import VectorDBService
    vdb = VectorDBService()
    print(f"   ✓ VectorDB initialized")
    print(f"     - Documents: {len(vdb.documents)}")
    print(f"     - Index ready: {vdb.index is not None}")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 4: Try a query
print("\n4️⃣ Testing Query through Pipeline...")
try:
    from FinSight.core.rag.pipeline import RAGPipeline
    pipeline = RAGPipeline()
    print(f"   ✓ Pipeline initialized")
    print(f"     - Embedder ready: {pipeline.embedder is not None}")
    print(f"     - LLM ready: {pipeline.llm is not None}")
    print(f"     - Docs in DB: {len(pipeline.vector_db.documents)}")
    
    # Try query
    print("\n   Running query: 'What is revenue?'...")
    result = pipeline.run_query("What is revenue?")
    
    print(f"   Answer: {result.get('answer', 'ERROR')[:100]}...")
    if result.get('source') == 'fallback_no_documents':
        print("   ✗ Query failed - using fallback (no documents found)")
    else:
        print(f"   ✓ Query successful - source: {result.get('source')}")
        
except Exception as e:
    import traceback
    print(f"   ✗ Error: {e}")
    traceback.print_exc()

print("\n" + "=" * 60)
