# File: brainboost_data_source_package/subscriber/ConcreteSubscriber.py

from brainboost_data_source_package.data_source_subscriber.BBSubscriber import BBSubscriber
from brainboost_data_source_package.data_source_abstract.BBRealTimeDataSource import BBRealTimeDataSource
from brainboost_data_source_logger_package.BBLogger import BBLogger

class BBConcreteSubscriber(BBSubscriber):
    def __init__(self):
        super().__init__(any_object=self)
    
    def notify(self, data: dict) -> None:
        """Handle incoming data updates."""
        BBLogger.log('Hello I am a subscriber object, I could be a UI')
        BBLogger.log(f"Received data update: {data}")

def test_realTimeDS():
    BBLogger.log('Starting Test test_realTimeDS')
    bbrtds =  BBRealTimeDataSource(name='test_bbrealtime')
    BBLogger.log('Starting listener...')
    bbrtds.subscribe(BBConcreteSubscriber())
    BBLogger.log('Listener finished...')