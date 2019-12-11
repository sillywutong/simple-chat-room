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
    
    root.withdraw()
    WelcomeWindow(client_global.tkroot)
    if client_global.session:
    #LoginWindow(login)

        #_thread.start_new_thread(main_listener_thread,(client_global.session, client_global.tkroot))
        t = threading.Thread(target = main_listener_thread, args=(client_global.session, client_global.tkroot), daemon=True)
        t.start()
        #print("threading start.")
        #with open('test.png','rb') as imag_file:
            #img_bytes = imag_file.read()
            #img_bytes=bytes(img_bytes)

        #print("send login 1:")
        #client_global.session.send(msg_type=GeneralMessage.LOGIN, msg_body=['rarecu', '1278ghdfsdf88', img_bytes])
        #print("send login 2:")
        #client_global.session.send(msg_type=GeneralMessage.LOGIN, msg_body=['sdshdj', 'dshdjfhjsdhfj'])
        #root.withdraw()
        root.mainloop()

        try: 
            root.destroy()
        except tk.TclError:
            pass