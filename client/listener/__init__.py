import threading
import socket
import select
import tkinter as tk
from tkinter import messagebox
from common.message import GeneralMessage
import struct
from client import client_global
from common.channel import Session

specific_listener=[]
chat_window_listener=[{},{}]   #[0]私聊，[1]群聊，'target_id'

def main_listener_thread(session, tk_root):
    bytes_buffer = bytes()  #每一个会话接收包，但可能不是一次性接收到完整的包
    received = 0    #目前这个包收到了多少字节
    to_receive = 0   #是每一个会话接收到前4个字节length of message之后，接下来要接收直到整个包完成的大小
    while(tk_root):
        rlist, wlist, xlist = select.select([session.socket], [session.socket],[])
        if len(rlist): 
            if received == 0 and to_receive == 0: #接收一个新的包
                connection = True
                length_bytes=b''
                try:
                    length_bytes = session.socket.recv(4, socket.MSG_WAITALL)
                except ConnectionError:
                    print("server has been shut down.")
                    child=[]
                    for key in tk_root.children:
                        child.append(tk_root.children[key])
                    for i in child:
                        i.destroy()
                    tk_root.destroy()
                    connection = False

                if length_bytes=='' or len(length_bytes)<4:
                    connection = False
                    messagebox.showerror(message="无法连接到服务器，服务器可能已经关闭。")
                    child=[]
                    for key in tk_root.children:
                        child.append(tk_root.children[key])
                    for i in child:
                        i.destroy()
                    tk_root.destroy()
                    
                if connection:
                    bytes_buffer = bytes()   
                    # msg length + padding 1+ nonce 12 + tag 16 + msg
                    to_receive = struct.unpack('!L', length_bytes)[0] + 1 + 12 + 16
            bytes_buffer += session.socket.recv(to_receive - received, socket.MSG_WAITALL) #直接等整个包被接受完才返回
            #print("length of buffer %d "  % len(bytes_buffer[sess]))
            received = len(bytes_buffer)   #但保险起见还是判断一下是不是真的收到整个包了

            if received == to_receive and len(bytes_buffer)!=0:
                print("receive a package")
                received = 0
                to_receive = 0
                data = session.get_message(bytes_buffer)
                if data['msg_type'] == GeneralMessage.KICK:
                    messagebox.showerror(message="您的账号在别处登录")
                    kick(tk_root)
                if data['msg_type'] == GeneralMessage.GENERAL_ERROR:
                    messagebox.showerror(message=data['msg_body'])
                if data['msg_type'] == GeneralMessage.PASS:
                    process_and_show_message(data['msg_body'])
                
                for listener in specific_listener:
                    listener(data['msg_type'], data['msg_body'])
                bytes_buffer = bytes()
def kick(tk_root):
    child=[]
    for key in tk_root.children:
        child.append(tk_root.children[key])
    for i in child:
        i.destroy()
    tk_root.destroy()



def add_listener(listener):
    specific_listener.append(listener)

def remove_listener(listener):
    print("listener removed.")
    if listener in specific_listener:
        specific_listener.remove(listener)

def add_chat_window(listener, target_type, target_id):
    chat_window_listener[target_type][target_id]=listener

def remove_chat_window(target_type, target_id):
    if target_id in chat_window_listener[target_type]:
        del chat_window_listener[target_type][target_id]

def process_and_show_message(data):
    """
        TODO: 
            - 找到该用户聊天记录文件夹，聊天记录文件夹分用户账号，每个账号下有曾经聊天过的用户的记录，记录可以采用.json
                或者.pkl保存
            - 如果没有该用户账号的文件夹，就mkdir。
            - 之后如果没有这个发送者账号的聊天记录，就生成一个新的文件
            - 将这条聊天记录放在文件末尾。


            - 更新当前记录联系人的最晚聊天时间
            - 更新当前记录联系人的未读消息（只有在线的时候，会保存这个未读消息数据结构，当窗口被打开时，显示所有未读消息，然后删掉这个保存）

            - 根据最晚聊天时间重新排序联系人
            - 如果有新消息，但是窗口没有打开，则列表中对应的联系人背景色可以变成另一种颜色。

            - 通知聊天窗口
            - 如果窗口已经打开，则将聊天记录解开，传给该窗口的处理函数，让窗口来做前端显示。
            

            - 
    """
    pass