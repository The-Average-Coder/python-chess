from abc import ABC, abstractmethod

class UIElement(ABC):
    @abstractmethod
    def render(self):
        pass