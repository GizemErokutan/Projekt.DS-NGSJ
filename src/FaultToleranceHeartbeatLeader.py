import socket
import threading
import time

LEADER_HOST = '127.0.0.1'
LEADER_PORT = 2345
TIMEOUT = 6

server_last_heartbeat = {}

def monitor_servers():
    while True: 
        currentTime = time.time()
        for server, last_heartbeat in list(server_last_heartbeat.items()):
            if currentTime - last_heartbeat > TIMEOUT:
                print(f"Server{server} is down.")
                del server_last_heartbeat[server]
        time.sleep(1)

def handle_server(conn, addr):
    print(f"Connection established by {addr}")
    with conn: 
        while True: 
            try: 
                data = conn.recv(1024)
                if not data: 
                    break 
                server_last_heartbeat[addr] = time.time()
            except ConnectionResetError:
                break
    print(f"Disconnected from {addr}.")

def start_leader():
    with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s: 
        s.bind((LEADER_HOST,LEADER_PORT))
        s.listen()
        print(f"Leader is running on {LEADER_HOST}:{LEADER_PORT}")

        threading.Thread(target=monitor_servers, daemon=True).start()

        while True: 
               conn, addr = s.accept()
               threading.Thread(target=handle_server, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    start_leader()



