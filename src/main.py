import threading

from common.sharedobject import SharedObject
from gcom_handler.gcomhandler import GCom_Server
from mps_server.server import MPS_Server

#instantiate shared object
so = SharedObject()

#create server
mps = MPS_Server(so)
gcm = GCom_Server(so)

#mpss thread
mpss_thread = threading.Thread(target=mps.serve_forever)

#gcmh thread
gcmh_thread = threading.Thread(target=gcm.serve_forever)

mpss_thread.start()
gcmh_thread.start()