# LegalEase

LegalEase is an AI-powered legal document analysis and Q&A application that helps users understand legal documents and get answers to legal questions.

## Features

- **Document Analysis**: Upload legal documents (PDF, TXT) and get AI-powered analysis tailored to your profile and experience level
- **Legal Q&A**: Ask questions about legal concepts or specific documents
- **Modern UI**: Clean, intuitive interface built with Flet
- **AI-Powered**: Uses LLM models through Ollama for intelligent document processing

## Tech Stack

- **Backend**: FastAPI, LangChain, Ollama
- **Frontend**: Flet (Python UI framework)
- **Document Processing**: PyPDF2, Sentence Transformers
- **Vector Database**: FAISS

## Running the Backend with Docker

### Prerequisites

- Docker and Docker Compose installed
- At least 8GB of RAM for running the LLM models

### Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/LegalEase.git
   cd LegalEase
   ```

2. Start the backend services using Docker Compose:
   ```bash
   docker-compose up -d
   ```

3. The backend API will be available at:
   - http://localhost:8000

4. You can test the API with the following endpoints:
   - Document Analysis: POST http://localhost:8000/analyze
   - Legal Q&A: POST http://localhost:8000/legal_qa

### Running the UI Locally

To run the UI locally (connecting to the Docker backend):

1. Make sure you have Python 3.11+ installed

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the UI:
   ```bash
   python ui/main.py
   ```

4. The UI will be available at:
   - Desktop app running on port 8550

## Models

The application uses two main models:

1. **llama3.2**: Used for general legal Q&A
2. **LegalAI**: A custom model based on llama3.2, fine-tuned for legal document analysis

Both models are automatically pulled and configured when starting the Docker containers.

## API Documentation

Once the backend is running, you can access the API documentation at:
- http://localhost:8000/docs

## Running Tests

LegalEase uses promptfoo for testing LLM outputs:

```bash
# Install promptfoo
npm install -g promptfoo

# Run tests
promptfoo eval
```

## Development Setup

If you prefer to run the application without Docker:

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Start the API:
   ```bash
   uvicorn api.main:app --reload
   ```

3. Start the UI:
   ```bash
   python -m ui.main
   ```

## License

MIT
