#!/usr/bin/env python
"""Check which embedder the pipeline is using"""
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

print("Checking Pipeline Embedder...")

from FinSight.core.rag.pipeline import RAGPipeline
p = RAGPipeline()

print(f"\nEmbedder:")
print(f"  - Class: {type(p.embedder).__name__}")
print(f"  - Module: {type(p.embedder).__module__}")
print(f"  - Using HF: {getattr(p.embedder, 'use_huggingface', 'N/A')}")

# Try embedding
print(f"\nTesting embedding generation...")
try:
    result = p.embedder.generate_query_embedding('What is profit?')
    print(f"  ✓ Generated {len(result)}-dimension embedding")
except Exception as e:
    print(f"  ✗ Error: {e}")

# Try query
print(f"\nTesting full query...")
try:
    import time
    start = time.time()
    result = p.run_query("What is profit?")
    elapsed = time.time() - start
    
    print(f"  Time taken: {elapsed:.2f}s")
    print(f"  Answer: {result.get('answer', 'NO ANSWER')[:100]}...")
    print(f"  Source: {result.get('source')}")
    print(f"  Citations: {len(result.get('citations', []))} found")
except Exception as e:
    print(f"  ✗ Error: {e}")
    import traceback
    traceback.print_exc()
