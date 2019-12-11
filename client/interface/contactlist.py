import tkinter as tk
from tkinter import ttk
from common.message import GeneralMessage
from client import client_global
from tkinter import simpledialog
from tkinter import messagebox
from client.listener import add_listener
class ContactItem(tk.Frame):
    def __init__(self, parent, onclick):
        super().__init__(self, parent)

        self.pack()
class VerticalScrolledFrame(tk.Frame):
    """A pure Tkinter scrollable tk.Frame that actually works!

    * Use the 'interior' attribute to place widgets inside the scrollable tk.Frame
    * Construct and pack/place/grid normally
    * This tk.Frame only allows vertical scrolling

    """

    def __init__(self, parent, *args, **kw):
        tk.Frame.__init__(self, parent, *args, **kw)

        # create a canvas object and a vertical scrollbar for scrolling it
        vscrollbar = tk.Scrollbar(self, orient=tk.VERTICAL)
        vscrollbar.pack(fill=tk.Y, side=tk.RIGHT, expand="no")
        canvas = tk.Canvas(self, bd=0, highlightthickness=0,
                        yscrollcommand=vscrollbar.set)
        canvas.pack(side="left", fill="both", expand="yes")
        vscrollbar.config(command=canvas.yview)

        # reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # create a tk.Frame inside the canvas which will be scrolled with it
        self.interior = interior = tk.Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior,
                                           anchor=tk.NW)

        # track changes to the canvas and tk.Frame width and sync them,
        # also updating the scrollbar
        def _configure_interior(event):
            # update the scrollbars to match the size of the inner tk.Frame
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the canvas's width to fit the inner tk.Frame
                canvas.config(width=interior.winfo_reqwidth())

        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the inner tk.Frame's width to fill the canvas
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())

        canvas.bind('<Configure>', _configure_canvas)

        return
class ContactList(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.parent.resizable(width=False, height=False)
        self.parent.geometry('300x600')
        self.configure(bg='#ffffff')

        top_color='#525D66'
        header = tk.Frame(self)
        header.configure(bg=top_color)
        header.pack(anchor=tk.N, side='top', fill='x', ipadx=30)

        self.topUserInfo = tk.Label(master=header, text='Hello!  '+client_global.current_user['username'])
        self.topUserInfo.configure(bg=top_color,font=('Microsoft Yahei UI',"12"))
        self.topUserInfo.pack(anchor=tk.W, padx=10,pady=(15, 15))

        

        btnbkg='#525D66'
        btnframe=tk.Frame(self)
        btnframe.configure(bg=btnbkg)

        btnframe.pack(anchor=tk.N, side='top', fill='x',ipadx=0, ipady=0)

        self.add_friend = ttk.Button(btnframe, text="          New Friend        ", command=self.on_new_friend)
        self.new_group = ttk.Button(btnframe, text="        Create Group       ", command=self.on_new_group)
        #self.join_group = ttk.Button(btnframe, text="   Invite    ", command=self.on_join_group)

        self.add_friend.grid(row=0,column=0,columnspan=2)
        self.new_group.grid(row=0,column=2, columnspan=2)
        #self.join_group.grid(row=0,column=2)
        self.scroll = VerticalScrolledFrame(self)
        self.scroll.pack(fill="both", expand="yes")
        self.pack(fill="both",expand="yes")
        self.contacts=[]

        add_listener(self.handle_message)




    def on_new_friend(self):
        username = simpledialog.askstring(title="Add new friend", prompt="Please input a username", parent=None)
        if username:
            client_global.session.send(GeneralMessage.ADD_FRIEND, username)
    def on_new_group(self):
        group_name = simpledialog.askstring(title="Create a group", prompt="Your new group's name:", parent=None)
        if group_name:
            result = simpledialog.askstring(title="Invite some friends?", prompt="Input usernames ,separated by \' \' blankspace:")
            if result:
                usernames = list(set(result.split()))
                client_global.session.send(GeneralMessage.CREATE_G,[group_name,[client_global.current_user['username']]+usernames])
            else:
                client_global.session.send(GeneralMessage.CREATE_G, [group_name,[client_global.current_user['username']]])   # TODO: 创建群的时候同时下拉框选择要加入的好友。
    def handle_message(self, msg_type, msg_data):
        if msg_type==GeneralMessage.INITIALIZE:
            # TODO: 接收好友、群列表，接收离线时收到的消息，把这些离线消息保存到聊天文件里面去。
            # 顺便将client_global里面存的未读消息更新，最后联系时间更新。
            # 最后刷新联系人列表
        if msg_type==GeneralMessage.STATUS_CREATE_G:
            if msg_data[0]:
                # 创建成功
                messagebox.showinfo(message="Sucessfully create new group!")
            else:
                messagebox.showerror(message=msg_data[1])
        elif msg_type==GeneralMessage.STATUS_ADD_FRIEND:
            if msg_data[0]:
                messagebox.showinfo(message="Great!You are now friends!")
                # TODO: 加入聊天列表一个新的元素，重新排列列表，使得有操作的联系人总在顶上
                # 生成该用户的聊天文件
            else:
                if msg_data[1]=='':
                    # 不需要在contactlist加一个item，只需要打开旧的聊天窗口
                    # TODO: 自动打开该用户的聊天窗口
                    messagebox.showinfo(message="You are already friends.")
                else:
                    messagebox.showerror(message=msg_data[1])
        elif msg_type==GeneralMessage.ADD_TO_G:
            group_name = msg_data[1]
            messagebox.showinfo(message="You are invited to group: %s" %group_name)
            # TODO: 加入聊天列表新元素，重新排序，并生成新的聊天记录文件。
            self.handle_new_friend(msg_data[0], msg_data[1])
        elif msg_type==GeneralMessage.NEW_FRIEND:
            username = msg_data[1] 
            messagebox.showinfo(message="User %s added you as friend." % username)
            # TODO: 加入聊天列表新的元素，重新排序，并生成新的聊天记录文件
            self.handle_new_group(msg_data[0], msg_data[1])

    def handle_new_friend(self, id, name):
        pass
    def handle_new_group(self, id, name):
        pass
    def refresh_list(self):
        pass
    def contact_item_clicked(self):
        #TODO: 生成新窗口并进行窗口的初始化，将点击的时间作为last_time， 刷新好友列表。
        pass


        


        
