from .openai_handler import OpenAIHandler
from .azure_openai_handler import AzureOpenAIHandler
from .claude_handler import ClaudeHandler

def get_ai_handler(model_type):
    if model_type == 'OpenAI':
        return OpenAIHandler()
    elif model_type == 'AzureOpenAI':
        return AzureOpenAIHandler()
    elif model_type == 'Claude':
        return ClaudeHandler()
    else:
        raise ValueError(f"Unsupported model type: {model_type}")