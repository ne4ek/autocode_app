from abc import ABC, abstractmethod

class AbstractDatabase(ABC):
    @abstractmethod
    def get_data(self, task_id: int) -> dict:
        pass
    
    @abstractmethod
    def save_data(self, task_id: int, data: dict):
        pass

    @abstractmethod
    def search_data(self, task_id: int) -> dict:
        pass
    
    