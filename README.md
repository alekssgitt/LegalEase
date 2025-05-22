# LegalEase

LegalEase is an AI-powered legal document analysis and Q&A application that helps users understand legal documents and get answers to legal questions.

## Features

- **Document Analysis**: Upload legal documents (PDF, TXT) and get AI-powered analysis tailored to your profile and experience level.
- **Legal Q&A**: Ask questions about legal concepts or specific documents.
- **Modern UI**: Clean, intuitive interface built with Flet.
- **AI-Powered**: Uses LLM models through Ollama for intelligent document processing.

## Tech Stack

- **Backend**: FastAPI, LangChain, Ollama
- **Frontend**: Flet (Python UI framework)
- **Document Processing**: PyPDF2
- **AI Models**: `llama3.2` (for general Q&A), `LegalAI` (custom fine-tune model based on llama3.2 for document analysis)

## Getting Started (Recommended Docker Deployment)

This is an so called instruction on how to succesessfully run this app.
### Prerequisites

- **Git**: For cloning the repository.
- **Python 3.11+**: Required to run the Flet-based user interface locally.
- **System Resources**: At least 8GB of RAM is recommended for running the LLM models smoothly, preferably more if available.

### Running Steps

2.  **Start Backend Services with Docker Compose**:
    This command will build the necessary Docker images (if they don't exist or if backend code has changed) and start all backend services, including the API, Ollama, and the model initialization service. The first time you run this, it might take several minutes to download models and build images.
    ```bash
    docker compose up --build -d
    ```
    This starts:
    - The LegalEase API.
    - The Ollama service.
    - An initialization service that pulls the `llama3.2` model and creates the custom `LegalAI` model.

3.  **Install UI Dependencies (if not already done)**:
    The UI runs as a local Python application. Ensure you are in the project's root directory (`LegalEase`), and install its dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the User Interface**:
    Once the Docker services are up and running (you can check their status with `docker ps`), start the Flet UI from the project's root directory:
    ```bash
    python ui/main.py
    ```
    The UI application window should open. It is configured to connect to the backend services running in Docker.

### Important Note on Document Analysis

- The **`LegalAI`** model is used for in-depth document analysis. Due to the complexity of this task and the nature of the model, analyzing documents, especially larger ones, **can take a significant amount of time** (potentially several minutes or more depending on document size and system resources). Please be patient while the analysis is in progress.
- General Q&A functionalities and context questions in the second tab ,using the `llama3.2` model are typically much faster.

### Accessing the API Directly
- The backend API will be available on your host machine at `http://localhost:8000`.
- API documentation (Swagger UI) can be accessed at `http://localhost:8000/docs`.

## Models

The application uses two main models:

1.  **`llama3.2`**: Used for general legal Q&A.
2.  **`LegalAI`**: A custom model based on `llama3.2`, fine-tuned specifically for legal document analysis.

Both models are automatically pulled and configured by the `init-ollama` service when you start the application with `docker compose up --build -d`.

## Running Tests

LegalEase uses promptfoo for testing LLM outputs:

```bash
npm install -g promptfoo

promptfoo eval
```

## Running locally(If for some reason it doesnt work on docker or something.)

If you prefer to run the application components locally without Docker (e.g., for backend development):

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run Ollama Locally**:
    You'll need to have Ollama installed and running separately on your system. Ensure the `llama3.2` model is pulled and the `LegalAI` model is created (e.g., using `ollama pull llama3.2` and `ollama create legalai -f LegalAI/modelfile`).

3.  **Start the API**:
    Ensure the `OLLAMA_BASE_URL` environment variable is correctly set if your local Ollama instance is not at the default `http://localhost:11434`.
    ```bash
    uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
    ```

4.  **Start the UI**:
    ```bash
    python ui/main.py
    ```

## Important Notes
  Be patient with analysis of the documents it can take a pretty long time,so if you would really like to test it out fast,i recommend running it locally without docker.
  All of the app functionality can take up to 5 minutes on the cold start,but after first request the time considerebly minimizes.
  The way application works is you can either go to tab 1 and upload document for analysis,or you can go to second tab,ask general legal question or upload document and ask question about the document specifically.