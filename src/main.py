import sys
#from multiprocessing import Process
from threading import Thread

from server.common.sharedobject import SharedObject
from server.gcomhandler import GCOM_Server
from server.mps_server import MPS_Server
from server.status_wsclient import Status_Client

# Process command line args
production = True
HOST, PORT, SOCKET_PORT = "localhost", 9000, 9001
STATUS_HOST, STATUS_PORT = "localhost", 1323
DISABLE_STATUS = False
if __name__ == "__main__":
    # Extract arguments
    arguments = {}
    for arg in sys.argv:
        k, *v = arg.split('=', 1)
        arguments[k] = v

    # Process options
    if "--test" in arguments.keys():
        print("starting test environment")
        
    if '--dev' in arguments.keys():
        print("Starting server in development")
        production = False
    else:
        print("Starting server in production")
    
    if '--port' in arguments.keys():
        PORT = int(arguments['--port'][0])

    if '--socket-port' in arguments.keys():
        SOCKET_PORT = int(arguments['--socket-port'][0])

    if '--status-host' in arguments.keys():
        STATUS_HOST = arguments['--status-host'][0]
    
    if '--status-port' in arguments.keys():
        STATUS_PORT = arguments['--status-port'][0]

    if '--disable-status' in arguments.keys():
        DISABLE_STATUS = True
        
    print(f"Starting... HTTP server listening at {HOST}:{PORT}. " + ("" if DISABLE_STATUS else f"Status WS connecting to {STATUS_HOST}:{STATUS_PORT}."))

    # Instantiate shared object
    so = SharedObject()

    # Create server
    mpss = MPS_Server(so)
    gcmh = GCOM_Server(so)
    skth = Status_Client(so)

    # mpss thread
    mpss_thread = Thread(target=mpss.serve_forever)

    # gcmh thread
    gcmh_thread = Thread(target=gcmh.serve_forever, args=[production, HOST, PORT])

    #status websocket client thread
    if not DISABLE_STATUS:
        skth_thread = Thread(target=skth.connect_to, args=[production, STATUS_HOST, STATUS_PORT])

    print("\nStarting threads...\n")

    mpss_thread.start()
    gcmh_thread.start()
    if not DISABLE_STATUS:
        skth_thread.start()

    mpss_thread.join()
    gcmh_thread.join()
    if not DISABLE_STATUS:
        skth_thread.join()
