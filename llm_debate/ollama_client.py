import requests
import json
from llm_debate.llm_client import LLMClient

class OllamaClient(LLMClient):
    def __init__(self, url="http://host.docker.internal:11434/api/generate"):
        self.url = url
        self.previous_arguments = []

    def generate_response(self, prompt_message: str):
        url = "http://host.docker.internal:11434/api/generate"
        # url = "http://ollama:11434/api/generate"
        headers = {"Content-Type": "application/json"}
        payload = {
            "model": "qwen3:30b-a3b",
            "prompt": prompt_message,
            "stream": True,
        }

        buffer = ""  # Buffer to hold partial words
        full_response = "" # Accumulate the full response

        try:
            with requests.post(url, headers=headers, json=payload, stream=True, timeout=30) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if line:
                        try:
                            data_str = line.decode('utf-8')
                            data = json.loads(data_str)
                            chunk = data.get('response', '')

                            # Filter out control tokens
                            if chunk not in ("</think>", "<think>"):
                                # Append new chunk to buffer and full response
                                buffer += chunk
                                full_response += chunk

                                # Split into parts
                                parts = buffer.split()

                                if parts:
                                    # Yield all complete words (except last)
                                    for word in parts[:-1]:
                                        yield word + ' '
                                    # Keep the last part (possibly incomplete)
                                    buffer = parts[-1]
                                else:
                                    # No words yet; keep buffer as-is (possibly whitespace)
                                    continue

                        except (json.JSONDecodeError, UnicodeDecodeError):
                            continue

            # After stream ends, check if there's an incomplete word left
            if buffer.strip():
                yield buffer + ' '

            # Append the full response to previous_arguments
            self.previous_arguments.append(full_response.strip())

        except requests.RequestException as e:
            print(f"Request failed: {e}")
            # Re-raise or handle the exception as appropriate
            raise e