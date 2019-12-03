from common.channel.Session import client_new_session
import socket
import select
from client import client_global
import io

def run():
    try:
        client_global.session = client_new_session()
    except ConnectionError:
        print('Server has been closed.')
    with open('test.png',"rb") as image_file:
        image = image_file.read()
        img = bytes(image)
    #io = io.BytesIO(img)
    length = client_global.session.send(msg_type=1, msg_body={'nothing':0,'something':[1,2,3,'string!','中文',{'another dict': 12345, 'username':'rarecu'}],'image': img})
    print("length to send: %d" % length)
    client_global.session.send(msg_type=2, msg_body={})