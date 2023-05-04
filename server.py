import socket
import threading
import tkinter as tk
import os
import constants
import traceback

class ChatServer:
    # making the window
    def __init__(self):
        # Server attributes
        self.host = '127.0.0.1'  # local host to connect
        self.port = None  # port for server used
        self.max_connections = 250  # max 250 clients can connect
        # clients are stored as dictionary with client_address as key and username as value
        self.clients = {}

        # Create the main window and widgets
        self.root = tk.Tk()  # tinker for gui
        self.root.title('Chat Server')

        # Port input
        self.port_entry_frame = tk.Frame(self.root)
        self.port_entry_label = tk.Label(
            self.port_entry_frame, text='Enter port number:')
        self.port_entry_label.pack(side=tk.LEFT)
        self.port_entry = tk.Entry(self.port_entry_frame, width=10)
        self.port_entry.pack(side=tk.LEFT, padx=5)
        self.listen_button = tk.Button(
            self.port_entry_frame, text='Listen', command=self.start_server)
        self.listen_button.pack(side=tk.LEFT)
        self.root.bind('<Return>', lambda event: self.start_server())
        self.port_entry_frame.pack(pady=5)

        # initializing box
        self.message_frame = tk.Frame(self.root)
        self.scrollbar = tk.Scrollbar(self.message_frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.message_listbox = tk.Listbox(
            self.message_frame, height=15, width=50, yscrollcommand=self.scrollbar.set)
        self.message_listbox.pack(side=tk.LEFT, fill=tk.BOTH)
        self.scrollbar.config(command=self.message_listbox.yview)
        self.message_frame.pack()

        self.root.protocol('WM_DELETE_WINDOW', self.quit)
        self.root.mainloop()

    # Starting the server
    def start_server(self):
        self.port = int(self.port_entry.get())
        self.server_socket = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM)  # basic socket connection
        self.server_socket.bind((self.host, self.port))
        self.listen_button.config(state=tk.DISABLED)
        threading.Thread(target=self.receive_messages).start()

    def receive_messages(self):
        try:
            while True:
                data, client_address = self.server_socket.recvfrom(constants.PACKET_SIZE)
                if data:
                    username, message_text = data.decode().split(':', 1)
                    self.clients[client_address] = username

                    if message_text.startswith('file_size'):
                        file_info = message_text.split(':')
                        file_size = int(file_info[1])
                        filename = file_info[-1].split('/')[-1]

                        self.receive_file(file_size, filename)
                        continue

                    message_with_username = f'{username}: {message_text}'

                    # Send the message to all clients except the sender
                    for recipient_address, recipient_username in self.clients.items():
                        if recipient_address != client_address:
                            self.server_socket.sendto(
                                message_with_username.encode(), recipient_address)

                    # Display the message on the server GUI
                    formatted_message = message_with_username
                    self.message_listbox.insert(tk.END, formatted_message)
        except Exception:
            traceback.print_exc()

    
    # Broadcast message to all the clients and server itself
    def broadcast(self, message, sender_address=None, is_server_message=False, file_path=None):
        message_with_username = ''
        if not is_server_message:
            username = self.clients[sender_address]
            message_with_username = f'{username}: '
        message_with_username += message

        # Send the message to all clients except the sender
        for client_address, username in self.clients.items():
            if client_address != sender_address:
               
                    # Send text message
                    self.server_socket.sendto(
                        message_with_username.encode(), client_address)
                    self.message_listbox.insert(tk.END, message_with_username)

        # Display the message on the server GUI
        formatted_message = message_with_username
        self.message_listbox.insert(tk.END, formatted_message)
    
    
    # receiving the file from the client
    def receive_file(self, file_size, file_name):
        file_data = b''
        file_name = f'media/{file_name}'

        with open(file_name, 'wb') as f:
            while True:
                packet, client_address = self.server_socket.recvfrom(
                    constants.PACKET_SIZE)
                file_data += packet
                if len(packet) == 0:
                    break
            f.write(file_data)
            f.close()

        for recipient_address, recipient_username in self.clients.items():
            if recipient_address != client_address:
                self.send_file(file_name, recipient_address,
                               recipient_username)

    def send_file(self, filename, client_address, username):
        packet_size = constants.PACKET_SIZE
        file_size = os.path.getsize(filename)
        filename = filename.split('/')[-1]
        print('file_size:', file_size) 
       
        message_with_username = f'file_size:{file_size}:{filename}'
        self.server_socket.sendto(
            message_with_username.encode(), client_address)
        
        with open('media\\'+filename, 'rb') as f:
            filedata = b''
            while True:
                data = f.read(constants.PACKET_SIZE)
                filedata += data
                if len(data) == 0:
                    self.server_socket.sendto(b'', client_address)
                    break
                self.server_socket.sendto(data, client_address)
                print(len(filedata))
                # self.message_listbox.insert(tk.END, f'Sending {filename} to {username}')
        return

    # Stopping the server and disconnecting all the clients
    def stop_server(self):
        # Send a message to all clients indicating that the server is shutting down
        for client_address in self.clients:
            self.server_socket.sendto('Server is shutting down'.encode(), client_address)
        
        self.server_socket.close()
        self.root.destroy()

    # close the server socket
    def quit(self):
        self.stop_server()


if __name__ == '__main__':
    ChatServer()
