#!/bin/sh
# Exit script on any error
set -e

echo "Ollama Entrypoint: Starting Ollama server in background..."
# Start the Ollama server in the background
ollama serve &
# Capture the Process ID (PID) of the server
OLLAMA_PID=$!
echo "Ollama Entrypoint: Server started with PID ${OLLAMA_PID}."

# Wait a few seconds for the server to initialize
# Adjust this sleep time if needed, especially on slower systems
sleep 5

# Check if the model needs to be pulled (using the environment variable)
# Default to 'llama3' if OLLAMA_MODEL_TO_PULL is not set
MODEL_TO_PULL=${OLLAMA_MODEL_TO_PULL:-llama3}

echo "Ollama Entrypoint: Ensuring model '${MODEL_TO_PULL}' is available..."
ollama pull "${MODEL_TO_PULL}"
echo "Ollama Entrypoint: Model pull command finished for '${MODEL_TO_PULL}'."

# Now, wait for the Ollama server process to exit
echo "Ollama Entrypoint: Tailing server logs (waiting for PID ${OLLAMA_PID})..."
wait ${OLLAMA_PID}

# If wait finishes, it means ollama serve stopped.
# The exit code of this script will be the exit code of ollama serve
echo "Ollama Entrypoint: Ollama server process (PID ${OLLAMA_PID}) has exited."
exit $?
