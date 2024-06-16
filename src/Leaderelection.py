import socket
import threading
import time
import random

class Node:
    def __init__(self, next_node_ip, next_node_port, port):
        self.uid = random.randint(1, 10000)  # Zufällige UID zwischen 1 und 10000
        self.next_node_ip = next_node_ip
        self.next_node_port = next_node_port
        self.port = port
        self.is_leader = False
        self.stop_flag = False
        self.leader_announced = False
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('0.0.0.0', port))
        print(f"Node {self.uid} initialized on port {port}, next node is {next_node_ip}:{next_node_port}\n")
        
    def start(self):
        threading.Thread(target=self.receive).start()
        time.sleep(1)
        self.send_uid(self.uid)
        print(f"Node {self.uid} starting election with UID {self.uid}")

    def receive(self):
        while not self.stop_flag:
            data, _ = self.socket.recvfrom(1024)
            received_message = data.decode()
            if received_message.isdigit():
                received_uid = int(received_message)
                print(f"Node {self.uid} received UID {received_uid}")
                self.process_uid(received_uid)
            elif received_message == "STOP_RING_PROCESS":
                print(f"Node {self.uid} received stop message from {self.next_node_ip}:{self.next_node_port}")
                self.stop_flag = True
            elif received_message == "LEADER_ANNOUNCEMENT":
                if not self.leader_announced and self.is_leader:
                    print(f"Node {self.uid}: Leader {self.uid} announced")
                    self.leader_announced = True
                    self.send_stop_message("STOP_RING_PROCESS")

    def send_uid(self, uid):
        message = str(uid).encode()
        print(f"Node {self.uid} sending UID {uid} to {self.next_node_ip}:{self.next_node_port}")
        self.socket.sendto(message, (self.next_node_ip, self.next_node_port))

    def process_uid(self, received_uid):
        if self.stop_flag:
            return
        
        if received_uid > self.uid:
            print(f"Node {self.uid}: Received UID {received_uid} is greater. Forwarding to {self.next_node_ip}:{self.next_node_port}")
            self.send_uid(received_uid)
        elif received_uid < self.uid:
            print(f"Node {self.uid}: Received UID {received_uid} is smaller. Ignoring.")
        elif received_uid == self.uid:
            if not self.is_leader:
                self.is_leader = True
                print(f"Node {self.uid} is the leader")
                self.send_leader_announcement()

    def send_leader_announcement(self):
        announcement = "LEADER_ANNOUNCEMENT"
        message_bytes = announcement.encode()
        
        self.socket.sendto(message_bytes, (self.next_node_ip, self.next_node_port))
        print(f"Node {self.uid} sent leader announcement to {self.next_node_ip}:{self.next_node_port}")

        # Sende an den vorherigen Node (Annahme: Ringstruktur)
        previous_port = self.port - 1 if self.port > 5000 else 5002
        if previous_port != self.port:  # Sende nicht an sich selbst
            self.socket.sendto(message_bytes, ('127.0.0.1', previous_port))
            print(f"Node {self.uid} sent leader announcement to 127.0.0.1:{previous_port}")
        else:
            print(f"Node {self.uid} skipped sending leader announcement to itself")

    def send_stop_message(self, message):
        message_bytes = message.encode()
        self.socket.sendto(message_bytes, (self.next_node_ip, self.next_node_port))
        print(f"Node {self.uid} sent stop message to {self.next_node_ip}:{self.next_node_port}")

    def stop(self):
        self.stop_flag = True
        self.socket.close()

# Beispiel-Nutzung
if __name__ == "__main__":
    node1 = Node(next_node_ip='127.0.0.1', next_node_port=5001, port=5000)
    node2 = Node(next_node_ip='127.0.0.1', next_node_port=5002, port=5001)
    node3 = Node(next_node_ip='127.0.0.1', next_node_port=5000, port=5002)

    node1.start()
    node2.start()
    node3.start()

    try:
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        node1.stop()
        node2.stop()
        node3.stop()
