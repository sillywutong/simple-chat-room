from common.channel import Session
path='history'   #聊天记录的文件目录，用target_name.json??  

current_user=''
session = Session.Session(None, None)
shared_key = ''

tkroot = None

friends = set() # set of usernames
groups = {} # get group_name and group_members(set) by group_id
contacts_private = {} # {username: [{type, time, data, source_username}]}
contacts_group = {} # {group_id: [{}]}
tk_img_ref = []