import openai
from django.utils import timezone
from .base import BaseAIHandler

class OpenAIHandler(BaseAIHandler):
    def process_request(self, ai_model, input_data):
        if not ai_model.api_key:
            raise ValueError("API key is not set for this OpenAI model")
        
        openai.api_key = ai_model.api_key
        
        model_name = ai_model.name
        if not model_name:
            raise ValueError("Model name is not set for this OpenAI model")
        
        try:
            print("実行されるプロンプト:")
            print(input_data['node_data']['instruction'])
            temperature = input_data['node_data'].get('temperature', 0.5)
            response = openai.ChatCompletion.create(
                model=model_name,
                temperature=temperature,
                messages=[
                    {"role": "system", "content": input_data['node_data']['system_prompt']},
                    {"role": "user", "content": input_data['node_data']['instruction']}
                ]
            )
        except openai.error.OpenAIError as e:
            raise ValueError(f"OpenAI API error: {str(e)}")
        
        return {
            "result": response.choices[0].message['content'].strip(),
            "timestamp": str(timezone.now())
        }
    
    def _create_prompt(self, input_data):
        instruction = input_data['node_data']['instruction']
        previous_output = input_data['previous_output']['result']
        return f"Instruction: {instruction}\n\nInput: {previous_output}\n\nOutput:"