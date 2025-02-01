import sys
#from multiprocessing import Process
from threading import Thread

from server.utilities.connect_to_sysid import connect_to_sysid
from server.utilities.request_message_streaming import set_message_streaming_rates

from server.httpserver import HTTP_Server

# Process command line args
production = True
HOST, PORT, SOCKET_PORT = "localhost", 9000, 9001
STATUS_HOST, STATUS_PORT = "localhost", 1323
DISABLE_STATUS = False
MAVLINK_CONNECTION_STRING = 'udpin:localhost:14551'

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

    if '--mavlink-conn' in arguments.keys():
        MAVLINK_CONNECTION_STRING = arguments['--mavlink-conn'][0]
        
    print(f"Starting... HTTP server listening at {HOST}:{PORT}. " + ("" if DISABLE_STATUS else f"Status WS connecting to {STATUS_HOST}:{STATUS_PORT}."))

    mav_connection = connect_to_sysid(MAVLINK_CONNECTION_STRING, 1)
    if mav_connection == None:
        print(f"MAV connection failed")
    else:
        print(f"MAV connection successful")
    
    # set_message_streaming_rates(mav_connection) # optional - set update rate (applies to both MissionPlanner and this server)

    # Create server
    gcmh = HTTP_Server(mav_connection)
    #skth = Status_Client(so)

    # gcmh thread
    gcmh_thread = Thread(target=gcmh.serve_forever, args=[production, HOST, PORT])

    # #status websocket client thread
    # if not DISABLE_STATUS:
    #     skth_thread = Thread(target=skth.connect_to, args=[production, STATUS_HOST, STATUS_PORT])

    print("\nStarting threads...\n")

    gcmh_thread.start()
    # if not DISABLE_STATUS:
    #     skth_thread.start()

    gcmh_thread.join()
    # if not DISABLE_STATUS:
    #     skth_thread.join()
