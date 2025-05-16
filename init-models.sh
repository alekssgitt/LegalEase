#!/bin/sh

echo "Checking if Ollama is running..."

# Check if llama3.2 model exists
echo "Checking if llama3.2 model is available..."
llama_check=$(curl -s http://localhost:11434/api/tags | grep llama3.2)
if [ -z "$llama_check" ]; then
  echo "Pulling llama3.2 model..."
  curl -X POST http://localhost:11434/api/pull -d '{"name":"llama3.2"}'
else
  echo "llama3.2 model is already available"
fi

sleep 2

# Create the LegalAI model
echo "Creating LegalAI model..."
MODELFILE="FROM llama3.2
PARAMETER temperature 0.2
SYSTEM \"\"\"
You are LegalAI, an expert legal document analyzer. Your job is to:
- Explain legal documents in plain language.
- Tailor explanations for the user's type and legal experience.
- Provide:
  1. A clear summary
  2. Key points and obligations
  3. Potential risks or hidden clauses
  4. Recommended actions
Always be concise, accurate, and user-friendly. If the document is complex, break down the explanation into manageable sections.
\"\"\""

curl -X POST http://localhost:11434/api/create -d "{\"name\":\"legalai\", \"modelfile\":\"$MODELFILE\"}"

echo "Model initialization completed!"
