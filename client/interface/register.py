import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from client import client_global
from common.message import GeneralMessage
from client.listener import add_listener, remove_listener
import re

class RegisterForm(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master=master

        #self.master.configure(bg="#fafaf2")
        self.master.resizable(width=False, height=False)
        self.configure(bg=self.master.cget('bg'))
        
        self.username = tk.Entry(self)
        self.password1 = tk.Entry(self, show="*")
        self.password2 = tk.Entry(self, show="*")

        self.usernamelb = tk.Label(self, text="Username:", bg=self.cget('bg'))
        self.passwordlb = tk.Label(self, text="Password:", bg=self.cget('bg'))
        self.passwordlb2 = tk.Label(self, text="Confirm again:", bg=self.cget('bg'))

        buttonFrame = tk.Frame(master=self, bg=self.cget('bg'))
        self.okbtn = ttk.Button(master=buttonFrame, text="sign up", command=self.sign_up_clicked)
        self.cancelbtn = ttk.Button(master=buttonFrame, text="cancel", command=self.master.cancel_register)

        self.usernamelb.grid(row=0, sticky=tk.E, padx=6)
        self.username.grid(row=0, column=1, padx=6, pady=20)
        self.passwordlb.grid(row=1, sticky=tk.E, padx=6)
        self.password1.grid(row=1, column=1, padx=6, pady=20)
        self.passwordlb2.grid(row=2, sticky=tk.E, padx=6)
        self.password2.grid(row=2, column=1, padx=6, pady=20)

        buttonFrame.grid(row=3, rowspan=2, columnspan=2, pady=10, ipady=20)
        self.okbtn.grid(row=0, column=0, padx=10)
        self.cancelbtn.grid(row=0, column=1,padx=10)

        self.pack(anchor=tk.CENTER, padx=30, pady=30)
        self.master.title("Welcome to Chatbot")
        add_listener(self.handle_response)
        print("register listener added.")


    def sign_up_clicked(self):
        username = self.username.get()
        password1 = self.password1.get()
        password2 = self.password2.get()

        if len(username)==0:
            tk.messagebox.showinfo(message="Username can't be empty, please enter your username.")
        elif len(password1)<8 or len(password2)<8:
            tk.messagebox.showinfo(message="The length of password should at least be 8.")
        elif password1 != password2:
            tk.messagebox.showinfo(message="Passwords entered twice are inconsistent, please check again.")
        elif not re.match(r'^[a-zA-Z0-9_-]{4,16}$', "abwc"):
            tk.messagebox.showinfo(message="username should only include numbers, letters and '_'")
        else:
            client_global.session.send(GeneralMessage.REGISTER, [username, password1])
    def cancel_clicked(self):
        self.master.master.username.delete(0, tk.END)
        self.master.master.password.delete(0, tk.END) 
        self.master.destroy()
    def handle_response(self, msg_type, msg_body):
        if msg_type == GeneralMessage.REG_FAIL:
            messagebox.showerror(message="username has been registered, please choose another one.")
        elif msg_type == GeneralMessage.REG_OK:
            messagebox.showinfo(message="Congratulations! You are now a new member!")
            remove_listener(self.handle_response)
            self.master.register_to_login()
