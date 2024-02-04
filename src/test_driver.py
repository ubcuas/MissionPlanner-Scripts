import os
import sys
import importlib
import sys
import json
import requests
#from multiprocessing import Process
from threading import Thread
from server.common.sharedobject import SharedObject
from server.gcomhandler import GCOM_Server
from server.mps_server import MPS_Server
from server.socket_handler import Socket_Handler
import pytest
from server.custom_thread import CustomThread

# Process command line args
production = True
HOST, PORT, SOCKET_PORT = "localhost", 9000, 9001
so = None
# base_url = "http://localhost:9000"
class TestClass:

    @pytest.fixture(autouse=True)
    def before(self):
        # Instantiate shared object
        so = SharedObject()

        # Create server
        try:
            mpss = MPS_Server(so)
            gcmh = GCOM_Server(so)
            skth = Socket_Handler(so)
        except e:
            print(f"Error!: {e}")

        # mpss thread
        mpss_thread = CustomThread(target=mpss.serve_forever)

        # gcmh thread
        gcmh_thread = CustomThread(target=gcmh.serve_forever, args=[production, HOST, PORT])

        mpss_thread.start()
        gcmh_thread.start()
        
        response = requests.get(f"http://{HOST}:{PORT}/queue")
        print(f"response: {response}")
        yield

        print("Teardown for after test script")
        mpss_thread.stop()
        gcmh_thread.stop()


    def test_get_queue(self):
        print("test")
        data = [
            {
                "id": 1,
                "name": "Alpha",
                "longitude": 38.83731,
                "latitude": -20.48321,
                "altitude": 50.7
            },
            {
                "id": 2,
                "name": "Beta",
                "longitude": 38.83731,
                "latitude": -20.48321,
                "altitude": 60
            }
        ]
        requests.post(f"http://{HOST}:{PORT}/queue", json=data)
        response = requests.get(f"http://{HOST}:{PORT}/queue")
        print(f'response : {response}')
        print(f'response result : {response.json()}') 
        assert response.status_code == 200

    def test_get_status(self):
        response = requests.get(f'http://{HOST}:{PORT}/status')
        print(f'response : {response}')
        print(f'response result : {response.json()}') 
        assert response.status_code == 200
        
    # # Add more tests for other endpoints...

    def test_get_lock(self): 
        response = requests.get(f'http://{HOST}:{PORT}/lock')
        print(f'response result : {response}') 
        assert response.status_code == 200

    def test_get_unlock(self):
        response = requests.get(f'http://{HOST}:{PORT}/unlock')
        print(f'response : {response}')
        assert response.status_code == 200

    def test_post_takeoff(self):
        data = {
                "altitude": 50.7
            }
        response = requests.post(f'http://{HOST}:{PORT}/takeoff', json=data)
        print(f'response : {str(response)}')
        assert response.status_code == 200

    def test_get_rtl(self):
        response = requests.get(f'http://{HOST}:{PORT}/rtl')
        print(f'response : {response}')
        assert response.status_code == 200

    def test_post_rtl(self):
        data = {
                "altitude": 69
            }
        response = requests.post(f'http://{HOST}:{PORT}/rtl', json=data)
        print(f'response : {response}')
        assert response.status_code == 200

    # def test_post_queue(self):
    #     # Prepare a JSON payload for testing
    #     payload = [
    #         {"id": 1, "name": "Waypoint 1", "latitude": 10.0, "longitude": 20.0, "altitude": 30},
    #         # Add more waypoints as needed
    #     ]
    #     response = requests.post('/queue', json=payload)
    #     assert response.status_code == 200
    #     # Add your assertion based on expected response

# print("Current Directory:", current_directory)   