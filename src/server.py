# import required modules 
import socket 
import threading 

HOST = '127.0.0.1' # das ist die Verbindung zum Netzwerk 
PORT = 1234 # you can use any port between o t 65535
LISTENER_LIMIT = 5 # wird nur 5 Verbindungen aufnehmen 
active_clients = [] # List of all currently connected users
groups = {}

# Function to listen for upcoming messages from a client 
# Bereich .listen
def listen_for_messages(client, username): 
    while True: 
        try:
            message = client.recv(2048).decode('utf-8')
            if message: 
                if message.startswith("/msg"):
                    _, target_username, msg = message.split(" ",2)
                    send_direct_message(username,target_username, msg)
                elif message.startswith("/group"): 
                    _, group_name, msg = message.split(" ", 2)
                    send_group_message(username, group_name, msg)
                else: 
                    final_msg = f"{username}'~'{message}"
                    send_multicast_message(final_msg)
            else:
                print(f"The messages sent from client {username} is empty")
        except: 
            remove_client(client)
            break
 
def send_direct_message(sender_username, target_username, message):
    for user in active_clients:
        if user[0] == target_username:
            final_msg = f"{sender_username} (private)~{message}"
            send_message_to_client(user[1], final_msg)
        break

def send_group_message(sender_username, group_name, message): 
    if group_name in groups:
        final_msg = f"{sender_username} (group {group_name})~{message}"
        for user in groups[group_name]:
            send_message_to_client(user[1], final_msg)
    else: 
        print(f"Group {group_name} does not exist")

def send_multicast_message(message):
    MULTICAST_GROUP = "224.0.0.0"
    MULTICAST_PORT = 49152
    
    multicast_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    multicast_sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
    multicast_sock.sendto(message.encode(), (MULTICAST_GROUP, MULTICAST_PORT))
    multicast_sock.close()

def send_message_to_client(client, message):
    client.sendall(message.encode())

def remove_client(client):
    for user in active_clients:
        if user[1] == client:
            active_clients.remove(user)
            break
# Function to handle client 
def client_handler(client):

    # Server will listen for client message that will
    # contain the username 
    while True:
        try:  
            username = client.recv(2048).decode('utf-8') # 2048 Byte von Daten können empfangen werdenv
            if username: 
                active_clients.append((username, client))
                break
            else: 
                print('Client username is empty')
        except:
            return
    threading.Thread(target=listen_for_messages, args=(client, username, )).start()
# main function 
def main():
    # creating the server socket
    # AF_INET: we are going to use IPv4 addresses 
    # SOCK_STREAM: we are using TCP packets for communication 
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try: 
        server.bind((HOST, PORT))
        print (f"Running the server on {HOST}{PORT}")
    except: 
        print(f"Unable to bind to host {HOST} and Port {PORT}") 
    server.listen(LISTENER_LIMIT)

    # This while loop will keep listening to client connections 
    while True: 
        client, address = server.accept()
        print(f"Successfully connected to client {address[0]} {address[1]} ")
        threading.Thread(target=client_handler, args=(client, )).start()

if __name__ == '__main__':
    main()
