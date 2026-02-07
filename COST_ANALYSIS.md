# AI Semantic Analyzer - Cost Analysis

### Processing 147 Rows of Real Data (Jan 2026)
- **Tool**: `analyzer.py` + DeepSeek API
- **Task**: Sentiment, Sarcasm detection, Topic classification.
- **Total Cost**: **< $0.01** (approximately 0.007 USD)

### Token Breakdown:
- **Input (Cache Hit)**: 9,088 tokens (Prompt templates & repeating instructions)
- **Input (Cache Miss)**: 23,720 tokens (Unique row content)
- **Output**: 4,659 tokens (Generated JSON results)

### Why it's a "No-Brainer":
1. **Row-by-Row Isolation**: By processing each row individually, we ensure zero context leakage. The AI treats every customer/comment as a unique entity, ensuring high accuracy even for complex sarcasm.
2. **DeepSeek Cache Optimization**: Using a consistent prompt structure allows the API to cache the "system instructions," making subsequent calls significantly cheaper and faster.
3. **Massive ROI**: Manually analyzing 1000 reviews takes ~10-15 hours of human work. This tool does it for cents in minutes.

---
*Maintained by Ivan Kurilov - System Analyst & AI Automation Specialist.*
