from common.message import GeneralMessage
from server import database
from server.server_global import *
import time
from common.channel import Session
def run(session, parameters):
    """服务器转发聊天消息

       服务器接收到的消息格式是 ：GeneralMessage.SEND,  {type, target_id,  msg:{type, data}}
       转发消息格式是： GeneralMessage.PASS, {type, time, from_id, from_name, target_id, msg:{type, data}} 
       检查用户是否在线, 对发送方和接收方，都发送PASS消息（target id，target name不一样）
       如果不在线，把消息放进数据库，数据库history格式是:
            type, target_id, source_id, msg. （msg的格式： {type, time, from_id, from_name, target_id, msg:{type, data}}
            编码成字节, 对于群聊，target_id是用户的id，source_id是群的id， PASS消息里面，from_id,from_name是发送消息的用户id， target_id是群的id
            对于私聊， PASS消息里面，from_id，from_name是发送方id，target_id是接收方用户id。
    """
    user_id = session.user_id
    c = database.get_cursor()
    username = c.execute('SELECT username FROM users WHERE id=?', user_id).fetchone()[0]
    message = {'type': parameters['type'], 
                'time':int(time.time()),
                'from_id': user_id,
                'from_name': username,
                'msg': parameters['msg']}
    
    if parameters['type'] == 0:
        #私聊
        message['target_id'] = user_id
        session.send(GeneralMessage.PASS, message)

        target_id = parameters['target_id']
        message['target_id'] = target_id
        if target_id in user_id_to_session:
            user_id_to_session[target_id].send(GeneralMessage.PASS, message)
        else:
            database.add_chat_history(parameters['type'],user_id, target_id, message)
    else:
        #群聊
        
        session.send(GeneralMessage.PASS, message)
        
        group_id = parameters['target_id']
        members = database.get_group_members_id(group_id)
        for mid in members:
            if mid in user_id_to_session:
                user_id_to_session[mid].send(GeneralMessage.PASS, message)
            else:
                database.add_chat_history(parameters['type'], group_id, mid, message)
                
