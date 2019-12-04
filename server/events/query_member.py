from server import database
from server.server_global import *
from common.message import GeneralMessage

def run(session, parameters):
    """ 收到查询群成员的数据包
        格式为 group_id,
        返回 [group_id, [username, username....]]
    """
    group_id = parameters
    
    members = database.get_group_members_info(group_id)
    mname = members[:, 1]

    session.send(GeneralMessage.G_MEMBER, [group_id, mname])