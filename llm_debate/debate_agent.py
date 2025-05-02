import os
import json
from typing import Optional
from dotenv import load_dotenv
import requests

load_dotenv()  # Loads .env file from current directory by default

class DebateAgent:
    def __init__(self, side, topic):
        self.side = side  # 'for' or 'against'
        self.topic = topic
        self.previous_arguments = []  # Track what was said in previous rounds
    
    def build_debate_prompt(self, opponent_argument):
        self_history = "\n".join(f"{i+1}. {arg}" for i, arg in enumerate(self.previous_arguments[-2:]))
        prompt = f"""
            /no_think
            You are engaged in a direct, one-on-one debate with your opponent on the following topic:

            "{self.topic}"

            Instructions:
            - Respond conversationally and directly to your opponent's last argument below.
            - DO NOT start your reply with any formal salutation (e.g., "Ladies and gentlemen", "esteemed judges", etc.).
            - Focus only on addressing your opponent's points and advancing your case.
            - Maintain a natural, professional tone as if speaking directly to another expert—not an audience.
            - Build on both your own previous arguments and theirs for coherence.
            - Use examples, data, and logic as needed.
            - Write a detailed response (about 300–400 words).

            Your previous arguments:
            {self_history}

            Opponent just said:
            "{opponent_argument}"

            Compose your response now—begin directly with substance.
        """
        return prompt

    def respond(self, opponent_argument):
        prompt_message = self.build_debate_prompt(opponent_argument)
        try:
            url = "http://host.docker.internal:11434/api/generate"
            headers = {"Content-Type": "application/json"}
            payload = {
                "model": "qwen3:30b-a3b",
                "prompt": prompt_message,
                "stream": True,
            }

            collected_response = ""
            with requests.post(url, headers=headers, json=payload, stream=True) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if line:
                        data = json.loads(line.decode('utf-8'))
                        chunk = data.get('response', '')
                        if chunk != "</think>" and chunk != "<think>":
                            print(chunk, end='', flush=True)
                            collected_response += chunk
                            yield chunk  # Real-time token stream

            self.previous_arguments.append(collected_response.strip())

        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse JSON response from OpenAI API. Response was:\n{reply_content}") from e
        except Exception as e:
            raise RuntimeError(f"Failed to classify email: {e}")

import re

def is_valid_text(text):
    # Define a regex pattern that matches valid text (letters, numbers, spaces, punctuation)
    # You can adjust this pattern as needed
    return bool(re.match(r'^[\w\s\.,!?\-\'\";:()]+$', text))