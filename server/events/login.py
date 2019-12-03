from server.server_global import *
from common.utils import md5
from server import database
from common.message import GeneralMessage
def run(session, parameters):
    username = parameters['username']
    password = parameters['password']
    cur = database.get_cursur()
    rows = cur.execute('SELECT * FROM users WHERE username=?',(username)).fetchall()

    if len(rows) == 0:
        # 用户不存在
        session.send(GeneralMessage.LG_FAIL, {'error_code':0})
    else if rows[0][2]!=md5(password):
        # 密码错误
        session.send(GeneralMessage.LG_FAIL, {'error_code':1})
    else:
        #登录成功
        user_id = rows[0][0]
        session.send(GeneralMessage.LG_OK, {'user_id': user_id, 'username': username})

        if user_id in user_id_to_session:
            # 重复登录, 把旧的会话关掉，把旧的登录踢掉
            old_session = user_id_to_session[user_id]
            old_session.send(GeneralMessage.KICK, {})
            old_session.close()
            remove_session(old_session)

        #登录成功，将会话与这个用户id映射起来
        user_id_to_session[user_id] = session
        session.user_id = user_id
        session.send(GeneralMessage.LG_OK, {'user_id': user_id, 'username':username})

        initialize_data={}
        
            

    
