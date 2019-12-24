from client.client_global import friends
from tkinter import *
from client import client_global
from common.message import GeneralMessage
from client.interface.vertical_scrolled_frame import VerticalScrolledFrame

class GroupCreater(Frame):
    def __init__(self, master, gname):
        super().__init__(master)

        self.gname = gname
        self.friends = sorted(list(client_global.friends))
        self.vars = [IntVar() for i in range(len(self.friends))]
        scroll = VerticalScrolledFrame(self)
        scroll.pack(side=LEFT, fill=BOTH, expand=True)
        for i in range(len(self.friends)):
            cb = Checkbutton(scroll.interior, text=self.friends[i], variable=self.vars[i])
            cb.pack(fill=BOTH, expand=True)
        self.pack()
        b = Button(self, text='OK', command=self.on_ok)
        b.pack(side=BOTTOM)

    def on_ok(self):
        gms = []
        for i in range(len(self.friends)):
            if self.vars[i]:
                gms.append(self.friends[i])
        msg = [self.gname, gms + [client_global.current_user]]
        client_global.session.send(GeneralMessage.CREATE_G, msg)
        