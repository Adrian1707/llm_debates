import os
import json
import requests

class DebateAgent:
    def __init__(self, for_or_against, topic):
        if for_or_against == 'for':
            self.side = 'in favor'
        else:
            self.side = 'not in favor'
        self.topic = topic
        self.for_or_against = for_or_against
        self.previous_arguments = []  # Track what was said in previous rounds
    
    def build_debate_prompt(self, opponent_argument):
        self_history = "\n".join(f"{i+1}. {arg}" for i, arg in enumerate(self.previous_arguments[-2:]))
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
        
        url = "http://host.docker.internal:11434/api/generate"
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
            # Handle the request failure, potentially retry or log
            # For now, re-raising the exception or handling it as needed
            # Depending on desired behavior, you might want to add the partial response
            # to previous_arguments even on failure, or handle it differently.
            # For this task, we'll assume successful response is needed to add to history.
            prompt_message = self.build_debate_prompt(opponent_argument)

            url = "http://host.docker.internal:11434/api/generate"
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

                                    # Split into words; keep last part if incomplete
                                    parts = buffer.split()

                                    # All but last are complete words
                                    for word in parts[:-1]:
                                        yield word + ' '

                                    # Last part might be incomplete; keep it in buffer
                                    buffer = parts[-1]
                            except (json.JSONDecodeError, UnicodeDecodeError):
                                continue

                # After stream ends, check if there's an incomplete word left
                if buffer:
                    yield buffer + ' '

                # Append the full response to previous_arguments
                self.previous_arguments.append(full_response.strip())

            except requests.RequestException as e:
                print(f"Request failed: {e}")
                # Re-raise or handle the exception as appropriate
                raise e
