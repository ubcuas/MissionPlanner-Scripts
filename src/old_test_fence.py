import pytest
import json
import unittest
import time
from unittest.mock import patch, MagicMock
from server.common.sharedobject import SharedObject

queue_endpoint = "/queue"
        
        
class TestMyModule(unittest.TestCase):
    @patch("server.common.sharedobject.SharedObject")
    def test_fence_inclusive(self, app):
        # Mock the app
        app = MagicMock()

        # Set up the shared object
        shared_obj = SharedObject()
        shared_obj.fence = {"type": "inclusive", "lat": 0, "lon": 0, "radius": 100}
        
        app.put.return_value.status_code = 400
        
        
        # Call the function to test
        response = app.put(queue_endpoint)
        result = json.dumps(response)

        print(response)
       


