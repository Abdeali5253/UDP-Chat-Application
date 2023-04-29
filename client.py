import socket
import tkinter as tk
from tkinter import filedialog
from changeProfile import ChangeForm
import traceback
import os
import constants


class ChatClient:
    # making the window
    def __init__(self, username):
        self.host = '127.0.0.1'
        self.port = None  # Initialize port to None
        self.username = username  # Store username
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.connected = False
        
        self.file_bytes = b''
        self.file_size = 0

        # Create the main window and widgets
        self.root = tk.Tk()
        self.root.title(self.username)
        
        #taking port input
        self.port_frame = tk.Frame(self.root)
        self.port_label = tk.Label(self.port_frame, text="Enter Port Number:")
        self.port_label.pack(side=tk.LEFT)
        self.port_entry = tk.Entry(self.port_frame, width=10)
        self.port_entry.pack(side=tk.LEFT)
        self.connect_button = tk.Button(self.port_frame, text='Connect', command=self.connect_to_server)
        self.connect_button.pack(side=tk.LEFT, padx=5)
        self.change_profile_button = tk.Button(self.port_frame, text='Change Profile', command=lambda: self.openform())
        self.change_profile_button.pack(side=tk.LEFT, padx=10)
        self.port_frame.pack()

        #box for msg display
        self.message_frame = tk.Frame(self.root)
        self.scrollbar = tk.Scrollbar(self.message_frame, orient=tk.VERTICAL)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.scrollbar_x = tk.Scrollbar(self.message_frame, orient=tk.HORIZONTAL)
        self.scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.message_listbox = tk.Listbox(self.message_frame, height=15, width=50, yscrollcommand=self.scrollbar.set, xscrollcommand=self.scrollbar_x.set)
        self.message_listbox.pack(side=tk.LEFT, fill=tk.BOTH)
        self.scrollbar.config(command=self.message_listbox.yview)
        self.scrollbar_x.config(command=self.message_listbox.xview)
        self.message_frame.pack()

        #message sending frame
        self.message_entry = tk.Entry(self.root, width=50)
        self.message_entry.pack(pady=5)

        #buttons
        self.button_frame = tk.Frame(self.root)
        self.send_button = tk.Button(self.button_frame, text='Send', command=self.send_message, state=tk.DISABLED)  # Disable send button by default
        self.send_button.pack(side=tk.LEFT)
        self.button_frame.pack()
        self.root.bind('<Return>', lambda event: self.send_message())
        self.send_file_button = tk.Button(self.button_frame, text='Send File', command=self.send_file, state=tk.DISABLED)
        self.send_file_button.pack(side=tk.LEFT, padx=10)
        self.button_frame.pack()

        self.root.protocol('WM_DELETE_WINDOW', self.quit)
        self.root.after(100, self.connect_to_server)
        self.root.mainloop()

    # opening the change profile window
    def openform(self):
        self.root.withdraw()
        ChangeForm(self.root, self.username)

    # connecting the clients to the server    
    def connect_to_server(self):
        # Get port number from user input
        port_str = self.port_entry.get()
        if port_str:
            self.port = int(port_str)
        
        if not self.port:
            self.message_listbox.insert(tk.END, 'Please enter a valid port number')
            return
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            username = self.username
            message_with_username = f'{username}:{f"has joined the chat"}'
            self.socket.sendto(message_with_username.encode(), (self.host, self.port))
            self.message_listbox.insert(tk.END, 'Connected to server') # adding client to server list
            self.socket.setblocking(0)
            self.connected = True
            self.send_button.config(state=tk.NORMAL)
            self.send_file_button.config(state=tk.NORMAL)
            self.root.after(100, self.receive_messages)
        except:
            self.message_listbox.insert(tk.END, 'Unable to connect to server') # if connection not build
    
    def receive_messages(self):
        try:
            packet, address = self.socket.recvfrom(constants.PACKET_SIZE)
            message = packet.decode()
            

            if message.startswith('file_size:'):
                file_info = message.split(':')
                
                self.file_size = int(file_info[1])
                self.file_name = file_info[2]
                self.receive_file(self.file_size, self.file_name)
                # self.file_bytes = b''
                # timeout = 0
                # while len(self.file_bytes) < self.file_size and timeout < 1000000:
                #     timeout +=1
                #     try:
                #         packet = self.socket.recvfrom(constants.PACKET_SIZE)[0]
                #         self.file_bytes += packet
                #         
                #     except socket.error as e:
                #         pass
                # # Save the file to disk
                # with open(self.file_name, 'wb') as f:
                #     f.write(self.file_bytes)
                #     

            else:
                self.message_listbox.insert(tk.END, message)
        except socket.error as e:
            if e.errno != 10035 and e.errno != 11: # Ignore "Resource temporarily unavailable" and "Resource temporarily unavailable" errors
                self.message_listbox.insert(tk.END, 'Error receiving message: {}'.format(e))
        except UnicodeDecodeError:
            self.message_listbox.insert(tk.END, 'Error decoding message')
        except:
            traceback.print_exc()
            self.message_listbox.insert(tk.END, 'Error receiving message')
        self.root.after(100, self.receive_messages)

    # Define the send_file method
    def send_file(self):
        filename = filedialog.askopenfilename()
        file_size = os.path.getsize(filename)
        

        username = self.username
        message_with_username = f'{username}:file_size:{file_size}:{filename}'
        self.socket.sendto(message_with_username.encode(), (self.host, self.port))

        with open(filename, 'rb') as f:
            filedata = b''
            while True:
                data = f.read(constants.PACKET_SIZE)
                filedata += data
                if len(data) == 0:
                    self.socket.sendto(b'', (self.host, self.port))
                    break
                self.socket.sendto(data, (self.host, self.port))

        # Send an empty packet to signal the end of the file transfer
        # self.socket.sendto(b'', (self.host, self.port))

    # sending the message to the server and other clients
    def send_message(self):
        message = self.message_entry.get()
        self.message_entry.delete(0, tk.END)
        if message:
            try:
                username = self.username
                message_with_username = f'{username}:{message}'
                self.socket.sendto(message_with_username.encode(), (self.host, self.port))
                # Add the sent message to the message listbox manually
                message_with_username = f'You: {message}'
                self.message_listbox.insert(tk.END, message_with_username)
            except socket.error as e:
                if e.errno != 10035: # Ignore "Resource temporarily unavailable" error
                    self.message_listbox.insert(tk.END, 'Error sending message: {}'.format(e))
            except:
                self.message_listbox.insert(tk.END, 'Error sending message')
        else:
            pass

    # Close socket and destroy tkinter window
    def quit(self):
        try:
            username = self.username
            message_with_username = f'{username}:{f"has left the chat"}'
            self.socket.sendto(message_with_username.encode(), (self.host, self.port))
        except:
            pass
        self.socket.close()
        self.root.destroy()

    def receive_file(self, file_size, file_name):
        
        
        file_data = b''
        file_name = f'media/{self.username}_{file_name}'

        timeout = 0
        with open(file_name, 'wb') as f:
            while timeout < constants.TIMEOUT and len(file_data) < file_size:
                timeout +=1
                try:
                    packet = self.socket.recvfrom(constants.PACKET_SIZE)[0]
                except socket.error as e:
                    continue
                file_data += packet
                
            f.write(file_data)
            f.close()

        file_size = os.path.getsize(file_name)
        
