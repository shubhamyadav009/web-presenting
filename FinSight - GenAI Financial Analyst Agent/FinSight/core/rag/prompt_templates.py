class PromptTemplates:
    """
    Stores all prompt templates used in the RAG pipeline
    """

    # -------------------------------
    # Basic Q&A Prompt
    # -------------------------------
    @staticmethod
    def qa_prompt(query: str, context: str) -> str:
        return f"""
You are a financial analyst assistant.

Use ONLY the provided context to answer the question.
If the answer is not in the context, say "Information not available in the document."

Context:
{context}

Question:
{query}

Answer:
"""

    # -------------------------------
    # Financial Analysis Prompt
    # -------------------------------
    @staticmethod
    def financial_analysis_prompt(context: str) -> str:
        return f"""
You are an expert financial analyst.

Analyze the following financial data extracted from company reports.

Context:
{context}

Provide:
1. Key financial observations
2. Profitability insights
3. Risk factors
4. Overall performance summary

Answer in clear bullet points.
"""

    # -------------------------------
    # Comparative Analysis Prompt
    # -------------------------------
    @staticmethod
    def comparison_prompt(context: str, company_a: str, company_b: str) -> str:
        return f"""
You are a financial analyst comparing two companies.

Context:
{context}

Compare {company_a} and {company_b} based on:
- Revenue
- Profitability
- Debt levels
- Operational efficiency

Provide:
1. Metric-wise comparison
2. Key strengths of each company
3. Final verdict (which is financially stronger and why)

Be concise and structured.
"""

    # -------------------------------
    # Insight Generation Prompt
    # -------------------------------
    @staticmethod
    def insight_prompt(context: str) -> str:
        return f"""
You are a financial analyst.

From the following financial data, generate 3-5 key insights.

Focus on:
- Profitability
- Risk
- Growth signals

Context:
{context}

Answer in bullet points.
"""

    # -------------------------------
    # Recommendation Prompt
    # -------------------------------
    @staticmethod
    def recommendation_prompt(context: str) -> str:
        return f"""
You are an investment analyst.

Based on the following financial information:

{context}

Provide:
1. Investment recommendation (Buy / Hold / Sell)
2. Confidence level (High / Medium / Low)
3. Reasoning

Be concise and professional.
"""