from server.server_global import *
from common.message import GeneralMessage
from server import database

def run(session, parameters):
    """ 开启新群聊
        收到消息的格式是[group_name, [username, username, username...]]
        列表中的所有用户会收到ADD_TO_GROUP消息，被加入群聊，格式是[group_id, group_name]
    """
    group_name = parameters[0]
    members = parameters[1]

    mid = []
    for mname in members:
        c = database.get_cursor()
        r = c.execute('SELECT id FROM users WHERE username=?', [mname]).fetchone()
        if not r:
            # 用户名不存在
            session.send(GeneralMessage.STATUS_CREATE_G, [False,'用户名 %s 不存在'%mname])
            return
        else:
            mid.append(r[0])
    

    group_id = database.new_group(group_name, mid)
    if group_id:
        session.send(GeneralMessage.STATUS_CREATE_G, [True, ''])
        for id in mid:
            if id in user_id_to_session:
                # 在线
                user_id_to_session[id].send(GeneralMessage.ADD_TO_G, [group_id, group_name])
        
        

    
