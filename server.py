import socket
import pickle
import threading
import sys
import os
import random

HOST: str = '26.100.122.124' # Masked Ip
PORT: int = 6969
host, port = HOST, PORT
SERVER_NAME: str = 'Server #0'
max_clients: int = 10

class Server:
    def __init__(self):
        self.server_cs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_cs.bind((host, port))
        self.clients = []
        self.current_client = None
        self.nicknames = {}
        self.message_list = []

    def handle_client(self, client_cs):
        threading.Thread(target=self.client_handler, args=(client_cs,)).start()

    def client_handler(self, client_cs):
        try:
            while True:
                data = client_cs.recv(1024)
                if not data:
                    break
                received_message = pickle.loads(data)
                self.command_handler(client_cs, received_message)
        except Exception as e:
            print(f'Error handling client: {e}')

    def broadcast_message(self, message):
        for client_cs in self.clients:
            client_cs.sendall(pickle.dumps(message))

    def command_handler(self, client_cs, message):
        if message.startswith("/nick"):
            args = message.split(" ")
            if len(args) != 2:
                self.broadcast_message("Error: /nick command requires a new nickname")
            else:
                if client_cs not in self.nicknames:
                    self.nicknames[client_cs] = args[1]
                else:
                    new_username = args[1]
                    old_username = self.nicknames[client_cs]
                    self.nicknames[client_cs] = new_username
                    self.message_list.append(f"{old_username} is now known as {new_username}")
                    self.broadcast_message(f"{old_username} is now known as {new_username}")
        elif message.startswith("/roll"):
            args = message.split(" ")
            if len(args) < 3 or len(args) > 4:
                self.broadcast_message("Error: /roll command requires 3 arguments (number of rolls, number of sides, and optional increment/decrement)")
            else:
                try:
                    num_rolls = int(args[1])
                    num_sides = int(args[2])
                    if num_rolls < 1 or num_rolls > 20:
                        self.broadcast_message("Error: Number of rolls must be between 1 and 20")
                    elif num_sides < 1 or num_sides > 100:
                        self.broadcast_message("Error: Number of sides must be between 1 and 100")
                    else:
                        increment = 0
                        if len(args) == 4:
                            increment = int(args[3])
                        rolls = [f"{random.randint(1, num_sides)}(+{increment})" if increment != 0 else f"{random.randint(1, num_sides)}" for _ in range(num_rolls)]
                        total = sum([int(roll.split("(")[0]) + int(roll.split("(")[1].split(")")[0]) if "(" in roll else int(roll) for roll in rolls])
                        roll_message = f"{self.nicknames[client_cs]} rolled {num_rolls}d{num_sides}"
                        if increment != 0:
                            roll_message += f" with an increment of {increment}"
                        roll_message += f": {', '.join(rolls)} = {total}"
                        self.message_list.append(roll_message)
                        self.broadcast_message(roll_message)
                except ValueError:
                    self.broadcast_message("Error: Invalid argument")
        else:
            if message not in self.message_list:  # Check if the message is new
                self.message_list.append(message)
                self.broadcast_message(f"{self.nicknames[client_cs]}: {message}")
            else:
                client_cs.sendall(pickle.dumps("Message received"))

    def run(self):
        self.server_cs.listen(max_clients)
        print("Server is listening...")
        while True:
            client_cs, address = self.server_cs.accept()
            print(f"New connection from {address}")
            self.clients.append(client_cs)
            threading.Thread(target=self.handle_client, args=(client_cs,)).start()


class Client:
    def __init__(self):
        self.cs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.message_list = []
        self.username = input("Enter your username: ")

    def connect(self):
        self.cs.connect((host, port))
        self.cs.sendall(pickle.dumps(f"/nick {self.username}"))

    def send_data(self):
        message = input("> ")
        self.command_handler(message)

    def command_handler(self, message):
        if message.startswith("/nick"):
            args = message.split(" ")
            if len(args) != 2:
                print("Error: /nick command requires a new nickname")
            else:
                self.cs.sendall(pickle.dumps(message))
        elif message.startswith("/roll"):
            args = message.split(" ")
            if len(args) < 3 or len(args) > 4:
                print("Error: /roll command requires 3 arguments (number of rolls, number of sides, and optional increment/decrement)")
            else:
                try:
                    num_rolls = int(args[1])
                    num_sides = int(args[2])
                    if num_rolls < 1 or num_rolls > 20:
                        print("Error: Number of rolls must be between 1 and 20")
                    elif num_sides < 1 or num_sides > 100:
                        print("Error: Number of sides must be between 1 and 100")
                    else:
                        increment = 0
                        if len(args) == 4:
                            increment = int(args[3])
                        self.cs.sendall(pickle.dumps(message))
                except ValueError:
                    print("Error: Invalid argument")
        else:
            self.cs.sendall(pickle.dumps(message))

    def receive_data(self):
        try:
            while True:
                data = self.cs.recv(1024)
                if not data:
                    break
                received_message = pickle.loads(data)
                if isinstance(received_message, list):
                    self.message_list = received_message
                    os.system('cls' if os.name == 'nt' else 'clear')
                    for message in self.message_list:
                        print(message)
                else:
                    print(received_message)
        except Exception as e:
            print(f'Error receiving data: {e}')

    def run(self):
        self.connect()
        threading.Thread(target=self.receive_data).start()
        while True:
            self.send_data()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "client":
        client = Client()
        client.run()
    else:
        server = Server()
        server.run()