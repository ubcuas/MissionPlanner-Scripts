import threading

from common.sharedobject import SharedObject
from gcom_handler.gcomhandler import gcomhandler
from mps_server.server import MPS_Server

#instantiate shared object
so = SharedObject()

#create server
mps = MPS_Server(so)
gch = gcomhandler(so)

#mps thread
mps_thread = threading.Thread(target=mps.serve_forever)

#gcomh thread
gch_thread = threading.Thread(target=gch.serve_forever)

mps_thread.start()
gch_thread.start()