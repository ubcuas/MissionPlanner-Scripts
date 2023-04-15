import sys
import threading

from server.common.sharedobject import SharedObject
from server.gcomhandler import GCOM_Server
from server.mps_server import MPS_Server

# Process command line args
production = True
HOST, PORT = "localhost", 9000
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
        
    print(f"HTTPServer listening on port {PORT}")

# Instantiate shared object
so = SharedObject()

# Create server
mps = MPS_Server(so)
gcm = GCOM_Server(so)

# mpss thread
mpss_thread = threading.Thread(target=mps.serve_forever)

# gcmh thread
gcmh_thread = threading.Thread(target=gcm.serve_forever, args=[production, HOST, PORT])

mpss_thread.start()
gcmh_thread.start()