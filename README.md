# LegalEase

An LLM-Powered Assistant for Understanding Contracts and Legal Documents

## Overview
LegalEase helps users understand complex legal documents using AI. Upload documents and get plain-language summaries and risk analysis.

## Features
- Document upload (PDF, text) support
- Plain language summaries
- Risk clause detection
- User profile-based explanations
- Local execution using Ollama
- Context-aware responses with memory

## Setup
1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Install Ollama and download required models:
```bash
# Download llama3.2 model
ollama pull llama3.2
```

3. Run the application:
```bash
uvicorn api.main:app --reload
```

## Project Structure
```
LegalEase/
├── api/              # FastAPI endpoints
├── core/            # Core business logic
├── models/          # Pydantic models
├── services/        # LLM and document processing services
├── utils/           # Helper functions
└── tests/           # Test files
```

## Author
- Alekss Noviconoks
