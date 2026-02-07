# AI Semantic Analyzer (sentiment-analyzer)

Industrial-grade tool for processing large datasets (CSV/Excel) using LLMs for deep semantic analysis, including sentiment, sarcasm detection, and demographic estimation.

## 🚀 Overview
Traditional NLP parsers fail at human nuances like sarcasm or complex slang. This tool implements a row-by-row AI processing pipeline that leverages DeepSeek (Cloud) or local models (Gemma/Llama) to provide human-level insights at scale.

## 🛠 Key Features
- **Sarcasm Detection**: Beyond keyword matching, the LLM understands context and tone.
- **Demographic Profiling**: Estimates gender and age range based on nicknames and linguistic patterns.
- **Batch Processing**: Designed to handle 1000+ rows efficiently.
- **Privacy-First (Local Mode)**: Supports integration with local LLM studios for processing sensitive PII (Personally Identifiable Information).

## 📊 Performance
- **Cloud (DeepSeek)**: High-speed, low-cost processing (1000 rows in minutes).
- **Local (Gemma/Llama)**: Zero-cost, 100% private, performance dependent on hardware.

## 📁 Repository Structure
- `analyzer.py`: Core processing script with multi-threading support.
- `examples/`: Sample datasets and prompt templates.

---
*Maintained by Ivan Kurilov - System Analyst & AI Automation Specialist.*
