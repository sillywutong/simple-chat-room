"""
查询数据库
"""
import sqlite3

conn = sqlite3.connect('server/database.db', isolation_level=None)  #每一次修改数据库都是立即写入，速度慢，但是保证不出现并发错误；想加快速度可以用#BEGIN TRANSACTION COMMIT

def get_cursor():
    return conn.cursor()

def get_user_by_id(user_id):
    """
        根据给出的user id， 从数据库中查询user， 返回一个字典类型，包含字段：
        user_id: id,
        username: username,
        password: password,
    """
    return {}
def get_user_by_name(username):
    """
        返回：
        {
            user_id:
            username
        }
    """
    return {}

def get_friend(user_id):
    '''
        根据给出的user id, 查询所有好友, 返回好友user id, username, 是个列表[[user_id, user_name],[user_id, user_name],...]
    '''
    friends=[]
    c = get_cursor()
    rows = c.execute('SELECT user_id1, user_id2 FROM friends WHERE user_id1=? or user_id2=?', [user_id, user_id]).fetchall()
    for t in rows:
        if t[0]==user_id:
            c2=get_cursor()
            fname = c.execute('SELECT username FROM users WHERE id=?',[t[1]]).fetchone()[0]
            friends.append([t[1],fname])
        else:
            c2=get_cursor()
            fname = c.execute('SELECT username FROM users WHERE id=?',[t[0]]).fetchone()[0]
            friends.append([t[0],fname])
    return friends

def is_friend(user_id1, user_id2):
    '''
        判断user_id2 是不是user_id1的好友
    '''
    c=get_cursor()
    r = c.execute('SELECT * FROM friends WHERE (user_id1=? and user_id2=?) or (user_id1=? and user_id2=?)', [user_id1,user_id2, user_id2, user_id1]).fetchall()
    if len(r):
        return True
    return False
def get_group(user_id):
    '''
    查询用户加入了哪些群，返回[[group_id, group_name],[group_id, group_name],...]
    '''
    groups=[]
    c=get_cursor()
    rows = c.execute('SELECT X.group_id, group_name From group_member as X, groups as Y WHERE user_id=? and X.group_id=Y.group_id',[user_id] ).fetchall()
    for t in rows:
        groups.append([t[0],t[1]])
    return groups
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
        根据群组id，获取群内所有用户的信息，返回二维数组[[user_id, username]]
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
            # target_name, 
            message:{type, data}

        }]
    '''
    return {}

def add_friend(from_id, to_id):
    c=get_cursor()
    c.execute('INSERT INTO friends (user_id1, user_id2) values(?,?)',[from_id, to_id])
    return True

def add_to_group(group_id, user_id):
    return
def is_in_group(group_id, user_id):
    return

def add_chat_history(type, user_id, target_id, msg):
    return

def delete_chat_history(history_id):
    return

def add_user(username, password):
    '''
    插入数据库后，返回id（id在数据库里按递增顺序存放
    '''
    c = get_cursor()
    c.execute('INSERT INTO users (username, password) values (?,?)', [username, password])

    return c.lastrowid
def new_group(group_name, members):
    """
        给出群名和成员id，新建一个群, 成功返回群id，保证members里面的id都是存在的。
    """
    c=get_cursor()
    c.execute("INSERT INTO groups (group_name) values (?)", [group_name])
    gid = c.lastrowid
    c= get_cursor()
    for mid in members:
        c.execute('INSERT INTO group_member (group_id, user_id) values (?,?)', [gid, mid])
    
    return gid



