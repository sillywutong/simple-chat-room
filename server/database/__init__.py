"""
查询数据库
"""
import sqlite3

conn = sqlite3.connect('server/database.db', isolation_level=None)  #每一次修改数据库都是立即写入，速度慢，但是保证不出现并发错误；想加快速度可以用#BEGIN TRANSACTION COMMIT

def get_cursor():
    return conn.cursor()

def init_database():
    with open('server/main.sql') as f:
        conn.executescript(f.read())

def get_user_by_name(username):
    """
        返回：
        {
            username:
            password:
        }
    """
    tups = conn.execute('select * from users where username = ?', (username, )).fetchall()
    if len(tups) != 1:
        print('Database: can not get user by username.')
        return None
    return {'username': tups[0][0], 'password': tups[0][1]}

def get_friend(username):
    '''
        根据给出的username, 查询所有好友, 返回好友usernames
    '''
    tups = conn.execute(
        '''
        select username
        from friends, users
        where username1 = ? and username2 = username or username2 = ? and username1 = username
        ''',
        (username, username)
    ).fetchall()
    return [tup[0] for tup in tups]

def is_friend(username1, username2):
    '''
        判断username2 是不是username1的好友
    '''
    tups = conn.execute(
        '''
        select *
        from friends
        where username1 = ? and username2 = ? or username2 = ? and username1 = ? 
        ''',
        (username1, username2, username1, username2,)
    ).fetchall()
    return len(tups) >= 1

def get_group(username):
    '''
    查询用户加入了哪些群，返回[{group_id, group_name, group_members}]
    '''
    tups = conn.execute(
        '''
        select x.group_id, group_name
        from groups as x, group_member as y
        where x.group_id = y.group_id and username = ?
        ''',
        (username, )
    ).fetchall()
    return [{
        'group_id': tup[0], 
        'group_name': tup[1],
        'group_members': get_group_members(tup[0])
        } for tup in tups]

def get_group_name(group_id):
    '''
     返回字符串
    '''
    tups = conn.execute('select group_name from groups where group_id = ?', (group_id, )).fetchall()
    if len(tups) != 1:
        print('Database: can not get group name by group id.')
        return None
    return tups[0][0]

def get_group_members(group_id):
    '''
        根据群组id，获取群内用户的usernames
    '''
    tups = conn.execute('select username from group_member where group_id = ?', (group_id, )).fetchall()
    return [tup[0] for tup in tups]

def get_offline_messages(username):
    '''
        格式为：
        [{
            is_private:,
            time:,
            source_username:,
            (target_username:,)
            (group_id:,)
            type:,
            data:
        }]
    '''
    tups_private_text = conn.execute(
        '''
        select target_username, source_username, time, text
        from history_private_text
        where target_username = ?
        ''',
        (username,)
    ).fetchall()
    tups_private_img = conn.execute(
        '''
        select target_username, source_username, time, img
        from history_private_image
        where target_username = ?
        ''',
        (username,)
    ).fetchall()

    gids = [g['group_id'] for g in get_group(username)]
    tups_group_text_list = [
        conn.execute(
        '''
        select group_id, source_username, time, text
        from history_group_text
        where group_id = ?
        ''',
        (gid,)
    ).fetchall() for gid in gids
    ]
    tups_group_img_list = [
        conn.execute(
        '''
        select group_id, source_username, time, img
        from history_group_image
        where group_id = ?
        ''',
        (gid,)
    ).fetchall() for gid in gids
    ]

    rst = [{
        'is_private': True,
        'target_username': tup[0],
        'source_username': tup[1],
        'time': tup[2],
        'type': 0, # text
        'data': tup[3]
    } for tup in tups_private_text]
    rst += [{
        'is_private': True,
        'target_username': tup[0],
        'source_username': tup[1],
        'time': tup[2],
        'type': 1, # img
        'data': tup[3]
    } for tup in tups_private_img]
    for tups in tups_group_text_list:
        rst += [{
            'is_private': False,
            'group_id': tup[0],
            'source_username': tup[1],
            'time': tup[2],
            'type': 0, # text
            'data': tup[3]
        } for tup in tups]
    for tups in tups_group_img_list:
        rst += [{
            'is_private': False,
            'group_id': tup[0],
            'source_username': tup[1],
            'time': tup[2],
            'type': 1, # img
            'data': tup[3]
        } for tup in tups]
    
    return rst

def add_friend(from_username, to_username):
    conn.execute(
        '''
        insert or ignore into friends (username1, username2)
        values (?, ?)
        ''',
        (from_username, to_username)
    )
    return

def add_to_group(group_id, username):
    conn.execute(
        '''
        insert or ignore into group_member (group_id, username)
        values (?, ?)
        ''',
        (group_id, username)
    )
    return

def is_in_group(group_id, username):
    tups = conn.execute(
        '''
        select *
        from group_member
        where group_id = ? and username = ?
        ''',
        (group_id, username)
    ).fetchall()
    return len(tups) > 0

def add_chat_history(**msg):
    assert 'is_private' in msg and 'type' in msg and 'source_username' in msg and 'time' in msg
    if msg['is_private']:
        assert 'target_username' in msg
    else:
        assert 'group_id' in msg

    if msg['is_private']:
        params = (
            msg['target_username'],
            msg['source_username'],
            msg['time'],
            msg['data']
        )
        if msg['type'] == 0: # text          
            conn.execute(
                '''
                insert into history_private_text (target_username, source_username, time, text)
                values (?, ?, ?, ?)
                ''',
                params
            )
        else:
            conn.execute(
                '''
                insert into history_private_image (target_username, source_username, time, img)
                values (?, ?, ?, ?)
                ''',
                params
            )
    else:
        params = (
            msg['source_username'],
            msg['group_id'],
            msg['time'],
            msg['data']
        )
        if msg['type'] == 0: # text          
            conn.execute(
                '''
                insert into history_group_text (source_username, group_id, time, text)
                values (?, ?, ?, ?)
                ''',
                params
            )
        else:
            conn.execute(
                '''
                insert into history_group_image (source_username, group_id, time, img)
                values (?, ?, ?, ?)
                ''',
                params
            )    

def delete_chat_history(username):
    s1 = 'delete from history_'
    s2 = 'where target_username = ?'
    for s in ['private_text ', 'private_image ']:
        conn.execute(
            s1 + s + s2,
            (username,)
        )

def add_user(username, password):
    conn.execute(
        '''
        insert into users (username, password)
        values (?, ?)
        ''',
        (username, password)
    )

def new_group(group_name, members):
    """
        给出群名和成员username，新建一个群, 
        成功返回群id，保证members里面的username都是存在的。
    """
    conn.execute(
        '''
        insert into groups (group_name)
        values (?)
        ''',
        (group_name,)
    )
    gid = conn.execute(
        '''
        select last_insert_rowid()
        from groups
        '''
    ).fetchall()[0][0]
    for username in set(members):
        conn.execute(
            '''
            insert into group_member (group_id, username)
            values (?, ?)
            ''',
            (gid, username)
        )
    return gid



