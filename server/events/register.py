from server import database
from common.message import GeneralMessage
from common.utils import md5

def run(session, parameters):
    """
    Args:
       parameters=[username, password]
    """
    username = parameters[0]
    password = parameters[1]
    c = database.get_cursor()
    r = c.execute('SELECT * FROM users WHERE username=?', [username]).fetchone()
    if r:
        # 用户名已存在
        session.send(GeneralMessage.REG_FAIL, 0)

    else:
        user_id = database.add_user(username, md5(password))
        session.send(GeneralMessage.REG_OK, [user_id, username])
        #注册成功之后还得登录才行
    
