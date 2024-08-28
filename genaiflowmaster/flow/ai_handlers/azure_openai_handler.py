import openai
from django.utils import timezone
from .base import BaseAIHandler

class AzureOpenAIHandler(BaseAIHandler):
    def process_request(self, ai_model, input_data):
        if not ai_model.api_key or not ai_model.api_version or not ai_model.endpoint:
            raise ValueError("API key, API version, or endpoint is not set for this Azure OpenAI model")

        openai.api_type = "azure"
        openai.api_version = ai_model.api_version
        openai.api_base = ai_model.endpoint
        openai.api_key = ai_model.api_key

        model_name = ai_model.name
        if not model_name:
            raise ValueError("Model name is not set for this Azure OpenAI model")

        try:
            temperature = input_data['node_data'].get('temperature', 0.5)
            response = openai.ChatCompletion.create(
                engine=model_name,
                temperature=temperature,
                messages=[
                    {"role": "system", "content": input_data['node_data']['system_prompt']},
                    {"role": "user", "content": self._create_prompt(input_data)}
                ]
            )
        except openai.error.OpenAIError as e:
            raise ValueError(f"Azure OpenAI API error: {str(e)}")
        
        return {
            "result": response.choices[0].message['content'].strip(),
            "timestamp": str(timezone.now())
        }
    
    def _create_prompt(self, input_data):
        instruction = input_data['node_data']['instruction']
        previous_output = input_data['previous_output']['result']
        return f"Instruction: {instruction}\n\nInput: {previous_output}\n\nOutput:"