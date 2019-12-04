from common.message import GeneralMessage
from server.server_global import *
from server import database

def run(session, parameters):
    user_id = parameters
    session.user_id = None
    del user_id_to_session[user_id]
    



