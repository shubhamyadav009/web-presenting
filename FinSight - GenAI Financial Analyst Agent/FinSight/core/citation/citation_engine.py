from typing import List, Dict


class CitationEngine:
    """
    Handles citation extraction and formatting
    """

    def __init__(self):
        pass

    # -------------------------------
    # Extract citations from retrieved docs
    # -------------------------------
    def extract_citations(self, documents: List[Dict]) -> List[Dict]:
        """
        Input: List of retrieved document chunks
        Each document should have:
        {
            "content": "...",
            "metadata": {
                "source": "file_name.pdf",
                "page": 12
            }
        }

        Output:
        [
            {
                "source": "file_name.pdf",
                "page": 12,
                "text": "relevant snippet..."
            }
        ]
        """
        citations = []

        for doc in documents:
            metadata = doc.get("metadata", {})
            content = doc.get("content", "")

            citation = {
                "source": metadata.get("source", "Unknown"),
                "page": metadata.get("page", "N/A"),
                "text": content[:300]  # limit snippet length
            }

            citations.append(citation)

        return citations

    # -------------------------------
    # Format citations for display
    # -------------------------------
    def format_citations(self, citations: List[Dict]) -> List[str]:
        """
        Converts citations into readable strings for UI
        """
        formatted = []

        for cite in citations:
            text_preview = cite["text"].replace("\n", " ").strip()

            formatted_str = (
                f"📄 {cite['source']} | Page {cite['page']}:\n"
                f"\"{text_preview}...\""
            )

            formatted.append(formatted_str)

        return formatted

    # -------------------------------
    # Remove duplicate citations
    # -------------------------------
    def deduplicate_citations(self, citations: List[Dict]) -> List[Dict]:
        """
        Removes duplicate citations based on source + page
        """
        seen = set()
        unique_citations = []

        for cite in citations:
            key = (cite["source"], cite["page"])

            if key not in seen:
                seen.add(key)
                unique_citations.append(cite)

        return unique_citations