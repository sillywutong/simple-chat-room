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
    r = database.get_user_by_name(username)
    if r:
        # 用户名已存在
        session.send(GeneralMessage.REG_FAIL, 0)

    else:
        database.add_user(username, md5(password))
        session.send(GeneralMessage.REG_OK, {})
        #注册成功之后还得登录才行
