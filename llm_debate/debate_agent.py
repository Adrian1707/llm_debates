import os
import json
import requests
from llm_debate.ollama_client import OllamaClient

class DebateAgent:
    def __init__(self, for_or_against, topic):
        if for_or_against == 'for':
            self.side = 'in favor'
        else:
            self.side = 'not in favor'
        self.topic = topic
        self.for_or_against = for_or_against
        self.llm_client = OllamaClient()
    
    def build_debate_prompt(self, opponent_argument):
        self_history = "\n".join(f"{i+1}. {arg}" for i, arg in enumerate(self.llm_client.previous_arguments[-2:]))
        prompt = f"""
            /no_think
            You are engaged in a direct, one-on-one debate with your opponent on the following topic:
            "{self.topic}"
            You are "{self.side}" of this so you will argue "{self.for_or_against}" the topic in question.

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

    def respond(self, opponent_argument: str):
        prompt_message = self.build_debate_prompt(opponent_argument)
        return self.llm_client.generate_response(prompt_message)
