#!/bin/sh
set -e

echo "Checking if Ollama is running"

echo "Checking if llama3.2 model is available"
llama_check=$(ollama list | grep llama3.2 || true)
if [ -z "$llama_check" ]; then
  echo "Pulling llama3.2"
  ollama pull llama3.2
  echo "llama3.2 model pulled."
else
  echo "llama3.2 model is already available"
fi

sleep 10

echo "Creating LegalAI model using existing Modelfile"

echo "Attempting to create LegalAI model"
ollama create legalai -f /app/LegalAI/modelfile

echo "Model initialization completed!"
