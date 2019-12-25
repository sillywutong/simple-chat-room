from tkinter import *
from client.client_global import contacts_private
import tkinter as tk
from tkinter import ttk
from client.listener import remove_listener

class ChatForm(Toplevel):
    def __init__(self, master, **args):
        super().__init__(master, **args)
        self.master=master
        self.child = None
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
    def on_closing(self):
        if not self.child is None:
            remove_listener(self.child.handle)
        self.destroy()