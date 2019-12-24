from server.server_global import *
from common.message import GeneralMessage
from server import database

def run(session, parameters):
    """ 开启新群聊
        收到消息的格式是[group_name, [username, username, username...]]
        创建者会受到STATUS_CREATE_G，{success, error, group_id, group_name, members}
        列表中的所有用户会收到ADD_TO_GROUP消息，被加入群聊，格式是{source_username: group_id:, group_name:, group_members: }
    """
    #print('handling NEWGROUP')
    group_name = parameters[0]
    members = parameters[1]

    for mname in members:
        user = database.get_user_by_name(mname)
        if not user:
            # 用户名不存在
            session.send(GeneralMessage.STATUS_CREATE_G, {'success': False,'error': '用户名 %s 不存在'%mname})
            return
    
    group_id = database.new_group(group_name, list(set(members)))
    if group_id:
        msg = {'success': True, 'group_id': group_id, 'group_name': group_name, 'group_members': members}
        session.send(GeneralMessage.STATUS_CREATE_G, msg)
        
        msg = {'source_username': session.username, 'group_id': group_id, 'group_name': group_name, 'group_members': members}
        for member in members:
            if member != session.username and member in username_to_session:
                username_to_session[member].send(GeneralMessage.ADD_TO_G, msg)
            
        
        

    
