from server.server_global import *
from common.message import GeneralMessage
from server import database

def run(session, parameters):
    """
    # ADD_FRINED : (str)username
    # STATUS_ADD_FRIEND: {'success':, 'error':, 'username':}
    如果bool为False， 而str是空字符串，打开旧的聊天窗口。
    """
    friend = parameters
    if friend != None:
        # 该用户存在，先看两人是不是已经是朋友
        if database.is_friend(session.username, friend):
            session.send(GeneralMessage.STATUS_ADD_FRIEND, {'success': False, 'username': friend}) #在旧的聊天窗口打开
        elif friend == session.username:
            session.send(GeneralMessage.STATUS_ADD_FRIEND, {'success': False, 'error': '不能与自己发起聊天', 'username': friend})
            return
        else:
            database.add_friend(session.username, friend)
            session.send(GeneralMessage.STATUS_ADD_FRIEND, {'success': True, 'username': friend})
            if friend in username_to_session:
                username_to_session[friend].send(GeneralMessage.NEW_FRIEND, {'username': session.username})
    else:
        session.send(GeneralMessage.STATUS_ADD_FRIEND, {'success': False, 'error': '用户名不存在', 'username': friend} )
    
    
