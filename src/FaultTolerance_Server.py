import socket
import threading
import time

LEADER_HOST = '127.0.0.1'
LEADER_PORT = 2345
HEARTBEAT_INTERVAL= 3

def send_heartbeat(): 
    while True: 
        try:
            with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s: 
                s.connect((LEADER_HOST,LEADER_PORT))
                s.sendall(b'Heartbeat')
        except ConnectionRefusedError:
                print ("The Leader is unreachable")
        time.sleep(HEARTBEAT_INTERVAL)

def start_server(): 
    threading.Thread(target=send_heartbeat, daemon=True).start()
    while True:
        time.sleep(1)

if __name__== "__main__" :
    start_server()


