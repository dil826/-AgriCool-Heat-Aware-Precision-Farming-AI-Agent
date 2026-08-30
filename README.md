# AgriCool: Heat-Aware Precision Farming AI Agent

AgriCool is a starter AI application for the **FortyGuard Global AI Hackathon '26**. It combines microclimate temperature intelligence with heat-aware agronomy logic and conversational AI guidance to help farmers make faster irrigation and crop-protection decisions.

## Value Proposition

- Converts hyper-local field temperature signals into actionable heat-stress insights.
- Estimates irrigation demand and water-loss pressure for common crops.
- Delivers natural-language recommendations tailored to crop and thermal risk conditions.

## Features

- FortyGuard API client with robust offline/mock fallback.
- Supplementary weather enrichment (humidity, wind, precipitation).
- Heat index and irrigation estimation engine.
- LangChain conversational advisor (OpenAI or Mistral) with graceful fallback responses.
- Streamlit dashboard with sidebar inputs, KPI cards, and interactive farmer Q&A.

## Project Architecture

```text
.
├── app.py
├── requirements.txt
├── .env.example
├── data/
│   └── crop_thresholds.json
└── src/
    ├── __init__.py
    ├── ai_agent.py
    ├── fortyguard_client.py
    ├── heat_calculator.py
    └── weather_client.py
```

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Then add your API keys in `.env`:

- `FORTYGUARD_API_KEY`
- `OPENAI_API_KEY` **or** `MISTRAL_API_KEY` (or `OPEN_MISTRAL_API_KEY`)

## Run

```bash
streamlit run app.py
```

## Usage

1. Set field coordinates in the sidebar.
2. Select the crop type.
3. Review temperature, heat risk, and irrigation estimates.
4. Ask the AgriCool advisor a field question in the chat input.

## Hackathon Context

Built as a modular baseline for rapid experimentation during the **FortyGuard Global AI Hackathon '26** with a focus on heat resilience, explainability, and practical farmer guidance.
