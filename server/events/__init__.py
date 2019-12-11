from server.events import login
from server.events import add_friend
from server.events import invite_to_group
from server.events import new_group
from server.events import query_member
from server.events import register
from server.events import send_message
from server.events import logout
from common.message import GeneralMessage

TYPE_TO_EVENT_FUNCTION={
    GeneralMessage.LOGIN: login,
    GeneralMessage.ADD_FRIEND: add_friend,
    GeneralMessage.INVITE: invite_to_group,
    GeneralMessage.CREATE_G: new_group,
    GeneralMessage.REGISTER: register,
    GeneralMessage.SEND: send_message,
    GeneralMessage.QUERY_MEMBER: query_member,
    GeneralMessage.LOGOUT: logout
}
def handle_event(session, msg_type, msg_body):
    print("handling events...")
    TYPE_TO_EVENT_FUNCTION[msg_type].run(session, msg_body)