import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from client import client_global
from common.message import GeneralMessage
from client.interface.login import LoginWindow
from client.interface.register import RegisterForm
from client.interface.buildsession import client_new_session
class WelcomePage(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.configure(bg=self.master.cget('bg'))
        self.session_establish = False

        self.headline = tk.Label(self, height=2, width=40, justify=tk.CENTER, text="Welcome to Secret Chat Room 1.0\n All of Your Messages Will be Encrypted.")
        self.headline.configure(bg=self.master.cget('bg'))
        self.headline.configure(font=("Helvetica","12"))
        

        self.headline.pack(anchor=tk.CENTER, padx=30, pady=10)

        self.dialogbox = tk.Text(self, height=10, width=40)
        self.dialogbox.configure(bg='#fafaf2')
        self.dialogbox.pack(anchor=tk.CENTER, pady=10, padx=40)
        
        connection = True
        if client_global.session == None:
            try:
                self.session_init()
            except ConnectionError:
                connection = False
                tk.messagebox.showerror(message="Server has no response.")
                self.destroy()
                client_global.tkroot.destroy()
        else:
            self.session_establish = True

        if connection:
            buttonFrame = tk.Frame(self)
            buttonFrame.configure(bg=self.cget('bg'))

            buttonFrame.pack(anchor=tk.CENTER, padx=40, pady=20)
            self.loginbtn = tk.Button(master=buttonFrame, text="   log  in   ", command=self.master.switch_login)
            self.registerbtn = tk.Button(master=buttonFrame, text="   sign up   ",command=self.master.switch_signup)
            self.loginbtn.grid(row=0, column=0, columnspan=2, padx=25)
            self.registerbtn.grid(row=0, column=2, columnspan=2, padx=25)
            self.pack(anchor=tk.CENTER)


    def session_init(self):
        self.dialogbox.insert(tk.END, "Connecting to Server...")
        client_global.session = client_new_session()
        self.dialogbox.insert(tk.END, "Done\n")
        self.dialogbox.insert(tk.END, "Exchanging session key... Done\n")
        self.dialogbox.insert(tk.END, "Encrypting session messages... Done\n")
        self.session_establish = True

        
