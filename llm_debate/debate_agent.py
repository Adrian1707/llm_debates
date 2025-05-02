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
        You are participating in a formal debate. Your role is to argue {"in favor of" if self.side == 'for' else "against"} the following topic:

        "{self.topic}"

        Debate format:
        - Respond directly to your opponent's latest argument.
        - Address their main point(s).
        - Rebut their claims with logical reasoning and (if possible) supporting evidence or examples.
        - Reference your own earlier points if relevant.
        - Keep your response concise but thorough (3–6 sentences).
        - End with either a rhetorical question or a challenge for your opponent.

        History of your last arguments:
        {self_history}

        Opponent just said:
        "{opponent_argument}"

        Your turn!
        """
        return prompt

    def respond(self, opponent_argument):
        """Generate a response to the opponent's argument."""
        prompt_message = self.build_debate_prompt(opponent_argument)
        try:   
            url = "http://host.docker.internal:11434/api/generate"

            headers = {
                "Content-Type": "application/json"
            }

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
                        print(chunk, end='', flush=True)
                        collected_response += chunk
                        yield chunk  # For true streaming back to caller
            self.previous_arguments.append(collected_response.strip())

        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse JSON response from OpenAI API. Response was:\n{reply_content}") from e
        except Exception as e:
            raise RuntimeError(f"Failed to classify email: {e}")