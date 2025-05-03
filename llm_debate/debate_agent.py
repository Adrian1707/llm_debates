import os
import json
import requests

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
            - Look through your previous arguments and make sure you do not repeat any of these arguments. Take the debate into another direction and expand on the topic in a multi-disciplinary way.
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
                            collected_response += chunk
                            yield chunk

            self.previous_arguments.append(collected_response.strip())
        except Exception as e:
            raise RuntimeError(f"Failed to complete local LLM call: {e}")
