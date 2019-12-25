from common.message import GeneralMessage
from server import database
from server.server_global import *
from datetime import datetime
from common.channel import Session
def run(session, parameters):
    """服务器转发聊天消息

       服务器接收到的消息格式是 ：GeneralMessage.SEND,  {is_private, (target_username / group_id),  type, data}
       转发消息格式是： GeneralMessage.PASS, {is_private, time, source_username, target_username, type, data} 
       检查用户是否在线, 对发送方和接收方，都发送PASS消息
       如果不在线，把消息放进数据库，数据库history格式是:
    """
    username = session.username
    msg = parameters
    msg['time'] = datetime.now()
    msg['source_username'] = username
    
    if parameters['is_private'] == True:
        #私聊
        session.send(GeneralMessage.PASS, msg)
        if msg['target_username'] in username_to_session:
            username_to_session[msg['target_username']].send(GeneralMessage.PASS, msg)
        else:
            database.add_chat_history(**msg)
    else:
        #群聊
        # session.send(GeneralMessage.PASS, msg) 跟其他member一起发
        group_id = parameters['group_id']
        members = database.get_group_members(group_id)
        database.add_chat_history(**msg)
        for member in members:
            if member in username_to_session:
                username_to_session[member].send(GeneralMessage.PASS, msg)
#            else:
#               database.add_chat_history(**msg)
                
