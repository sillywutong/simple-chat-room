import socket
import select
from common.config import get_config
from common.channel.Session import server_new_session
from server.server_global import *
import struct 
def run():
    config = get_config()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((config['server']['ip'], config['server']['port']))
    
    sock.listen(1)   #监听新的连接
    print('server listening on address %s port %s' %(config['server']['ip'], config['server']['port']))

    bytes_buffer = {}   #每一个会话接收包，但可能不是一次性接收到完整的包
    received = {}    #目前这个包收到了多少字节
    to_receive = {}   #是每一个会话接收到前4个字节length of message之后，接下来要接收直到整个包完成的大小
    while(1):
        rlist, wlist, xlist = select.select(list(map(lambda x: x.socket, sessions))+[sock], [],[])
        
        for s in rlist:
            if s == sock : # new connection
                new_sess = server_new_session(s)
                socket_to_sessions[new_sess.socket] = new_sess #从套接字快速找到会话通道; 自定义的通道类直接保存了socket
                sessions.append(new_sess)
                bytes_buffer[new_sess] = bytes()
                received[new_sess]=0
                to_receive[new_sess]=0
                continue
               
            sess = socket_to_sessions[s]    #旧的会话
            if received[sess] == 0 and to_receive[sess] == 0: #接收一个新的包
                try:
                    length_bytes = sess.socket.recv(4)
                except ConnectionError:
                    print("there are some problems with connection to the server, please check your network.")
                
                if len(length_bytes) == 4:
                    bytes_buffer[sess] = bytes()   # struct.unpack的返回结果为元组，即使只包含一个条目
                    # msg length + padding 1+ nonce 12 + tag 16 + msg
                    to_receive[sess] = struct.unpack('!L', length_bytes)[0] + 1 + 12 + 16
            
            #print("toreceive: %d" % to_receive[sess])
            #print("received : %d" % received[sess])
            bytes_buffer[sess] += sess.socket.recv(to_receive[sess] - received[sess]) 
            #print("length of buffer %d "  % len(bytes_buffer[sess]))
            received[sess] += len(bytes_buffer[sess])

            if received[sess] == to_receive[sess] and len(bytes_buffer[sess])!=0:
                print("receive a package")
                received[sess] = 0
                to_receive[sess] = 0
                data = sess.get_message(bytes_buffer[sess])
                bytes_buffer[sess] = bytes()





