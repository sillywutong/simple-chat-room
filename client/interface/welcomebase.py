import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from client import client_global
from common.message import GeneralMessage
from client.interface.register import RegisterForm
from client.interface.login import LoginWindow
from client.interface.welcome import WelcomePage
from client.listener import *

class WelcomeWindow(tk.Toplevel):
    def __init__(self, root=None):
        super().__init__(master=root, takefocus=True)
        self.root = root
        self.geometry('400x300')
        self.configure(bg="#DADFE6")

        self.welcomeframe = WelcomePage(self)
    
    def switch_login(self):
        self.welcomeframe.destroy()
        self.loginform = LoginWindow(self)
    
    def switch_signup(self):
        self.welcomeframe.destroy()
        self.signupform = RegisterForm(self)
    def cancel_login(self):
        remove_listener(self.loginform.handle_response)
        self.loginform.destroy()
        self.welcomeframe = WelcomePage(self)
    def cancel_register(self):
        remove_listener(self.signupform.handle_response)
        self.signupform.destroy()
        self.welcomeframe = WelcomePage(self)
    def register_to_login(self):
        remove_listener(self.signupform.handle_response)
        self.signupform.destroy()
        self.loginform = LoginWindow(self)