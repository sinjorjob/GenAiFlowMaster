import anthropic
from django.utils import timezone
from .base import BaseAIHandler
import json
import traceback

class ClaudeHandler(BaseAIHandler):
    def process_request(self, ai_model, input_data):
        if not ai_model.api_key:
            raise ValueError("API key is not set for this Claude model")

        client = anthropic.Anthropic(api_key=ai_model.api_key)
        
        model_name = ai_model.name
        if not model_name:
            raise ValueError("Model name is not set for this Claude model")
        
        try:
            print("実行されるプロンプト:")
            print(input_data['node_data']['instruction'])
            temperature = input_data['node_data'].get('temperature', 0.5)
            response = client.messages.create(
                model=model_name,
                max_tokens=4096,
                temperature=temperature,
                system=input_data['node_data']['system_prompt'],
                messages=[
                    {"role": "user", "content": input_data['node_data']['instruction']}
                ]
            )
            
            print(f"Response type: {type(response.content)}")
            
            # TextBlockからテキストを抽出
            if isinstance(response.content, list) and len(response.content) > 0:
                extracted_text = response.content[0].text
            else:
                extracted_text = str(response.content)
            
            print(f"Extracted text: {extracted_text}")
            
            result = {
                "result": extracted_text,
                "timestamp": str(timezone.now())
            }
            
            # 結果をJSONシリアライズ可能かどうかチェック
            try:
                json_result = json.dumps(result)
                print("Result successfully serialized to JSON")
                return json.loads(json_result)  # デシリアライズして返す
            except TypeError as e:
                print(f"JSON Serialization error: {e}")
                print(f"Problematic result: {result}")
                raise ValueError(f"Result is not JSON serializable: {e}")
        
        except anthropic.APIError as e:
            print(f"Claude API error: {str(e)}")
            print(f"Detailed error: {traceback.format_exc()}")
            raise ValueError(f"Claude API error: {str(e)}")
        
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            print(f"Detailed error: {traceback.format_exc()}")
            raise
    
    def _create_prompt(self, input_data):
        instruction = input_data['node_data']['instruction']
        previous_output = input_data['previous_output']['result']
        return f"Instruction: {instruction}\n\nInput: {previous_output}\n\nOutput:"