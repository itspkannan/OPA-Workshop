#!/bin/sh

MODEL=${LLM_MODEL:-tinyllama}

echo "Waiting for Ollama to be ready..."
until curl -s http://llm_service:11434/health; do sleep 1; done

echo "Pulling model: $MODEL..."
curl -s http://llm_service:11434/api/pull -d "{\"name\": \"$MODEL\"}"
echo "Model pulled."

echo "Testing model: $MODEL..."
curl -s -X POST http://llm_service:11434/api/generate \
  --header 'Content-Type: application/json' \
  -d "{\"model\": \"$MODEL\", \"prompt\": \"why is the sky blue?\", \"stream\": false}"
echo "Done."
