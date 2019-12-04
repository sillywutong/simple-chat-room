from server.server_global import *
from common.message import GeneralMessage
from server import database

def run(session, parameters):
    '''
    # ADD_FRINED : (str)username
    # STATUS_ADD_FRIEND: [bool, str]
    如果bool为False， 而str是空字符串，打开旧的聊天窗口。
    '''
    friend_name = parameters
    c = database.get_cursor()
    friend = c.execute('SELECT id FROM users WHERE username=?', friend_name).fetchall()
    if len(friend) != 0:
        # 该用户存在，先看两人是不是已经是朋友
        if database.is_friend(session.user_id, friend[0][0]):
            session.send(GeneralMessage.STATUS_ADD_FRIEND, [False, '']) #在旧的聊天窗口打开
        else if friend[0][0] == session.user_id:
            session.send(GeneralMessage.STATUS_ADD_FRIEND, [False, '不能与自己发起聊天'])
        else:
            database.add_friend(session.user_id, friend[0][0])
            session.send(GeneralMessage.STATUS_ADD_FRIEND, [True, ''])
    else:
        session.send(GeneralMessage.STATUS_ADD_FRIEND, [False, '用户名不存在'] )
    
    c = database.get_cursor()
    uname = c.execute('SELECT username FROM users WHERE id=?', session.user_id)
    user_id_to_session[friend[0][0]].send(GeneralMessage.NEW_FRIEND, [session.user_id, uname])
