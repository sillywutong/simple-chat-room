from client.client_global import contacts_private
import tkinter as tk
from tkinter import ttk
from common.message import GeneralMessage
from client import client_global
from tkinter import simpledialog
from tkinter import messagebox
from client.listener import add_listener
from tkinter import *
from datetime import datetime
from client.interface.chat_window import ChatWindow
from client.interface.group_creater import GroupCreater
from client.interface.vertical_scrolled_frame import VerticalScrolledFrame
from client.interface.chatform import ChatForm

class ContactItem(Frame):
    def __init__(self, parent, onclick):
        tk.Frame.__init__(self, parent)

        def handle_on_click(e):
            e.widget = self
            onclick(e)

        tk.Frame.config(self, background='white', borderwidth=2, relief=GROOVE)
        # == Line 1

        self.title_frame = Frame(self, bg='white')
        self.title_frame.pack(side=TOP, fill=X, expand=True, anchor=W, pady=(1, 1), padx=3)

        self.title = Label(self.title_frame, text="Title", bg='white')
        self.title.pack(side=LEFT, fill=None, anchor=W)

        self.last_message_time = Label(self.title_frame, text="date", font=('', 8), fg='#999', bg='white')
        self.last_message_time.pack(side=RIGHT, anchor=E)

        # == Line 2

        self.message_frame = Frame(self, bg='white')
        self.message_frame.pack(side=TOP, fill=X, expand=True, anchor=W, pady=(0, 5), padx=3)

        self.unread_message_count = Label(self.message_frame, text="0", font=('', 9), fg='white', bg='red')
        self.unread_message_count.pack(side=RIGHT, anchor=E, fill=None, expand=False, ipadx=4)
        self.unread_message_count.pack_forget()

        self.last_message = Label(self.message_frame, text="recent message", font=('', 9), fg='#666', bg='white')
        self.last_message.pack(side=LEFT, fill=X, expand=True, anchor=W)

        # propagate click event to parent..
        self.title.bind("<Button>", handle_on_click)
        self.last_message_time.bind("<Button>", handle_on_click)
        self.last_message.bind("<Button>", handle_on_click)
        self.unread_message_count.bind("<Button>", handle_on_click)
        self.message_frame.bind("<Button>", handle_on_click)
        self.title_frame.bind("<Button>", handle_on_click)

        self.pack()
        return

class ContactList(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.parent.resizable(width=False, height=False)
        self.parent.geometry('500x600')
        self.configure(bg='#ffffff')

        self.scroll = VerticalScrolledFrame(self)
        self.scroll.pack(side=RIGHT, fill="both", expand="yes")
        
        top_color='#525D66'
        header = tk.Frame(self)
        header.configure(bg=top_color)
        header.pack(anchor=tk.N, side='top', fill='x', ipadx=20)

        self.topUserInfo = tk.Label(master=header, text='Hello!  '+client_global.current_user)
        self.topUserInfo.configure(bg=top_color,font=('Microsoft Yahei UI',"12"))
        self.topUserInfo.pack(anchor=tk.W, padx=10,pady=(15, 15))

        btnbkg='#525D66'
        btnframe=tk.Frame(self)
        btnframe.configure(bg=btnbkg)

        btnframe.pack(anchor=tk.N, side='top', fill='x',ipadx=0, ipady=0)

        buttons = Frame(btnframe)
        buttons.pack(side=BOTTOM, fill='x')
        self.add_friend = ttk.Button(buttons, text="New Friend", command=self.on_new_friend)
        self.new_group = ttk.Button(buttons, text="Create Group", command=self.on_new_group)
        self.add_friend.pack(side=LEFT, fill='x', expand=True)
        self.new_group.pack(side=RIGHT, fill='x', expand=True)
        #self.join_group = ttk.Button(btnframe, text="   Invite    ", command=self.on_join_group)
        
        #self.join_group.grid(row=0,column=2)
        self.friend_list = []
        self.group_list = []

        self.friend_listbox = tk.Listbox(self, bg='#EEE')
        self.friend_listbox.bind('<Double-Button-1>', self.friend_listbox_double_click)
        self.friend_listbox.pack(side=LEFT, expand=False, fill=BOTH)

        self.group_listbox = tk.Listbox(self, bg='#EEE')
        self.group_listbox.bind('<Double-Button-1>', self.group_listbox_double_click)
        self.group_listbox.pack(side=LEFT, expand=False, fill=BOTH)
        
        self.pack(fill="both",expand="yes")
        
        self.contacts = []
        self.pack_objs = []

        add_listener(self.handle_message)

    def on_new_friend(self):
        username = simpledialog.askstring(title="Add new friend", prompt="Please input a username", parent=None)
        if username:
            client_global.session.send(GeneralMessage.ADD_FRIEND, username)

    def on_new_group(self):
        group_name = simpledialog.askstring(title="Create a group", prompt="Your new group's name:", parent=None)
        if group_name:
            GroupCreater(ChatForm(client_global.tkroot, takefocus=True), group_name)

    def handle_message(self, msg_type, msg_data):
        if msg_type==GeneralMessage.INITIALIZE:
            # TODO: 接收好友、群列表，接收离线时收到的消息，把这些离线消息保存到聊天文件里面去。
            client_global.friends = set(msg_data['friends'])
            self.refresh_friend_listbox()
            gs = msg_data['groups']
            client_global.groups = {
                g['group_id']: {
                    'group_name': g['group_name'], 
                    'group_members': g['group_members'] 
                } for g in gs 
            }
            self.refresh_group_listbox()
            msgs = msg_data['msgs']
            for msg in msgs:
                if msg['is_private']:
                    uname = msg['target_username'] \
                        if msg['source_username'] == client_global.current_user \
                        else msg['source_username']
                    del msg['is_private'], msg['target_username']
                    if uname in client_global.contacts_private:
                        client_global.contacts_private[uname].append(msg)
                    else:
                        client_global.contacts_private[uname] = [msg]
                else:
                    gid = msg['group_id']
                    del msg['is_private'], msg['group_id']
                    if gid in client_global.contacts_group:
                        client_global.contacts_group[gid].append(msg)
                    else:
                        client_global.contacts_group[gid] = [msg]
            for l in client_global.contacts_private.values():
                l.sort(key=lambda x: x['time'])
            for l in client_global.contacts_group.values():
                l.sort(key=lambda x: x['time'])
            self.contacts += [{
                'is_private': True,
                'username': k,
                'time': v[-1]['time'],
                'message': v[-1]['data'] if v[-1]['type'] == 0 \
                    else '%s sent an image' % v[-1]['source_username']
            } for k, v in client_global.contacts_private.items()]
            self.contacts += [{
                'is_private': False,
                'group_id': k,
                'time': v[-1]['time'],
                'message': v[-1]['data'] if v[-1]['type'] == 0 \
                    else '%s sent an image' % v[-1]['source_username']
            } for k, v in client_global.contacts_group.items()]
            self.refresh_contacts()

        if msg_type==GeneralMessage.STATUS_CREATE_G:
            if msg_data['success']:
                # 创建成功
                messagebox.showinfo(message="Sucessfully create new group!")
                client_global.groups[msg_data['group_id']] = {
                    'group_name': msg_data['group_name'],
                    'group_members': set(msg_data['group_members'])
                }
                client_global.contacts_group[msg_data['group_id']] = [{
                    'type': 0,
                    'data': '(you created a new group)',
                    'time': datetime.now()
                }]
                self.refresh_contacts()
                self.refresh_group_listbox()                                        
            else:
                messagebox.showerror(message=msg_data.get('error', None))
        elif msg_type==GeneralMessage.STATUS_ADD_FRIEND:
            if msg_data['success']:
                client_global.friends.add(msg_data['username'])
                messagebox.showinfo(message="Great!You are now friends!")
                client_global.contacts_private[msg_data['username']] = [{
                    'type': 0,
                    'data': '(new friend)',
                    'time': datetime.now()
                }]
                self.refresh_contacts()
                self.refresh_friend_listbox()
                # todo: 生成该用户的聊天文件
            else:
                if not msg_data.get('error', None):
                    # 不需要在contactlist加一个item，只需要打开旧的聊天窗口
                    # TODO: 自动打开该用户的聊天窗口
                    messagebox.showinfo(message="You are already friends.")
                else:
                    messagebox.showerror(message=msg_data['error'])
        elif msg_type==GeneralMessage.ADD_TO_G:
            group_name = msg_data['group_name']
            group_id = msg_data['group_id']
            messagebox.showinfo(message="You are invited to group: %s" %group_name + '#' + str(group_id))
            client_global.groups[group_id] = {
                'group_name': group_name,
                'group_members': set(msg_data['group_members'])
            }
            client_global.contacts_group[group_id] = [{
                'data': '(%s invited you into a group)' % msg_data['source_username'],
                'type': 0,
                'time': datetime.now()
            }]
            self.refresh_contacts()      
            self.refresh_group_listbox()
        elif msg_type==GeneralMessage.NEW_FRIEND:
            username = msg_data['username']
            messagebox.showinfo(message="User %s added you as friend." % username)
            client_global.friends.add(username)
            client_global.contacts_private[username] = [{
                'type': 0,
                'data': '(new friend)',
                'time': datetime.now()
            }]
            self.refresh_contacts()     
            self.refresh_friend_listbox()      
        elif msg_type == GeneralMessage.PASS:
            msg = msg_data.copy()
            if msg['is_private']:
                uname = msg['source_username'] \
                    if msg['target_username'] == client_global.current_user \
                    else msg['target_username']
                del msg['target_username'], msg['is_private']
                if uname not in client_global.contacts_private:
                    client_global.contacts_private[uname] = []
                if len(client_global.contacts_private[uname]) == 0 or client_global.contacts_private[uname][-1] != msg:
                    client_global.contacts_private[uname].append(msg)
            else:
                gid = msg['group_id']
                del msg['group_id'], msg['is_private']
                if gid not in client_global.contacts_group:
                    client_global.contacts_group[gid] = []
                if len(client_global.contacts_group[gid]) == 0 or client_global.contacts_group[gid][-1] != msg:
                    client_global.contacts_group[gid].append(msg)
            self.refresh_contacts()

    def handle_new_friend(self, id, name):
        pass

    def handle_new_group(self, id, name):
        pass

    def refresh_contacts(self):
        for pack_obj in self.pack_objs:
            pack_obj.pack_forget()
            pack_obj.destroy()

        self.pack_objs = []

        self.contacts = []
        for uname, msgs in client_global.contacts_private.items():
            if len(msgs) > 0:
                self.contacts.append({
                    'is_private': True,
                    'username': uname,
                    'time': msgs[-1]['time'],
                    'msg': 'an image' if msgs[-1]['type'] == 1 else msgs[-1]['data']
               })
        for gid, msgs in client_global.contacts_group.items():
            if len(msgs) > 0:
                self.contacts.append({
                    'is_private': False,
                    'group_id': gid,
                    'time': msgs[-1]['time'],
                    'msg': 'an image' if msgs[-1]['type'] == 1 else msgs[-1]['data']
                })
        # sorted(self.contacts, cmp=compare)
        # self.contacts.sort(key=lambda x: -client.memory.last_message_timestamp[x['type']].get(x['id'], 0))
        self.contacts.sort(key=lambda x: x['time'], reverse=True)
        for item in self.contacts:
            contact = ContactItem(self.scroll.interior, self.on_frame_click)
            contact.pack(fill=BOTH, expand=True)
            contact.item = item

            contact.bind("<Button>", None)
            if (item['is_private']):
                # 联系人
                contact.title.config(text=item['username'])
                contact.title.config(fg='green')
            else:
                # 群
                contact.title.config(
                    text=client_global.groups[item['group_id']]['group_name'] + '#' + str(item['group_id'])
                )
                contact.title.config(fg='blue')

            # contact.last_message.config(text=item['nickname'] + (' (在线)' if item['online'] else ' (离线)'))

            self.pack_objs.append(contact)

            time_message = item['time'].ctime()
            contact.last_message_time.config(text=time_message)
            
            if item.get('msg', None):
                contact.last_message.config(text=item['msg'])

    def contact_item_clicked(self):
        #TODO: 生成新窗口并进行窗口的初始化，将点击的时间作为last_time， 刷新好友列表。
        pass
    def on_frame_click(self, e):      
        form = ChatForm(client_global.tkroot, takefocus=True)
        contact = {'is_private': True, 'username': e.widget.item['username']} \
            if e.widget.item['is_private'] \
            else {'is_private': False, 'group_id': e.widget.item['group_id']}
        ChatWindow(contact, form)

    def refresh_friend_listbox(self):
        # [id, nickname, online, username]
        self.friend_listbox.delete(0, END)
        self.friend_list = list(client_global.friends)
        self.friend_list.sort(reverse=True)
        for uname in self.friend_list:
            self.friend_listbox.insert(0, uname)
            self.friend_listbox.itemconfig(0, {'fg': ("green")})

    def friend_listbox_double_click(self, _):
        if len(self.friend_listbox.curselection()) == 0:
            return None
        index = self.friend_listbox.curselection()[0]
        selected_user = self.friend_list[-index-1]
        if selected_user == client_global.current_user:
            return
        form = ChatForm(client_global.tkroot, takefocus=True)
        ChatWindow({'is_private': True, 'username': selected_user}, form)
        # pprint(selected_user_id)
        return
        
    def refresh_group_listbox(self):
        # [id, nickname, online, username]
        self.group_listbox.delete(0, END)
        self.group_list = list(client_global.groups.keys())
        self.group_list.sort(key=lambda x: client_global.groups[x]['group_name'] + '#' + str(x), reverse=True)
        for gid in self.group_list:
            self.group_listbox.insert(0, client_global.groups[gid]['group_name'] + '#' + str(gid))
            self.group_listbox.itemconfig(0, {'fg': ("blue")})

    def group_listbox_double_click(self, _):
        if len(self.group_listbox.curselection()) == 0:
            return None
        index = self.group_listbox.curselection()[0]
        gid = self.group_list[-index-1]
        form = ChatForm(client_global.tkroot, takefocus=True)
        ChatWindow({'is_private': False, 'group_id': gid}, form)
        # pprint(selected_user_id)
        return


        
