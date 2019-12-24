from datetime import datetime
from server.server_global import *
from common.utils import md5
from server import database
from common.message import GeneralMessage

def run(session, parameters):
    username = parameters[0]
    password = parameters[1]
    
    user = database.get_user_by_name(username)
    if user == None:
        # 用户不存在
        print("用户不存在，服务端发送：")
        session.send(GeneralMessage.LG_FAIL, 0)
    elif user['password'] != md5(password):
        # 密码错误
        session.send(GeneralMessage.LG_FAIL, 1)
    else:
        #登录成功
        if username in username_to_session:
            # 重复登录, 把旧的会话关掉，把旧的登录踢掉
            old_session = username_to_session[username]
            old_session.send(GeneralMessage.KICK, {})
            old_session.close()
            remove_session(old_session)

        #登录成功，将会话与这个用户id映射起来
        username_to_session[username] = session
        session.username = username
        session.send(GeneralMessage.LG_OK, {'username': username})

        initialize_data={}
        # 初始化好友列表
        friends=database.get_friend(username)
        initialize_data['friends']=friends

        # 初始化加入的群列表
        groups=database.get_group(username)
        initialize_data['groups']=groups

        # 发送离线消息
        msgs = database.get_offline_messages(username)
        for msg in msgs:
            msg['time'] = datetime.strptime(msg['time'], '%Y-%m-%d %H:%M:%S.%f')
        initialize_data['msgs']=msgs

        session.send(GeneralMessage.INITIALIZE, initialize_data)
        print('login done.')

            

    
