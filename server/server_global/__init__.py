
sessions = []    # 存放目前的连接
socket_to_sessions = {}

 
username_to_session = {} # 字典，key为username, 值为socket



def remove_session(session):
    if session in sessions:
        sessions.remove(session)

    if session.username != None:
        username = session.username
        session.username = None
        if username in username_to_session:
            del username_to_session[username]

    if session.socket in socket_to_sessions:
        del socket_to_sessions[session.socket]
