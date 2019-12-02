from common.channel.Session import client_new_session
import socket
import select
from client import client_global


def run():
    try:
        client_global.session = client_new_session()
    except ConnectionError:
        print('Server has been closed.')
    client_global.session.send(msg_type=1, msg_body={'nothing':0})
    