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
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Initialize socket
        self.connected = False  # Initialize connected to False

        #file transfer variables
        self.file_bytes = b'' # Bytes of file
        self.file_size = 0 # Size of file

        # Create the main window and widgets
        self.root = tk.Tk() # tinker for gui
        self.root.title(self.username) # Set title to username
        
        #taking port input
        self.port_frame = tk.Frame(self.root)
        self.port_label = tk.Label(self.port_frame, text="Enter Port Number:")
        self.port_label.pack(side=tk.LEFT)
        self.port_entry = tk.Entry(self.port_frame, width=10)
        self.port_entry.pack(side=tk.LEFT)
        self.connect_button = tk.Button(self.port_frame, text='Connect', command=self.connect_to_server)
        self.connect_button.pack(side=tk.LEFT, padx=5 , pady=5)
        self.change_profile_button = tk.Button(self.port_frame, text='Change Profile', command=lambda: self.openform())
        self.change_profile_button.pack(side=tk.LEFT, padx=5 , pady=5)
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
        self.message_entry.focus_set()

        #buttons
        self.button_frame = tk.Frame(self.root)
        self.send_button = tk.Button(self.button_frame, text='Send', command=self.send_message, state=tk.DISABLED)  # Disable send button by default
        self.send_button.pack(side=tk.LEFT , pady=10)
        self.button_frame.pack()
        self.root.bind('<Return>', lambda event: self.send_message())
        self.send_file_button = tk.Button(self.button_frame, text='Send File', command=self.send_file, state=tk.DISABLED)
        self.send_file_button.pack(side=tk.LEFT, padx=10 , pady=10)
        self.button_frame.pack()
        self.emoji_button = tk.Button(self.root, text='😀', command=self.show_emoji_menu)
        self.emoji_button.pack(side=tk.LEFT, padx=10 , pady=10)
        self.button_frame.pack()

        #closing the window
        self.root.protocol('WM_DELETE_WINDOW', self.quit)
        self.root.after(100, self.connect_to_server)
        self.root.mainloop()

    def show_emoji_menu(self):
        # Create the menu
        self.emoji_menu = tk.Menu(self.root, tearoff=0)

        # Add each emoji to the menu
        for emoji in constants.emoji_list:
            self.emoji_menu.add_command(label=emoji, command=lambda e=emoji: self.add_emoji_to_message(e))

        # Display the menu at the current mouse location
        self.emoji_menu.post(self.root.winfo_pointerx(), self.root.winfo_pointery())

    def add_emoji_to_message(self, emoji):
        # Add the emoji to the message entry
        self.message_entry.insert(tk.END, emoji)

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
            self.connect_button.config(state=tk.DISABLED)
            self.root.after(100, self.receive_messages)
        except:
            self.message_listbox.insert(tk.END, 'Unable to connect to server') # if connection not build

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

    def receive_messages(self):
        try:
            packet, address = self.socket.recvfrom(constants.PACKET_SIZE)
            if packet.startswith(b'file_size:'):
                message = packet.decode()
                file_info = message.split(':')
                
                self.file_size = int(file_info[1])
                self.file_name = file_info[2]
                self.receive_file(self.file_size, self.file_name)
            else:
                message = packet.decode('utf-8')
                if message == 'Server is shutting down':
                    self.message_listbox.insert(tk.END, message)
                    new = 'Enter port to again connect to different server'
                    self.message_listbox.insert(tk.END, new)
                    self.send_button.config(state=tk.DISABLED)
                    self.send_file_button.config(state=tk.DISABLED)
                    self.connect_button.config(state=tk.NORMAL)
                    self.connected = False

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
        # Send the file size and name to the server
        message_with_username = f'{username}:file_size:{file_size}:{filename}'
        self.socket.sendto(message_with_username.encode(), (self.host, self.port))

        #inserting the message in the listbox
        message_with_username = f'You : Sending File{filename}'
        self.message_listbox.insert(tk.END, message_with_username)
        
        # Send the file data to the server
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
        self.socket.sendto(b'', (self.host, self.port))

    def receive_file(self, file_size, file_name):
        file_data = b''
        file_name = f'media\\{self.username}_{file_name}'
        self.message_listbox.insert(tk.END, f'Receiving file {file_name}')

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

    
        
