from client.interface.buildsession import client_new_session
import socket
import select
from client import client_global
import io
from common.message import GeneralMessage
import tkinter as tk
from client.interface import *
from client.listener import main_listener_thread
import threading
import _thread
def run():
    root = tk.Tk()
    root.title("chatbot")
    client_global.tkroot = root
    
    WelcomeWindow()
    root.withdraw()
    if client_global.session.socket:
    #LoginWindow(login)

        #_thread.start_new_thread(main_listener_thread,(client_global.session, client_global.tkroot))
        t = threading.Thread(target = main_listener_thread, args=(client_global.session, client_global.tkroot), daemon=True)
        t.start()

        root.mainloop()

        try: 
            root.destroy()
        except tk.TclError:
            pass