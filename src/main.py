import sys
#from multiprocessing import Process
from threading import Thread

from server.common.sharedobject import SharedObject
from server.gcomhandler import GCOM_Server
from server.mps_server import MPS_Server
from server.socket_handler import Socket_Handler

# Process command line args
production = True
HOST, PORT, SOCKET_PORT = "localhost", 9000, 9001
if __name__ == "__main__":
    # Extract arguments
    arguments = {}
    for arg in sys.argv:
        k, *v = arg.split('=', 1)
        arguments[k] = v

    # Process options
    if '--dev' in arguments.keys():
        print("Starting server in development")
        production = False
    else:
        print("Starting server in production")
    
    if '--port' in arguments.keys():
        PORT = int(arguments['--port'][0])

    if '--socket-port' in arguments.keys():
        SOCKET_PORT = int(arguments['--socket-port'][0])
        
    print(f"HTTPServer listening on port {PORT}")

    # Instantiate shared object
    so = SharedObject()

    # Create server
    mpss = MPS_Server(so)
    gcmh = GCOM_Server(so)
    skth = Socket_Handler(so)

    # mpss thread
    mpss_thread = Thread(target=mpss.serve_forever)

    # gcmh thread
    gcmh_thread = Thread(target=gcmh.serve_forever, args=[production, HOST, PORT])

    mpss_thread.start()
    gcmh_thread.start()

    skth.serve_forever(production, HOST, SOCKET_PORT)
