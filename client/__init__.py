from common.channel.Session import client_new_session
import socket
import select
from client import client_global
import io
from common.message import GeneralMessage

def run():
    try:
        client_global.session = client_new_session()
    except ConnectionError:
        print('Server has been closed.')
    with open('test.png',"rb") as image_file:
        image = image_file.read()
        img = bytes(image)
    #io = io.BytesIO(img)
    #length = client_global.session.send(msg_type=GeneralMessage.LOGIN, msg_body={'nothing':0,'something':[1,2,3,'string!','中文',{'another dict': 12345, 'username':'rarecu'}],'image': 123})
    #print("length to send: %d" % length)
    #client_global.session.send(msg_type=2, msg_body={})
    print("send login 1:")
    client_global.session.send(msg_type=GeneralMessage.LOGIN, msg_body=['rarecu', '1278ghdfsdf88'])
    print("send login 2:")
    client_global.session.send(msg_type=GeneralMessage.LOGIN, msg_body=['sdshdj', 'dshdjfhjsdhfj'])
    while 1:
        1+1