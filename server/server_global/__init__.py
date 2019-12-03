
sessions = []    # 存放目前的连接
socket_to_sessions = {}

 
user_id_to_session = {} # 字典，key为user_id, 值为socket



def remove_session(session):
    if session in sessions:
        sessions.remove(session)

    if session.user_id != None:
        uid = session.user_id
        session.user_id = None
        if uid in user_id_to_session:
            del user_id_to_session[uid]

    if session.socket in socket_to_sessions:
        del socket_to_sessions[session.socket]
