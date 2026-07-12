#!/usr/bin/env python
"""Test just the retrieval part"""
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

print("Testing Document Retrieval...")

# Test retrieval
from FinSight.core.rag.embeddings_optimized import EmbeddingGeneratorOptimized
from FinSight.services.vector_db_service import VectorDBService

embedder = EmbeddingGeneratorOptimized(use_huggingface=True)
vdb = VectorDBService()

query = "What is revenue?"
print(f"\n1. Generating embedding for: '{query}'")
query_embedding = embedder.generate_query_embedding(query)
print(f"   ✓ Embedding generated (length: {len(query_embedding)})")

print(f"\n2. Retrieving top-5 documents from {len(vdb.documents)} total...")
print(f"   Index dimensions: {vdb.index.d if vdb.index else 'N/A'}")
print(f"   Query embedding dimensions: {len(query_embedding)}")
try:
    retrieved_docs = vdb.search(query_embedding, top_k=5)
    print(f"   ✓ Retrieved {len(retrieved_docs)} documents")
    for i, doc in enumerate(retrieved_docs[:3], 1):
        print(f"\n   Document {i}:")
        print(f"   - Source: {doc.get('source', 'unknown')}")
        print(f"   - Content: {doc.get('content', '')[:100]}...")
except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n✓ Retrieval test complete")
