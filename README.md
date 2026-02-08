# AI Semantic Analyzer 🧠📊

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![DeepSeek](https://img.shields.io/badge/AI-DeepSeek_V3-blueviolet?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Production_Ready-success?style=for-the-badge)

**Transform raw chaos into structured business intelligence.**  
*High-performance, multi-threaded semantic analysis engine for CSV/Excel datasets.*

[Get Started](#-quick-start) • [How It Works](#-architecture) • [Examples](#-use-cases)

</div>

---

## 🌪 The Problem
You have **10,000 customer reviews** or survey responses.
- **Manual review?** Takes weeks. Expensive. Biased.
- **Classic keyword search?** Misses sarcasm ("Great service... NOT"), context, and implicit intent.
- **Generic AI tools?** Often hallucinate or fail to output structured data you can actually use in Excel.

## ⚡ The Solution
**AI Semantic Analyzer** is an industrial-grade pipeline that treats every row as a unique mission. It uses Large Language Models (LLM) to "read" data like a human expert, but at the speed of software.

| Feature | 🐢 Old Way (Manual/Legacy) | 🚀 AI Semantic Analyzer |
| :--- | :--- | :--- |
| **Speed** | 100 rows / hour | **5,000+ rows / hour** |
| **Cost** | $$$ (Human labor) | **<$0.10 per 1k rows** (DeepSeek/Gemma) |
| **Depth** | Surface level | **Deep psychological profiling** |
| **Output** | Vague notes | **Strict JSON / Structured Columns** |

---

## 🏗 Architecture

The system uses a **Scatter-Gather** pattern to process data in parallel, ensuring maximum throughput without rate-limit bottlenecks.

```mermaid
graph LR
    A[📄 Raw CSV/Excel] --> B{⚡ ThreadPool Orchestrator}
    B --> C[🤖 Agent 1]
    B --> D[🤖 Agent 2]
    B --> E[🤖 Agent 3]
    B --> F[🤖 Agent 4]
    C & D & E & F --> G[🧠 LLM Inference (DeepSeek/GPT)]
    G --> H[📦 JSON Extraction]
    H --> I[📊 Final Structured Dataset]
```

## 🔥 Key Features

- **🚀 Multi-Threaded Engine**: Utilizing Python's `ThreadPoolExecutor` to saturate API limits safely.
- **🎯 Strict JSON Enforcement**: The prompt engineering ensures 100% machine-readable output. No "Here is the analysis" chatter—just data.
- **🛡 Context Isolation**: Every row is analyzed independently. No bleeding of context between customers.
- **🔌 LLM Agnostic**: Optimized for **DeepSeek V3** (best cost/performance), but compatible with OpenAI GPT-4, Claude, or local Ollama/Llama models.

---

## 🚀 Quick Start

### 1. Clone & Install
```bash
git clone https://github.com/Maatq1544/ai-semantic-analyzer.git
cd ai-semantic-analyzer
pip install pandas openai openpyxl
```

### 2. Configure API
Open `analyzer.py` and set your API key (or use environment variables for security):
```python
DEEPSEEK_API_KEY = "your-key-here"
```

### 3. Run Analysis
Run the script with your file and a natural language task description.

```bash
python analyzer.py "reviews.csv" "Analyze sentiment (Positive/Negative), detect Sarcasm (true/false), and extract Main_Complaint."
```

---

## 💡 Use Cases & Examples

### Scenario A: E-Commerce Feedback
**Input Row:**
> "Oh fantastic, another update that breaks the login button. Just what I needed on a Monday."

**Task:**
> "Extract sentiment, check for sarcasm, and identify the broken feature."

**Output:**
```json
{
  "sentiment": "Negative",
  "sarcasm": true,
  "broken_feature": "Login Button",
  "urgency": "High"
}
```

### Scenario B: Lead Scoring
**Input Row:**
> "We are looking to replace our enterprise CRM for 500 seats next quarter. Budget is flexible."

**Task:**
> "Identify intent, company size, and budget sensitivity."

**Output:**
```json
{
  "intent": "Purchase",
  "company_size": "Enterprise (500 seats)",
  "budget_sensitivity": "Low",
  "lead_score": 95
}
```

---

## 🛠 Roadmap
- [ ] **GUI Interface**: Simple web UI for drag-and-drop analysis.
- [ ] **Local Mode**: Native integration with Ollama for offline processing.
- [ ] **Smart Batching**: Dynamic batch sizing to optimize token usage further.

---

<div align="center">

**Built with 🦾 by Tommy Norris & Ivan Kurilov**
*Efficient. Brutal. Effective.*

</div>
