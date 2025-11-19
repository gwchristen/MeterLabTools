import tkinter as tk
from tkinter import messagebox

class LoginDialog:
    def __init__(self, master):
        self.master = master
        master.title("Login")

        self.label = tk.Label(master, text="Enter your credentials:")
        self.label.pack()

        self.username_label = tk.Label(master, text="Username:")
        self.username_label.pack()
        self.username_entry = tk.Entry(master)
        self.username_entry.pack()

        self.password_label = tk.Label(master, text="Password:")
        self.password_label.pack()
        self.password_entry = tk.Entry(master, show="*")
        self.password_entry.pack()

        self.login_button = tk.Button(master, text="Login", command=self.login)
        self.login_button.pack()

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        # Add your authentication logic here
        if (username == "admin") and (password == "password"):
            messagebox.showinfo("Login Success", "You are logged in!")
            self.master.quit()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

if __name__ == '__main__':
    root = tk.Tk()
    login_dialog = LoginDialog(root)
    root.mainloop()