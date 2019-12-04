from server.server_global import *
from common.utils import md5
from server import database
from common.message import GeneralMessage
def run(session, parameters):
    print(" user login.")
    username = parameters[0]
    password = parameters[1]
    cur = database.get_cursor()
    rows = cur.execute('SELECT * FROM users WHERE username=?',[username]).fetchall()

    if len(rows) == 0:
        # 用户不存在
        print("用户不存在，服务端发送：")
        session.send(GeneralMessage.LG_FAIL, 0)
    elif rows[0][2]!=md5(password):
        # 密码错误
        session.send(GeneralMessage.LG_FAIL, 1)
    else:
        #登录成功
        user_id = rows[0][0]

        if user_id in user_id_to_session:
            # 重复登录, 把旧的会话关掉，把旧的登录踢掉
            old_session = user_id_to_session[user_id]
            old_session.send(GeneralMessage.KICK, {})
            old_session.close()
            remove_session(old_session)

        #登录成功，将会话与这个用户id映射起来
        user_id_to_session[user_id] = session
        session.user_id = user_id
        session.send(GeneralMessage.LG_OK, [user_id, username])

        initialize_data={}
        # 初始化好友列表
        friends=database.get_friend(user_id)
        initialize_data['friends']=friends

        # 初始化加入的群列表
        groups=database.get_group(user_id)
        initialize_data['groups']=groups

        # 发送离线消息
        msg = database.get_offline_messages(user_id)
        initialize_data['msg']=msg

        session.send(GeneralMessage.INITIALIZE, initialize_data)


            

    
