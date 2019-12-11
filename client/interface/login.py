import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from client import client_global
from common.message import GeneralMessage
from client.interface.register import RegisterForm
from client.listener import add_listener, remove_listener
from client.interface.contactlist import ContactList
class LoginWindow(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        #self.parent.configure(bg='#e3e3dc')
        self.parent.resizable(width=False, height=False)

        self.configure(bg=self.parent.cget('bg'))
        #self.configure(bg="#000000")
        self.usernamelabel = tk.Label(master=self, text="Username:", bg=self.cget('bg'))
        self.passwordlabel = tk.Label(master=self, text="Password:", bg=self.cget('bg'))

        self.username = tk.Entry(self)
        self.password = tk.Entry(self, show="*")

        buttonFrame = tk.Frame(self)
        buttonFrame.configure(bg=self.cget('bg'))

        btnstyle = ttk.Style()
        btnstyle.map("C.TButton", foreground=[('pressed', '#536580'), ('active', '#000000')],background=[('pressed', '!disabled', '#F2F8FF'), ('active', '#C2C6CC')])
        
        self.loginbtn = ttk.Button(master=buttonFrame, text="Log in", command=self.login_clicked, style="C.TButton")
        self.registerbtn = ttk.Button(master=buttonFrame, text="Cancel", command=self.master.cancel_login, style="C.TButton")

        self.username.grid(row=0, column=1, pady=15)
        self.usernamelabel.grid(row=0, padx=6, sticky=tk.W)    
        self.password.grid(row=1, column=1, pady=15)
        self.passwordlabel.grid(row=1, padx=6, sticky=tk.W)

        buttonFrame.grid(row=3, rowspan=2, columnspan=2, pady=15)
        self.loginbtn.grid(row=0, column=0, padx=10)
        self.registerbtn.grid(row=0, column=1, padx=10)
        self.pack(anchor=tk.CENTER, padx=30, pady=30, expand=True)

        add_listener(self.handle_response)
        print("listener added")
    def login_clicked(self):
        username = self.username.get()
        password = self.password.get()
        if len(username)==0:
            tk.messagebox.showinfo(message="用户名不能为空")
        elif len(password)==0:
            tk.messagebox.showinfo(message="请输入密码")
        else:
            client_global.session.send(GeneralMessage.LOGIN, [username, password])

    def handle_response(self, msg_type, msg_body):
        print("handle_response_called")
        if msg_type == GeneralMessage.LG_FAIL:
            error_code = msg_body
            if error_code == 0:
                tk.messagebox.showerror(message="Username does not exist.")
            else:
                tk.messagebox.showerror(message="Incorrect password, please check your input.")
        elif msg_type == GeneralMessage.LG_OK:
            user_id = msg_body[0]
            username = msg_body[1]
            client_global.current_user['id'] = user_id
            client_global.current_user['username'] = username
            print("current id: %d" %user_id)
            # TODO: open the main window.
            # close the login window.
            # never want to receive message from server.
            print("close login window and remove listener")
            remove_listener(self.handle_response)
            self.master.destroy()
            contactwnd = tk.Toplevel(client_global.tkroot, takefocus=True)
            ContactList(contactwnd)

    def cancel_clicked(self):
        '''
        register_window = tk.Toplevel(master=self, takefocus=True)
        RegisterForm(register_window)
        '''
        


