# tests/test_BBKnowledgeHookRealTimeDataSource.py

import pytest
import threading
import time
from unittest.mock import patch, MagicMock
from brainboost_data_source_package.data_source_addons import BBKnowledgeHookRealTimeDataSource
from brainboost_configuration_package.BBConfig import BBConfig
from io import StringIO
import sys
import numpy as np
from pathlib import Path

@pytest.fixture(scope="function", autouse=True)
def setup_test_environment():
    """
    Fixture to set up and clean the test environment before each test.
    """
    # Override configurations for testing purposes
    BBConfig.override('snapshots_database_enabled', False)
    BBConfig.override('snapshots_database_path', '')
    BBConfig.override('write_screenshots_to_files', False)  # Disable file writing during tests
    TEST_IMAGES_DIR = Path(__file__).parent / "test_images"
    BBConfig.override('snapshot_images', str(TEST_IMAGES_DIR))  # Ensure snapshot_images points to the test directory
    
    # Ensure the test_images directory exists and is clean before tests
    if TEST_IMAGES_DIR.exists():
        # Remove existing files
        for file in TEST_IMAGES_DIR.iterdir():
            if file.is_file():
                file.unlink()
    else:
        TEST_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    
    yield
    # Cleanup after test if necessary
    if TEST_IMAGES_DIR.exists():
        for file in TEST_IMAGES_DIR.iterdir():
            if file.is_file():
                file.unlink()

def test_fetch_method():
    """
    Test the fetch method of BBKnowledgeHookRealTimeDataSource.
    It mocks the Desktop.snapshot method to return predefined data.
    The fetch method is run in a separate thread and is stopped after a few iterations.
    The test verifies that subscribers receive the correct snapshot data.
    """
    # Mock data to return from snapshot
    mock_screenshot = np.zeros((100, 100, 3), dtype=np.uint8)
    mock_texts_with_rects = [("Hello", (10, 10, 50, 20)), ("World", (60, 60, 90, 80))]
    
    # Create a mock subscriber with a notify method
    mock_subscriber = MagicMock()
    
    # Instantiate the data source with a frequency of 1 second
    data_source = BBKnowledgeHookRealTimeDataSource(
        name="KnowledgeHooksTest",
        params={'frequency': 1},
        subscribers=[mock_subscriber]
    )
    
    # Function to run fetch and handle StopIteration to exit the loop
    def run_fetch():
        try:
            data_source.fetch()
        except StopIteration:
            pass  # Expected exception to stop the loop
        except Exception as e:
            print(f"Fetch loop exited with exception: {e}")
    
    # Start the fetch method in a separate thread
    fetch_thread = threading.Thread(target=run_fetch)
    fetch_thread.start()
    
    # Mock the Desktop.snapshot method to return predefined data and inject StopIteration after 3 calls
    with patch('brainboost_desktop_package.Desktop.Desktop.snapshot', return_value=(mock_screenshot, mock_texts_with_rects)):
        # Mock time.sleep to raise StopIteration after 3 calls
        sleep_call_count = {'count': 0}
        
        def mock_sleep(seconds):
            sleep_call_count['count'] += 1
            if sleep_call_count['count'] >= 3:
                raise StopIteration("Stopping fetch loop after 3 iterations")
            time.sleep.original_sleep(seconds)  # Call the real sleep for first 2 iterations
        
        # Patch time.sleep with our mock_sleep
        with patch('time.sleep', side_effect=mock_sleep):
            try:
                # Let the fetch loop run until StopIteration is raised
                fetch_thread.join(timeout=5)
            except StopIteration:
                pass
    
    # After the fetch loop is stopped, verify that the subscriber's notify method was called 3 times
    assert mock_subscriber.notify.call_count == 3, f"Expected notify to be called 3 times, got {mock_subscriber.notify.call_count}"
    
    # Verify the data sent to subscribers matches the mock data
    expected_snapshot_data = {
        'timestamp': pytest.approx(datetime.now().timestamp(), abs=5),  # Allow some leeway in timestamp
        'image': mock_screenshot,
        'texts_with_rects': mock_texts_with_rects
    }
    
    # Retrieve all calls to notify and verify their arguments
    for call in mock_subscriber.notify.call_args_list:
        args, kwargs = call
        snapshot_data = args[0]
        
        # Check that all required keys are present
        assert 'timestamp' in snapshot_data, "Snapshot data missing 'timestamp'"
        assert 'image' in snapshot_data, "Snapshot data missing 'image'"
        assert 'texts_with_rects' in snapshot_data, "Snapshot data missing 'texts_with_rects'"
        
        # Check that the image matches
        assert isinstance(snapshot_data['image'], np.ndarray), "Snapshot image is not a NumPy array"
        assert snapshot_data['image'].shape == mock_screenshot.shape, "Snapshot image shape mismatch"
        assert np.array_equal(snapshot_data['image'], mock_screenshot), "Snapshot image data mismatch"
        
        # Check that texts_with_rects matches
        assert snapshot_data['texts_with_rects'] == mock_texts_with_rects, "Snapshot texts_with_rects mismatch"

