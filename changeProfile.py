from tkinter import ttk,messagebox
import tkinter as tk


class ChangeForm:
    def __init__(self, master, username):
        self.root = tk.Toplevel(master)
        self.root.title('Change Form')
        self.old_username = username

        # Create the form widgets
        self.mainframe = ttk.Frame(self.root, padding='20 20 20 20')
        self.mainframe.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        self.mainframe.columnconfigure(0, weight=1)
        self.mainframe.rowconfigure(0, weight=1)

        self.username_label = ttk.Label(self.mainframe, text='New Username')
        self.username_label.grid(column=0, row=0, sticky=tk.W, pady=5)

        self.username_entry = ttk.Entry(self.mainframe)
        self.username_entry.grid(column=0, row=1, sticky=tk.W, pady=5)

        self.password_label = ttk.Label(self.mainframe, text='New Password')
        self.password_label.grid(column=0, row=2, sticky=tk.W, pady=5)

        self.password_entry = ttk.Entry(self.mainframe, show='*')
        self.password_entry.grid(column=0, row=3, sticky=tk.W, pady=5)

        self.confirm_button = ttk.Button(self.mainframe, text='Confirm', command=self.change)
        self.confirm_button.grid(column=0, row=4, sticky=tk.W, pady=10)
        self.mainframe.bind('<Return>', self.change)

    def change(self):
        from chat import Signup_login
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror('Error', 'Please enter a valid username and password')
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
            lines = f.readlines()

        with open('users.txt', 'w') as f:
            for line in lines:
                if line.strip().startswith(self.old_username + ':'):
                    # Rewrite new username to old username
                    f.write('{}:{}\n'.format(username, password))
                else:
                    f.write(line)

        messagebox.showinfo('Success', 'Change successful! , Please login again')
        self.root.destroy()
        Signup_login()


if __name__ == '__main__':
    root = tk.Tk()
    ChangeForm(root)
    root.mainloop()