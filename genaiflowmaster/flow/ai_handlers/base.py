from abc import ABC, abstractmethod

class BaseAIHandler(ABC):
    @abstractmethod
    def process_request(self, ai_model, input_data):
        pass