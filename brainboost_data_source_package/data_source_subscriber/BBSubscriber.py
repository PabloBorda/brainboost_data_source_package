# File: brainboost_data_source_package/subscriber/BBSubscriber.py

from abc import ABC, abstractmethod

class BBSubscriber(ABC):

    def __init__(self, any_object):
        self.any_object = any_object

    @abstractmethod
    def notify(self, data: dict) -> None:
        """Handle incoming data updates."""
        pass  # No implementation in abstract method
