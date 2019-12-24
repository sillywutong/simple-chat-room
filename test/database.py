from server.database import *
import string
import random

from string import ascii_letters

def test():
    init_database()

    usernames = [''.join(random.sample(string.ascii_letters, 6)) for i in range(3)]
    passwords = [''.join(random.sample(string.digits, 6)) for i in range(3)] 
    
    for i in range(3): 
        add_user(usernames[i], passwords[i])
    
    # get user by name
    ans = [get_user_by_name(name) for name in usernames]
    assert [a['password'] for a in ans] == passwords, \
        'get_user_by_name: wrong password'

    # is_friend
    ans = [is_friend(usernames[i], usernames[(i + 1) % 3]) for i in range(3)]
    assert ans == [False] * 3, 'is_friend: false but return true'

    # add_friend
    for i in range(3):
        add_friend(usernames[i], usernames[(i + 1) % 3])
    ans = [is_friend(usernames[(i + 1) % 3], usernames[i]) for i in range(3)]
    assert ans == [True] * 3, \
        'is_friend: true but return false OR add_friend: fail'
    
    # get_friends
    ans = [get_friend(uid) for uid in usernames]
    assert list(map(len, ans)) == [2] * 3, 'get_friend: fail'

    # new_group
    group_names = [''.join(random.sample(string.ascii_letters, 8)) for i in range(2)]
    gids = [new_group(name, usernames) for name in group_names]

    # get_group_name
    ans = [get_group_name(gid) for gid in gids]
    assert ans == group_names, 'get_group_name: wrong name'

    # get_group
    ans = [get_group(uid) for uid in usernames]
    for a in ans:
        assert {g['group_id'] for g in a} == set(gids), \
            'get_group: wrong id'
        assert {g['group_name'] for g in a} == set(group_names), \
            'get_group: wrong name'

    # get_group_members_id
    ans = [get_group_members(gid) for gid in gids]
    assert list(map(set, ans)) == [set(usernames)] * 2, 'get_group_members_id: fail'
    
    # is_in_group
    ngname = ''.join(random.sample(string.ascii_letters, 8))
    ngid = new_group(ngname, [usernames[0]])
    ans = [is_in_group(ngid, uid) for uid in usernames]
    assert ans == [True, False, False], 'is_in_group: wrong'

    # add_to_group
    add_to_group(ngid, usernames[1])
    ans = [is_in_group(ngid, uid) for uid in usernames]
    assert ans == [True, True, False], \
        'is_in_group: wrong OR add_to_group: fail'

    # add_chat_history
    text = ''.join(random.sample(ascii_letters, 20))
    add_chat_history(
        is_private=True,
        target_username=usernames[2],
        source_username=usernames[0],
        type=0,
        data=text
    )
    add_chat_history(
        is_private=False,
        group_id=gids[0],
        source_username=usernames[1],
        type=0,
        data=text
    )
    with open('test/1.jpg', 'rb') as f:
        img = f.read()
    add_chat_history(
        is_private=True,
        target_username=usernames[2],
        source_username=usernames[1],
        type=1,
        data=img
    )
    add_chat_history(
        is_private=False,
        group_id=gids[1],
        source_username=usernames[0],
        type=1,
        data=img
    )

    # get_offline_messages
    ans = [get_offline_messages(username) for username in usernames]
    assert list(map(len, ans)) == [2, 2, 4], 'get_offline_messages: wrong'

    # delete_chat_history
    delete_chat_history(usernames[2])
    ans = get_offline_messages(usernames[2])
    assert len(ans) == 2, 'delete_chat_history: fail'

    print('database test finished!')