import socket
import threading

HOST = '127.0.0.1'
PORT = 1234
MULTICAST_GROUP = "224.0.0.0"
MULTICAST_PORT = 49152

def listen_for_multicast_messages():
    multicast_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    multicast_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    multicast_sock.bind(('', MULTICAST_PORT))

    group = socket.inet_aton(MULTICAST_GROUP)
    mreq = group + socket.inet_aton(HOST)  # Packe die Multicast-Gruppenadresse und das lokale Host-Interface
    multicast_sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    while True:
        message, _ = multicast_sock.recvfrom(2048)
        if message:
            # Decodiere die Nachricht
            username, content = message.decode('utf-8').split('~')
            print(f"[{username}] {content}")

def send_message_to_server(client):
    while True:
        message = input('Message: ')
        if message:
            # Sende die Nachricht
            client.sendall(message.encode('utf-8'))
        else:
            print('Empty message')
            break

def communicate_to_server(client):
    username = input('Enter username:')
    if username:
        # Sende den Benutzernamen
        client.sendall(username.encode('utf-8'))
    else:
        print('Username cannot be empty')
        return

    threading.Thread(target=listen_for_multicast_messages).start()
    send_message_to_server(client)

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((HOST, PORT))
        print("Successfully connected to server")
    except Exception as e:
        print(f"Unable to connect to server {HOST} {PORT}: {e}")

    communicate_to_server(client)

if __name__ == '__main__':
    main()
