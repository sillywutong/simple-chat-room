import socket
from common.Crypto import crypt
from common.config import get_config
from common.utils import *
import struct
from common.channel.Session import Session



def client_new_session():
    config = get_config()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((config['client']['ip'],config['client']['port']))

    s.send(long_to_bytes(crypt.my_secret))
    server_secret = s.recv(1024)
    server_secret = int.from_bytes(server_secret, 'big')
    session_key = crypt.get_shared_secret(server_secret)
    session = Session(s, session_key)
    print("new session...")
    return session