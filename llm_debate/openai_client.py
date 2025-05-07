import openai

class OpenAIClient(LLMClient):
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key
        self.model = model
    
    def generate_response(self, prompt_message: str):
        full_response = ""
        response_stream = openai.ChatCompletion.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt_message}],
            stream=True,
            api_key=self.api_key,
        )

        buffer = ""
        
        for chunk in response_stream:
            delta_content = ''
            try:
                delta_content = chunk['choices'][0]['delta'].get('content', '')
            except (KeyError, IndexError):
                continue
            
            if delta_content:
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