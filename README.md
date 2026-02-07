# AI Semantic Analyzer (sentiment-analyzer)

Industrial-grade tool for processing large datasets (CSV/Excel) using LLMs for deep semantic analysis. 

**"Transforming raw text into structured business intelligence for less than a cent."**

## 💼 Business Use Cases (Why it matters)
Traditional automated sentiment analysis fails to capture human nuances. This tool solves that by applying "human-level" reasoning at scale:

*   **Customer Experience (CX)**: Automatically process thousands of product reviews to detect not just sentiment, but specific pain points and sarcasm that standard tools miss.
*   **Market Research**: Analyze competitor mentions, social media discussions, and forum threads to identify emerging trends and demographic shifts (Age/Gender estimation).
*   **Operational Efficiency**: Reduce manual document/feedback review time by 90%+. A task that takes a human team 10 hours now takes 5 minutes for less than $0.01 in API costs.
*   **Brand Monitoring**: Identify "quiet shockwaves" in public discourse before they become PR issues.

## 🚀 The Advantage: Row-by-Row Precision
Unlike batch processing that "summarizes" and loses detail, this engine treats **every single row** as a unique data point. This ensures:
1.  **Zero Context Contamination**: Information from one review doesn't bleed into the next.
2.  **High-Fidelity Sarcasm Detection**: The AI understands tone, slang, and cultural context (e.g., Gen-Z slang vs. Corporate speak).
3.  **Dynamic Tasking**: You can tell the system to look for *anything*—from "Is this user a potential VIP?" to "What feature is this person complaining about exactly?".

## 💰 Economic Impact (The $0.01 Benchmark)
In a real-world test (see `COST_ANALYSIS.md`), processing **147 complex comments** cost approximately **$0.007**. 
- **1,000 rows** ≈ $0.05
- **10,000 rows** ≈ $0.50
The ROI compared to human labor is infinite.

## 🛠 Technical Overview
- **Core Engine**: Multi-threaded Python pipeline.
- **AI Integration**: DeepSeek (Cloud) or Local LLMs (Gemma/Llama) via OpenAI-compatible API.
- **Privacy-First**: Optimized for Local LLMs to handle sensitive PII (Personally Identifiable Information) without internet access.

---
*Developed & Maintained by Ivan Kurilov - System Analyst & AI Automation Specialist.*
