path=''   #聊天记录的文件目录，用target_name.json??  

current_user={'id': 0, 'username': 000, 'nickname':000}
session = None
shared_key = ''

last_msg = [{},{}]    # last_msg[0]是私聊， last_msg[1]是群聊，字典格式是'target_id': msg
last_time = [{},{}]   # 每个窗口最后收到消息的时间，按时间排序

chat_window = []
instances = []


