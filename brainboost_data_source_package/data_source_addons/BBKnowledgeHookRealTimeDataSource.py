# brainboost_desktop_package/BBKnowledgeHooksRealTimeDataSource.py

import time
from typing import List, Tuple, Dict, Any
from brainboost_data_source_logger_package.BBLogger import BBLogger
from brainboost_desktop_package.Desktop import Desktop
from brainboost_data_source_package.data_source_abstract.BBDataSource import BBDataSource
from datetime import datetime
import numpy as np


class BBKnowledgeHookRealTimeDataSource(BBDataSource):
    def __init__(
        self,
        name: str = None,
        session: str = None,
        dependency_data_sources: List[Any] = [],
        subscribers: List[Any] = None,
        params: Dict[str, Any] = None
    ):
        """
        Initialize the BBKnowledgeHooksRealTimeDataSource.

        Args:
            name (str, optional): Name of the data source.
            session (str, optional): Session identifier.
            dependency_data_sources (list, optional): List of dependency data sources.
            subscribers (list, optional): List of subscribers.
            params (dict, optional): Parameters including 'frequency' in seconds.
        """
        super().__init__(name, session, dependency_data_sources, subscribers, params)
        self.frequency = self.params.get('frequency', 5)  # frequency in seconds, default to 5 seconds

    def fetch(self):
        """
        Fetch data in an infinite loop by taking desktop snapshots at specified frequency.
        Each snapshot includes an image and extracted texts with their bounding rectangles.
        """
        desktop = Desktop.get_desktop_singleton()
        BBLogger.log(f"Starting BBKnowledgeHooksRealTimeDataSource with frequency {self.frequency} seconds.")
        
        if self.status_callback:
            self.status_callback(self.get_name(), 'started')
        
        while True:
            try:
                # Take a snapshot
                screenshot, texts_with_rects = desktop.snapshot()
                
                # Print the image and rects as text
                snapshot_time = datetime.now().isoformat()
                print(f"Snapshot taken at {snapshot_time}")
                print(f"Image shape: {screenshot.shape}")  # (height, width, channels)
                print("Extracted Texts and their Bounding Rectangles:")
                for text, rect in texts_with_rects:
                    print(f"Text: '{text}', Rect: {rect}")
                
                # Notify subscribers with snapshot data
                snapshot_data = {
                    'timestamp': snapshot_time,
                    'image': screenshot,
                    'texts_with_rects': texts_with_rects
                }
                self.update(snapshot_data)
                
                # Optionally, use progress_callback if needed
                if self.progress_callback:
                    # Example: You can implement progress tracking here if applicable
                    pass  # Replace with actual progress tracking logic
                
                # Sleep for the specified frequency time
                time.sleep(self.frequency)
            
            except Exception as e:
                BBLogger.log(f"Exception in fetch: {e}")
                if self.status_callback:
                    self.status_callback(self.get_name(), 'error')
                break  # Exit the loop on error

    def get_icon(self) -> str:
        """
        Return the SVG code for the data source icon.

        Returns:
            str: SVG string representing the icon.
        """
        # Example SVG icon representing knowledge hooks
        return """
                <svg xmlns="http://www.w3.org/2000/svg"
                    width="64"
                    height="64"
                    viewBox="0 0 64 64">
                <!-- Rectangle 1 (Red) -->
                <rect x="4" y="4" width="10" height="12" fill="#FF0000" />

                <!-- Rectangle 2 (Gold) -->
                <rect x="20" y="6" width="14" height="20" fill="#FFD700" />

                <!-- Rectangle 3 (Green) -->
                <rect x="36" y="2" width="16" height="10" fill="#00FF00" />

                <!-- Rectangle 4 (Blue) -->
                <rect x="2" y="22" width="12" height="10" fill="#0000FF" />

                <!-- Rectangle 5 (Magenta) -->
                <rect x="16" y="32" width="24" height="14" fill="#FF00FF" />

                <!-- Rectangle 6 (Orange) -->
                <rect x="44" y="18" width="16" height="14" fill="#FFA500" />

                <!-- Rectangle 7 (Purple) -->
                <rect x="4" y="46" width="10" height="16" fill="#800080" />

                <!-- Rectangle 8 (Teal) -->
                <rect x="30" y="48" width="16" height="10" fill="#008080" />

                <!-- Rectangle 9 (Orchid) -->
                <rect x="50" y="32" width="8" height="18" fill="#DA70D6" />

                <!-- Rectangle 10 (Olive) -->
                <rect x="22" y="50" width="12" height="12" fill="#808000" />
                </svg>

                """

    def get_connection_data(self) -> Dict[str, Any]:
        """
        Return the connection type and required fields for this data source.

        Returns:
            dict: Connection type and required fields.
        """
        # Since it's a real-time data source from the local machine, connection type is Local
        return {
            "connection_type": "Local",
            "fields": ["frequency"]  # frequency in seconds
        }


