# AI Semantic Analyzer — LLM-Powered CSV/Excel Text Classification & Sentiment Analysis Pipeline 🧠📊

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![DeepSeek](https://img.shields.io/badge/AI-DeepSeek_V3-blueviolet?style=for-the-badge)
![OpenAI](https://img.shields.io/badge/LLM-GPT--4%20%7C%20Claude%20%7C%20Ollama-412991?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Production_Ready-success?style=for-the-badge)

**AI-powered semantic text analysis for CSV & Excel files.** 
*Batch sentiment analysis, text classification, survey response processing, and customer feedback extraction — 5,000+ rows per hour.*

[Quick Start](#-quick-start) • [Use Cases](#-use-cases) • [Architecture](#-architecture) • [Who Is This For](#-who-is-this-for)

</div>

---

---

## Quick Start

```bash
# Clone and install dependencies
cd ai-semantic-analyzer
pip install -r requirements.txt

# Set LLM API key (choose one)
export OPENAI_API_KEY="sk-..."
# or
export DEEPSEEK_API_KEY="..."

# Run analysis
python analyzer.py --input data.csv --output analyzed.csv --batch-size=50
```

**Output:** `analyzed.csv` with additional columns:
- `sentiment` (positive/negative/neutral)
- `sentiment_confidence` (0-1)
- `category` (your custom classification)
- `category_confidence` (0-1)

---

## 🌪 The Problem

You have **10,000 customer reviews**, survey responses, support tickets, or lead descriptions. Spreadsheet data with unstructured text.

- **Manual review?** Takes weeks. Expensive. Biased.
- **Classic keyword search?** Misses sarcasm ("Great service... NOT"), context, and implicit intent.
- **Generic AI tools?** Hallucinate or fail to output structured data you can actually use in Excel.
- **No-code tools?** Limited to 500 rows, hit paywalls fast.

## ⚡ The Solution

**AI Semantic Analyzer** is an industrial-grade NLP pipeline for CSV and Excel files. It uses Large Language Models (DeepSeek V3, GPT-4, Claude, Ollama) to analyze text data row-by-row — extracting sentiment, classifying content, detecting sarcasm, scoring leads, and more.

| Feature | 🐢 Manual / Legacy | 🚀 AI Semantic Analyzer |
| :--- | :--- | :--- |
| **Throughput** | 100 rows / hour | **5,000+ rows / hour** |
| **Cost** | $$$ (Human labor) | **<$0.10 per 1k rows** (DeepSeek/Gemma) |
| **Analysis Depth** | Surface level | **Deep semantic & psychological profiling** |
| **Output Format** | Vague notes | **Strict JSON / Structured CSV Columns** |
| **LLM Support** | N/A | **DeepSeek, GPT-4, Claude, Ollama (local)** |

---

## 👥 Who Is This For

| Role | Use Case |
| :--- | :--- |
| **Data Analysts** | Batch process survey results, NPS responses, open-ended feedback |
| **Customer Success Teams** | Classify support tickets by urgency & topic |
| **Sales & Marketing** | Score leads from free-text inquiries, analyze competitor reviews |
| **Researchers** | Qualitative coding at scale — sentiment, theme extraction, categorization |
| **E-Commerce Ops** | Process product reviews, detect sarcasm, extract feature requests |

---

## Security & Privacy

⚠️ **Important:**
- Input files are sent to external LLM APIs (OpenAI, DeepSeek, etc.)
- **Do NOT** process sensitive/PII data (passwords, personal IDs, confidential info)
- API keys are stored in environment variables — never commit `.env`
- Processed data may be logged by LLM provider — check provider's data policy
- For on-premise processing, use local LLM (Ollama) with `--model llama2`
- Output files inherit sensitivity of input — handle accordingly

---

## 🏗 Architecture

The system uses a **Scatter-Gather** pattern for parallel AI processing — maximum throughput without rate-limit bottlenecks.

```mermaid
graph LR
  A[📄 Raw CSV/Excel] --> B{⚡ ThreadPool Orchestrator}
  B --> C[🤖 Agent 1]
  B --> D[🤖 Agent 2]
  B --> E[🤖 Agent 3]
  B --> F[🤖 Agent 4]
  C & D & E & F --> G[🧠 LLM Inference (DeepSeek/GPT/Claude/Ollama)]
  G --> H[📦 JSON Extraction]
  H --> I[📊 Structured CSV Output]
```

## 🔥 Key Features

- **🚀 Multi-Threaded Engine** — Python `ThreadPoolExecutor` saturates API limits safely, processes thousands of rows in minutes.
- **🎯 Strict JSON Output** — Prompt engineering enforces 100% machine-readable results. No "Here is the analysis" fluff — just structured data.
- **🛡 Row-Level Context Isolation** — Every row analyzed independently. No data leakage between customers or samples.
- **🔌 LLM Agnostic** — Optimized for **DeepSeek V3** (best cost/performance), compatible with OpenAI GPT-4, Anthropic Claude, or local Ollama/Llama models.
- **📊 Excel-Native Output** — Results come as CSV with structured columns ready for pivot tables, BI tools, or further analysis.

---

## 🚀 Quick Start

### 1. Clone & Install
```bash
cd ai-semantic-analyzer
pip install pandas openai openpyxl
```

### 2. Configure API Key
Set your LLM API key as an environment variable:
```bash
export DEEPSEEK_API_KEY="your-key-here"
# Or for OpenAI: export OPENAI_API_KEY="sk-..."
```

### 3. Run Semantic Analysis
```bash
python analyzer.py "reviews.csv" "Analyze sentiment (Positive/Negative/Neutral), detect Sarcasm (true/false), and extract Main_Complaint."
```

---

## 💡 Use Cases

### A. E-Commerce Review Analysis
**Input:**
> "Oh fantastic, another update that breaks the login button. Just what I needed on a Monday."

**Task:** `"Extract sentiment, check for sarcasm, identify broken feature."`

**Output:**
```json
{
 "sentiment": "Negative",
 "sarcasm": true,
 "broken_feature": "Login Button",
 "urgency": "High"
}
```

### B. Lead Scoring & Sales Intelligence
**Input:**
> "We are looking to replace our enterprise CRM for 500 seats next quarter. Budget is flexible."

**Task:** `"Identify intent, company size, budget sensitivity, lead score 1-100."`

**Output:**
```json
{
 "intent": "Purchase",
 "company_size": "Enterprise (500 seats)",
 "budget_sensitivity": "Low",
 "lead_score": 95
}
```

### C. Support Ticket Classification
**Input:**
> "Your payment gateway keeps declining my card. I've tried 3 different cards. FIX THIS NOW."

**Task:** `"Classify ticket topic, urgency level, and sentiment."`

**Output:**
```json
{
 "topic": "Payment Gateway",
 "urgency": "Critical",
 "sentiment": "Angry",
 "needs_escalation": true
}
```

---

## 🛠 Roadmap

- [ ] **Web GUI** — Drag-and-drop interface for non-technical users
- [ ] **Ollama Native Mode** — Fully offline local LLM processing
- [ ] **Smart Batching** — Dynamic batch sizing to minimize token costs
- [ ] **Multi-File Processing** — Batch process entire folders of CSV/Excel files
- [ ] **Streaming Mode** — Real-time analysis for live data pipelines

---

<div align="center">

**Built with 🦾 by [Tommy Norris](https://github.com/tommynorris) & [Ivan Kurilov](https://github.com/)**

*Efficient. Brutal. Effective.*

⭐ **Star this repo** if you find it useful — it helps others discover the tool!

</div>

## License

MIT — see [LICENSE](LICENSE)

## Author

Agent Hermes — Lisa Carter  
[GitHub @Maatq1544](https://github.com/Maatq1544)
