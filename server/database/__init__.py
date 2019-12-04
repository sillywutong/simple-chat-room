'''
查询数据库
'''
import sqlite3

conn = sqlite3.connect('../database.db', isolation_level=None)  #每一次修改数据库都是立即写入，速度慢，但是保证不出现并发错误；想加快速度可以用#BEGIN TRANSACTION COMMIT

def get_cursor():
    return conn.cursor()

def get_user_by_id(user_id):
    '''
        根据给出的user id， 从数据库中查询user， 返回一个字典类型，包含字段：
        user_id: id,
        username: username,
        password: password,
    '''
    return {}
def get_user_by_name(username):
    '''
        返回：
        {
            user_id:
            username
        }
    '''
    return {}

def get_friend(user_id):
    '''
        根据给出的user id, 查询所有好友, 返回好友user id, username, 是个列表[{user_id, user_name},{user_id, user_name},...]
    '''
    return 0

def is_friend(user_id1, user_id2):
    '''
        判断user_id2 是不是user_id1的好友
    '''
    return False
def get_group(user_id):
    '''
    查询用户加入了哪些群，返回[{group_id, group_name},{group_id, group_name},...]
    '''
def get_group_name(group_id):
    '''
     返回字符串
    '''
    return ''

def get_group_members_id(group_id):
    '''
        根据群组id，获取群内用户的id，返回id的list
    '''
    return []
def get_group_members_info(group_id):
    '''
        根据群组id，获取群内所有用户的信息，返回字典数组{user_id, username}
    '''
    return [{}]

def get_offline_messages(user_id):
    '''
        用户上线的时候，查询数据库里面所有type=0(私聊），target_id=user_id的消息，和所有
        type=1，target_id=group_id where user_id in get_group_members_id的消息，返回所有的元组,
        格式为：
        [{
            type:,
            time:,
            from_id,
            from_name,
            target_id,
            target_name, #没必要？
            message:{type, data}

        }]
    '''
    return {}

def add_friend(from_id, to_id):
    return

def add_to_group(group_id, user_id):
    return
def is_in_group(group_id, user_id):
    return

def add_chat_history(type, user_id, target_id, msg):
    return

def delete_chat_history(history_id):
    return

def add_user(username, password, nickname):
    return





