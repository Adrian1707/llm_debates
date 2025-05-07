from openai import OpenAI
import os
from llm_debate.llm_client import LLMClient
from openai.types.responses import ResponseTextDeltaEvent

class OpenAIClient(LLMClient):
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.previous_arguments = []
    
    def generate_response(self, prompt_message: str):
        full_response = ""
        
        stream = self.client.responses.create(
            model="gpt-4.1-nano",
            input=prompt_message,
            stream=True,
        )

        buffer = ""
        
        for chunk in stream:
            if isinstance(chunk, ResponseTextDeltaEvent):
                delta_content = chunk.delta 

                buffer += delta_content
                full_response += delta_content

                parts = buffer.split()

                if parts:
                    # Yield all complete words except last partial one
                    for word in parts[:-1]:
                        yield word + ' '
                    # Keep the last part as it might be incomplete
                    buffer = parts[-1]
        
                # After streaming ends, yield any remaining partial word
        if buffer.strip():
            yield buffer + ' '

        self.previous_arguments.append(full_response.strip())