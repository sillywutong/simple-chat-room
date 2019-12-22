import math
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES
import socket
from common.Crypto import crypt
from common.config import get_config
import hashlib
from common.utils import *
import struct
from common.message import GeneralMessage

class Session:
    def __init__(self, socket, session_key):
        self.socket = socket
        self.session_key = session_key
        self.username = None

    def send(self, msg_type, msg_body={}):
        """
            original app message packing to layer 1 and send.
            msg_body is a dict.
        """
        print("sending: ")
        print({'msg_type': msg_type, 'msg_body':msg_body})
        nonce = get_random_bytes(12)
        cipher = AES.new(key=self.session_key, nonce=nonce, mode=AES.MODE_GCM)
        data_to_encrypt = GeneralMessage.encode(msg_type, msg_body) # to do, will serialize body, add len(body), serialize msg_type, return bytes
        length = len(data_to_encrypt)
        padding = math.ceil(length / 16) * 16 - length
        for i in range(padding):
            data_to_encrypt += b'\0'

        encrypted_data, tag = cipher.encrypt_and_digest(data_to_encrypt) # MAC tag =16 bytes
        # length of message, padding, nounce, tag, message
        length_of_message = len(encrypted_data)
        print("length of message:")
        print(length_of_message)
        return self.socket.sendall(struct.pack('!L', length_of_message) + bytes([padding]) + nonce + tag + encrypted_data)
        # struct.pack 将length_of_message按前面的格式字符串打包成字节串，L表示long(4字节)，！表示大端

    def get_message(self, data):
        """
            recv a complete package of level 1, pass the whole passage as parameter `data` \
                and process it.
        """
        # length of message, padding, nounce, tag, message
        padding = struct.unpack('!B',data[0:1])[0]
        nonce = data[1:1+12]
        tag = data[1+12: 1+12+16]
        encrypted_msg = data[1+12+16:len(data)]
        data = bytes()
        '''
        buffer = Buffer(data)
        padding = buffer.read(1)[0]
        nonce = buffer.read(12)
        tag = buffer.read(16)
        encrypted_msg = buffer.read_all()
        '''

        cipher = AES.new(key=self.session_key, nonce=nonce, mode=AES.MODE_GCM)
        decrypted_msg = cipher.decrypt_and_verify(encrypted_msg, tag)

        if padding != 0:
            decrypted_msg = decrypted_msg[0: -padding]
        print("unpack message ")
        return GeneralMessage.decode(decrypted_msg)
    def close(self):
        self.socket.close()



    
    

def server_new_session(sock):
    print("call in")
    conn, addr = sock.accept()

    client_secret = conn.recv(1024)
    client_secret = int.from_bytes(client_secret, 'big')
    print("client secret: %d" % client_secret)
    conn.send(long_to_bytes(crypt.my_secret))
    print("my secret: %d" % crypt.my_secret)
    session_key = crypt.get_shared_secret(client_secret)
    print("shared key: %d" % int.from_bytes(session_key,'big'))
    session = Session(conn, session_key)
    return session