import socket
import time

HOST = 'localhost'   # Symbolic name meaning all available interfaces
#SPORT = 5000 # Arbitrary non-privileged port  
RPORT = 4000 # Arbitrary non-privileged port

rsock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
print("Sockets Created")

counter = 0

while True:
    rsock.sendto(bytes("0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0", "utf-8"), (HOST, RPORT))

    msg = rsock.recv(1024).decode('utf-8')

    if (msg != "IDLE"):
        print(f"{counter}: {msg}")

    counter += 1

    time.sleep(1)