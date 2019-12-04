from common.message import GeneralMessage
from server.server_global import *
from server import database

def run(session, parameters):
    """ 邀请一个用户名进群
        收到数据格式： [group_id, username]
        查询该用户名是否存在，如果不存在，发送STATUS_CREATE_G[False, '用户名不存在']
        否则发送[True,'']
        被邀请的用户如果在线会受到 ADD_TO_G[group_id, group_name ]
    """
    group_id = parameters[0]
    uname = parameters[1]

    c = database.get_cursor()
    r = c.execute('SELECT id FROM users WHERE username=?', uname).fetchone()
    if len(r) == 0:
        session.send(GeneralMessage.STATUS_CREATE_G, [False, '用户名不存在'])
    else:
        database.add_to_group(group_id, r[0])
        session.send(GeneralMessage.STATUS_CREATE_G, [True, ''])
        if r[0] in user_id_to_session:
            c = database.get_cursor()
            group_name = c.execute('SELECT group_name FROM groups WHERE group_id=?', group_id).fetchall()
            user_id_to_session[r[0]].send(GeneralMessage.ADD_To_G, [group_id, group_name[0][0]])
            
