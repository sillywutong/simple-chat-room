from common.message import GeneralMessage
from server.server_global import *
from server import database

def run(session, parameters):
    """ 邀请一个用户名进群
        收到数据格式： [group_id, username]
        查询该用户名是否存在，如果不存在，发送STATUS_INVITE{success: False, error: '用户名不存在'}
        否则发送{success: True, username:, group_id:,}
        被邀请的用户如果在线会受到 ADD_TO_G{source_username, group_id:, group_name: group_members: [username]}
        其他群友会受到 NEW_MEMBER{group_id:, source_username:, target_username:}
    """
    print('handling INVITE')
    group_id = parameters[0]
    uname = parameters[1]

    r = database.get_user_by_name(uname)
    if not r:
        session.send(GeneralMessage.STATUS_INVITE, {'success': False, 'error': '用户名不存在'})
    else:
        database.add_to_group(group_id, uname)
        session.send(GeneralMessage.STATUS_INVITE, {'success': True})
        members = database.get_group_members(group_id)
        if uname in username_to_session:
            gname = database.get_group_name(group_id)
            msg = {'source_username': session.username, 'group_id': group_id, 'group_name': gname, 'group_member': members}
            username_to_session[uname].send(GeneralMessage.ADD_TO_G, msg)
        for member in members:
            if member != session.username and member in username_to_session:
                msg = {'group_id': group_id, 'source_username': session.username, 'target_username': uname}
                username_to_session[member].send(GeneralMessage.NEW_MEMBER, msg)
            
            
