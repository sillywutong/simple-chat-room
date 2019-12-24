from common.message import GeneralMessage
from server.server_global import *
from server import database

def run(session, parameters):
    # username = parameters
    del username_to_session[session.username]
    session.username = None