# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

**Please do not open a public issue for security vulnerabilities.**

Instead, report privately via one of these channels:

- **Email:** security@[project-domain].com (preferred)
- **GitHub Security Advisory:** Use the "Security" tab → "Advisories" → "New draft security advisory"

We will:

1. Acknowledge your report within **48 hours**
2. Provide an initial assessment within **5 business days**
3. Work with you on a coordinated disclosure timeline
4. Credit you in the fix release (unless you prefer anonymity)

## Data Privacy Considerations

> [!IMPORTANT]
> This tool sends your data to external LLM providers. Understand the implications before processing sensitive data.

**Cloud providers (DeepSeek, OpenAI, Anthropic):**

- Input data is transmitted to the provider's servers
- Providers may log inputs/outputs per their data retention policy
- Review each provider's data policy before production use:
  - [DeepSeek Privacy](https://deepseek.com/privacy)
  - [OpenAI Data Usage](https://openai.com/policies/privacy-policy)
  - [Anthropic Privacy](https://www.anthropic.com/privacy)

**Local processing (Ollama):**

- Data never leaves your machine
- Suitable for sensitive workloads
- Requires sufficient local compute (GPU recommended for speed)

**API key safety:**

- Never commit `.env` files
- Never hardcode keys in source code
- Use environment variables or a secret manager
- Rotate keys periodically
- Restrict API key permissions to only what's needed

## Best Practices

1. **Redact PII before processing** — strip emails, phone numbers, IDs unless absolutely needed
2. **Use Ollama for sensitive data** — full local processing
3. **Audit output files** — they may inherit sensitivity of input
4. **Set up rate limits** — prevent accidental bulk processing
5. **Monitor token usage** — catch unexpected spikes
6. **Use sandbox environments** — test on dummy data first
7. **Encrypt at rest** — protect output files containing sensitive analysis

## Disclosure Timeline

We aim to follow a **90-day disclosure timeline**:

- Day 0: Vulnerability reported
- Day 1-2: Acknowledgment
- Day 7: Initial assessment + triage
- Day 30: Patch developed (typical)
- Day 60: Patch released + CVE assigned (if applicable)
- Day 90: Public disclosure (if not earlier)
