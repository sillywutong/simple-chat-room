import tkinter as tk
from tkinter import *

from tkinter.scrolledtext import ScrolledText
from tkinter import colorchooser
from tkinter import simpledialog
from tkinter import filedialog
from PIL import Image, ImageTk
from io import BytesIO
import binascii

from client.listener import add_listener
from client import client_global
from common.message import GeneralMessage


class ChatWindow(tk.Frame):
    font_color = "#000000"
    font_size = 10
    user_list = []
    tag_i = 0

    def __init__(self, contact, master=None):
        super().__init__(master)
        self.master = master
        self.contact = contact
        self.user_listbox = tk.Listbox(self, bg='#EEE')
        add_listener(self.handle_message)
        master.resizable(width=True, height=True)
        master.geometry('660x500')
        master.minsize(520, 370)
        # self.sc = client.memory.sc

        if self.contact['is_private']:
            self.master.title(self.contact['username'])
        else:
            self.master.title("Group:" + client_global.groups[self.contact['group_id']]['group_name'] + "#" + str(self.contact['group_id']))
            # self.sc.send(MessageType.query_room_users, self.contact['id'])

        self.right_frame = tk.Frame(self, bg='white')

        self.user_listbox.bind('<Double-Button-1>', self.user_listbox_double_click)
        if not self.contact['is_private']:
            self.user_listbox.pack(side=LEFT, expand=False, fill=BOTH)
            self.refresh_user_listbox()
        
        self.right_frame.pack(side=LEFT, expand=True, fill=BOTH)

        self.input_frame = tk.Frame(self.right_frame, bg='white')

        self.input_textbox = ScrolledText(self.right_frame, height=10)
        self.input_textbox.bind("<Control-Return>", self.send_message)
        # self.input_textbox.bind_all('<Key>', self.apply_font_change)

        self.send_btn = tk.Button(self.input_frame, text='发送消息(Ctrl+Enter)', command=self.send_message)
        self.send_btn.pack(side=RIGHT, expand=False)

        self.image_btn = tk.Button(self.input_frame, text='发送图片', command=self.send_image)
        self.image_btn.pack(side=LEFT, expand=False)

        self.chat_box = ScrolledText(self.right_frame, bg='white')
        self.input_frame.pack(side=BOTTOM, fill=X, expand=False)
        self.input_textbox.pack(side=BOTTOM, fill=X, expand=False, padx=(0, 0), pady=(0, 0))
        self.chat_box.pack(side=BOTTOM, fill=BOTH, expand=True)
        self.chat_box.bind("<Key>", lambda e: "break")
        self.chat_box.tag_config("default", lmargin1=10, lmargin2=10, rmargin=10)
        self.chat_box.tag_config("me", foreground="green", spacing1='5')
        self.chat_box.tag_config("them", foreground="blue", spacing1='5')
        self.chat_box.tag_config("message", foreground="black", spacing1='0')
        self.chat_box.tag_config("system", foreground="grey", spacing1='0',
                                 justify='center',
                                 font=(None, 8))

        self.pack(expand=True, fill=BOTH)

        msgs = client_global.contacts_private.get(self.contact['username'], []) \
            if self.contact['is_private'] \
            else client_global.contacts_group.get(self.contact['group_id'], [])
        for msg in msgs:
            self.digest_message(msg)

    def handle_message(self, msg_type, msg_data):
        if msg_type == GeneralMessage.PASS:
            if self.contact['is_private'] and msg_data['is_private']:
                source = msg_data['source_username']
                target = msg_data['target_username']
                if set([self.contact['username'], client_global.current_user]) == set([source, target]):
                    # 私信，双方的username和当前窗口匹配
                    self.digest_message(msg_data)
            if not self.contact['is_private'] and not msg_data['is_private'] \
                and self.contact['group_id'] == msg_data['group_id']:
                # 群聊，group_id和当前窗口匹配
                self.digest_message(msg_data)
        if msg_type == GeneralMessage.NEW_MEMBER:
            if self.contact['group_id'] == msg_data['group_id']:
                if msg_data['source_username'] == client_global.current_user:
                    self.append_to_chat_box('you invited ' + msg_data['target_username'], 'system')
                else:
                    self.append_to_chat_box(msg_data['source_username'] + ' invited ' + msg_data['target_username'], 'system')

    def refresh_user_listbox(self):
        # [id, nickname, online, username]
        self.user_listbox.delete(0, END)
        self.user_list = list(client_global.groups[self.contact['group_id']]['group_members'])
        self.user_list.sort(reverse=True)
        for uname in self.user_list:
            self.user_listbox.insert(0, uname)
            self.user_listbox.itemconfig(0, {'fg': ("green")})

    def digest_message(self, data):
        time = data['time'].ctime()
        if data.get('source_username', None):
            self.append_to_chat_box(
                data['source_username'] + "  " + time + '\n',
                ('me' if client_global.current_user == data['source_username'] else 'them'))
            # type 0 - 文字消息 1 - 图片消息
            if data['type'] == 0:
                self.tag_i += 1
                self.chat_box.tag_config(
                    'new' + str(self.tag_i),
                    lmargin1=16,
                    lmargin2=16   
                )
                self.append_to_chat_box(data['data'] + '\n',
                                        'new' + str(self.tag_i))
        else:
            # no source_username, system
            self.append_to_chat_box(data['data'] + '\n', ('system'))
        
        if data['type'] == 1:
            client_global.tk_img_ref.append(ImageTk.PhotoImage(data=data['data']))
            self.chat_box.image_create(END, image=client_global.tk_img_ref[-1], padx=16, pady=5)
            self.append_to_chat_box('\n', '')

    def user_listbox_double_click(self, _):
        if len(self.user_listbox.curselection()) == 0:
            return None
        index = self.user_listbox.curselection()[0]
        selected_user = self.user_list[-index-1]
        if selected_user == client_global.current_user:
            return
        form = Toplevel(client_global.tkroot, takefocus=True)
        ChatWindow({'is_private': True, 'username': selected_user}, form)
        # pprint(selected_user_id)
        return

    def append_to_chat_box(self, message, tags):
        self.chat_box.insert(tk.END, message, [tags, 'default'])
        self.chat_box.update()
        self.chat_box.see(tk.END)

    def send_message(self, _=None):
        text = self.input_textbox.get("1.0", END)
        if not text or text.replace(" ", "").replace("\r", "").replace("\n", "") == '':
            return
        msg = {
            'is_private': self.contact['is_private'],
            'type': 0,
            'data': text
        }
        if msg['is_private']:
            msg['target_username'] = self.contact['username']
        else:
            msg['group_id'] = self.contact['group_id']
        client_global.session.send(GeneralMessage.SEND, msg)
        self.input_textbox.delete("1.0", END)

    def send_image(self):
        filename = filedialog.askopenfilename(filetypes=[("Image Files",
                                                          ["*.jpg", "*.jpeg", "*.png", "*.gif", "*.JPG", "*.JPEG",
                                                           "*.PNG", "*.GIF"]),
                                                         ("All Files", ["*.*"])])
        if filename is None or filename == '':
            return
        with open(filename, "rb") as imageFile:
            f = imageFile.read()
        b = bytes(f)
        msg = {
            'type': 1, 
            'data': b,
            'is_private': self.contact['is_private'],
        }
        if self.contact['is_private']:
            msg['target_username'] = self.contact['username']
        else:
            msg['group_id'] = self.contact['group_id']
        client_global.session.send(GeneralMessage.SEND, msg)
