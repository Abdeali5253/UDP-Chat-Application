import tkinter as tk
from tkinter import ttk, messagebox
from client import ChatClient

class SignupForm:
    def __init__(self, master):
        self.root = master
        self.root.title('Signup Form')
        self.root.geometry("250x250+{}+{}".format(
            self.root.winfo_screenwidth() // 2 - 125,
            self.root.winfo_screenheight() // 2 - 125))

        # Create the form widgets
        self.mainframe = ttk.Frame(self.root, padding='20 20 20 20')
        self.mainframe.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        self.mainframe.columnconfigure(0, weight=1)
        self.mainframe.rowconfigure(0, weight=1)

        self.username_label = ttk.Label(self.mainframe, text='Username')
        self.username_label.grid(column=0, row=0, sticky=tk.W, pady=5)

        self.username_entry = ttk.Entry(self.mainframe)
        self.username_entry.grid(column=0, row=1, sticky=tk.W, pady=5)

        self.password_label = ttk.Label(self.mainframe, text='Password')
        self.password_label.grid(column=0, row=2, sticky=tk.W, pady=5)

        self.password_entry = ttk.Entry(self.mainframe, show='*')
        self.password_entry.grid(column=0, row=3, sticky=tk.W, pady=5)

        self.confirm_password_label = ttk.Label(self.mainframe, text='Confirm Password')
        self.confirm_password_label.grid(column=0, row=4, sticky=tk.W, pady=5)

        self.confirm_password_entry = ttk.Entry(self.mainframe, show='*')
        self.confirm_password_entry.grid(column=0, row=5, sticky=tk.W, pady=5)

        self.signup_button = ttk.Button(self.mainframe, text='Signup', command=self.signup)
        self.signup_button.grid(column=0, row=6, pady=10)

        self.mainframe.grid_rowconfigure(7, minsize=20)

        # Bind the Signup button with Enter key
        self.root.bind('<Return>', self.signup)

    def signup(self, event=None):
        username = self.username_entry.get()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()

        if not username or not password or not confirm_password:
            messagebox.showerror('Error', 'Please enter a valid username and password')
            return

        # Check for matching passwords
        if password != confirm_password:
            messagebox.showerror('Error', 'Passwords do not match')
            return

        # Check for username criteria
        if not (any(c.islower() for c in username) and any(c.isupper() for c in username)):
            messagebox.showerror('Error', 'Username must contain both small and capital letters')
            return

        # Check for password criteria
        if len(password) < 8:
            messagebox.showerror('Error', 'Password must be at least 8 characters long')
            return

        with open('users.txt', 'r') as f:
            for line in f:
                if line.strip().startswith(username + ':'):
                    messagebox.showerror('Error', 'Username already exists. Please choose another one.')
                    return

        with open('users.txt', 'a') as f:
            f.write('{}:{}\n'.format(username, password))

        messagebox.showinfo('Success', 'Signup successful!')
        self.root.destroy()
        Signup_login()
        
class LoginForm:
    def __init__(self, master):
        self.master = master
        self.master.title('Login Form')
        self.master.geometry("250x150+{}+{}".format(
            self.master.winfo_screenwidth() // 2 - 125,
            self.master.winfo_screenheight() // 2 - 125))

        self.mainframe = ttk.Frame(self.master, padding='20 20 20 20')
        self.mainframe.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        self.mainframe.columnconfigure(0, weight=1)
        self.mainframe.rowconfigure(0, weight=1)

        self.username_frame = ttk.Frame(self.mainframe, padding='0 5 0 0')
        self.username_frame.grid(column=0, row=0, sticky=tk.W)

        self.username_label = ttk.Label(self.username_frame, text='Username:')
        self.username_label.grid(column=0, row=0, sticky=tk.W)

        self.username_entry = ttk.Entry(self.username_frame, width=20)
        self.username_entry.grid(column=1, row=0, sticky=tk.W, padx=5)

        self.password_frame = ttk.Frame(self.mainframe, padding='0 5 0 0')
        self.password_frame.grid(column=0, row=1, sticky=tk.W)

        self.password_label = ttk.Label(self.password_frame, text='Password:')
        self.password_label.grid(column=0, row=0, sticky=tk.W)

        self.password_entry = ttk.Entry(self.password_frame, show='*', width=20)
        self.password_entry.grid(column=1, row=0, sticky=tk.W, padx=5)

        self.login_button = ttk.Button(self.mainframe, text='Login', command=self.login)
        self.login_button.grid(column=0, row=2, sticky=tk.W, pady=10)
        self.master.bind('<Return>', lambda event: self.login())


    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror('Error', 'Please enter a valid username and password')
            return

        with open('users.txt', 'r') as f:
            for line in f:
                if line.strip() == '{}:{}'.format(username, password):
                    self.master.destroy()  # close the login form
                    client = ChatClient(username)  # create instance of ChatClient
                    client.start()  # start the chat client
                    return

        messagebox.showerror('Error', 'Invalid username or password')
        return

class Signup_login:
    def __init__(self):
        self.signup_form = None
        self.login_form = None
        
        # Create the main window and widgets
        self.root = tk.Tk()
        self.root.title('User Signup/Login')
        
        # Set the window size and center it on the screen
        self.root.geometry('300x200')
        self.root.eval('tk::PlaceWindow %s center' % self.root.winfo_toplevel())
        
        # Create the Signup/Login buttons
        self.signup_button = tk.Button(self.root, text='Signup', command=self.show_signup, font=('Arial', 14), padx=20, pady=10)
        self.signup_button.pack()
        self.login_button = tk.Button(self.root, text='Login', command=self.show_login, font=('Arial', 14), padx=20, pady=10)
        self.login_button.pack(pady=10)
        
        # Add a border around the buttons
        for btn in [self.signup_button, self.login_button]:
            btn.config(border=2, relief='groove')
        
        # Set the background color of the buttons and window
        self.root.config(bg='#F0F0F0')
        self.signup_button.config(bg='#FFFFFF')
        self.login_button.config(bg='#FFFFFF')
        
        # Center the buttons in the window
        self.signup_button.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.login_button.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        
        self.root.protocol('WM_DELETE_WINDOW', self.quit)
        self.root.mainloop() 

    def show_signup(self):
        self.signup_window = tk.Toplevel(self.root)
        self.signup_form = SignupForm(self.signup_window)
        self.root.withdraw()
        
    def show_login(self):
        self.login_window = tk.Toplevel(self.root)
        self.login_form = LoginForm(self.login_window)
        self.root.withdraw()

    def quit(self):
        try:
            self.socket.close()
        except:
            pass
        self.root.destroy()

if __name__ == '__main__':
    Signup_login()
