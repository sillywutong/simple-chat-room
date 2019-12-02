
sessions = []    # 存放目前的连接
socket_to_sessions = {}
session_to_user_id = {}   # 字典，socket为key， 值为user_id(这个id是数据库users的主键)
 
user_id_to_session = {} # 字典，key为user_id, 值为socket



