#!/usr/bin/env python3
# screen_monitor.py

import sys
import argparse
import os
import json
from datetime import datetime
from PyQt5.QtCore import QCoreApplication, QTimer

# Import custom packages
try:
    from brainboost_desktop_package.Desktop import Desktop
    from brainboost_data_source_package.BBKnowledgeHooksRealTimeDataSource import BBKnowledgeHooksRealTimeDataSource
    from brainboost_configuration_package.BBConfig import BBConfig
    from brainboost_data_source_logger_package.BBLogger import BBLogger
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Ensure that brainboost_desktop_package, brainboost_data_source_package, "
          "brainboost_configuration_package, and brainboost_data_source_logger_package "
          "are installed and accessible in PYTHONPATH.")
    sys.exit(1)

import cv2

def parse_arguments():
    """
    Parses command-line arguments.
    
    Returns:
        argparse.Namespace: Parsed arguments.
    """
    parser = argparse.ArgumentParser(description="Continuous Screen Monitor Script using BBKnowledgeHooksRealTimeDataSource")
    parser.add_argument(
        '-f', '--frequency',
        type=int,
        default=5,
        help='Frequency of screenshots in minutes (default: 5)'
    )
    parser.add_argument(
        '-c', '--config',
        type=str,
        default='worktwins.conf',
        help='Path to the configuration file (default: worktwins.conf)'
    )
    return parser.parse_args()

def initialize_configuration(config_path):
    """
    Initializes the BBConfig with the given configuration file.
    
    Args:
        config_path (str): Path to the configuration file.
    """
    if not os.path.exists(config_path):
        print(f"Configuration file not found at: {config_path}")
        sys.exit(1)
    
    BBConfig.load_config(config_path)
    BBLogger.log(f"Configuration loaded from {config_path}")

def handle_ocr_data(ocr_data):
    """
    Slot to handle OCR data emitted by the data source.
    
    Args:
        ocr_data (list): List of OCR result dictionaries.
    """
    BBLogger.log(f"Received OCR Data: {ocr_data}")
    # You can add additional processing here if needed

def handle_progress(progress_value):
    """
    Slot to handle progress updates emitted by the data source.
    
    Args:
        progress_value (int): Progress percentage.
    """
    BBLogger.log(f"OCR Processing Progress: {progress_value}%")

def handle_error(error_message):
    """
    Slot to handle error messages emitted by the data source.
    
    Args:
        error_message (str): Error message.
    """
    BBLogger.log(f"Error from Data Source: {error_message}")

def main():
    args = parse_arguments()
    frequency_minutes = args.frequency
    config_path = args.config
    
    initialize_configuration(config_path)
    
    # Initialize PyQt Core Application
    app = QCoreApplication(sys.argv)
    
    # Initialize the Data Source with poll_interval_seconds
    poll_interval_seconds = frequency_minutes * 60
    data_source = BBKnowledgeHooksRealTimeDataSource(poll_interval_seconds=poll_interval_seconds)
    
    # Connect signals to slots
    data_source.ocr_data_available.connect(handle_ocr_data)
    data_source.progress.connect(handle_progress)
    data_source.error.connect(handle_error)
    
    # Start the data source thread
    data_source.start()
    BBLogger.log(f"BBKnowledgeHooksRealTimeDataSource started with a polling interval of {frequency_minutes} minutes.")
    
    # Define a handler for graceful shutdown on SIGINT (Ctrl+C)
    def shutdown():
        BBLogger.log("Shutting down screen monitor.")
        data_source.stop_data_source()
        QTimer.singleShot(1000, app.quit)  # Allow some time for the thread to close

    # Connect the SIGINT signal to the shutdown function
    import signal
    signal.signal(signal.SIGINT, lambda sig, frame: shutdown())
    
    try:
        # Execute the PyQt event loop
        sys.exit(app.exec_())
    except Exception as e:
        BBLogger.log(f"Unexpected error in main event loop: {e}")
        data_source.stop_data_source()
        sys.exit(1)

if __name__ == "__main__":
    main()
