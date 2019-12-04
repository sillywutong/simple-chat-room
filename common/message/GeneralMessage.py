import struct
from PIL import Image
import base64
import io
from common.utils import long_to_bytes, Buffer

'''
 General Message: 
    usage:
        GeneralMessage.encode(msg_type=GeneralMessage.LOGIN, msg_body)
        GeneralMessage.decode(data)
    `msg_type`：消息类型
    `msg_body`: 消息体, 一定要是个`dict`，默认值是{}
    `data`：需要解码的bytes数据
    `msg_type`: 
        LOGIN 登入，  [username,password]
        REGISTER 注册， [username,password]
        ADD_FRIEND 发起聊天，  (str)username #朋友的用户名
        CREATE_G 创建群， {group_name, [username, username...] }
        INVITE 邀请 [group_id, username]
        SEND 发送消息 {type, target_id,  message:{type, data}}
        QUERY_MEMBER 查询群聊用户 (int)group_id
        LG_OK = 200 [user_id, username]
        REG_OK = 201 # [user_id, username]
        INITIALIZE = 202 # {friends:[username, user_id], groups[group_name, group_id], msg:[{}]}
        LG_FAIL = 400 # (int)error_code
        REG_FAIL = 401  # (int)error_code
        STATUS_ADD_FRIEND = 300 # [bool, str]
        NEW_FRIEND = 301 [userid, username]
        STATUS_CREATE_G = 302   # [group_id, group_name]
        ADD_TO_G = 303  # [group_id, group_name]
        G_MEMBER = 304  # [group_id, [username, username, username ...] ]
        PASS = 100  # {type, time, from_id, from_name, target_id, target_name, msg:{type, data}} 
        KICK = 500 
        GENERAL_ERROR = 501 # str

'''


LOGIN = 1

REGISTER = 2

ADD_FRIEND = 3

CREATE_G = 4
INVITE = 5
# group_id, username
SEND = 6

QUERY_MEMBER = 7


#
# server
#
LG_OK = 200

REG_OK = 201

INITIALIZE = 202


LG_FAIL = 400

REG_FAIL = 401


STATUS_ADD_FRIEND = 300

NEW_FRIEND = 301
STATUS_CREATE_G = 302

ADD_TO_G = 303

G_MEMBER = 304

PASS = 100

KICK = 500
GENERAL_ERROR = 501


MessageType=[LOGIN, REGISTER, ADD_FRIEND, CREATE_G, INVITE, SEND, QUERY_MEMBER, LG_OK, 
    REG_OK, INITIALIZE, LG_FAIL, REG_FAIL, STATUS_ADD_FRIEND, NEW_FRIEND, STATUS_CREATE_G, ADD_TO_G, G_MEMBER,\
    PASS, KICK, GENERAL_ERROR]

def _get_msg_type_by_value(value):
    pass

TYPE_TO_BYTES = {
    'int':1,
    'str':2,
    'list':3,
    'dict':4,
    'bool':5,
    'bytes':6
} 







def encode_any_type(data):
    '''
        input `value`, output `value type` 1byte+`value length` 4 byte + `value in bytes` 
    '''
    b = bytes()
    value_type = TYPE_TO_BYTES[type(data).__name__]     
    b += bytes([value_type])    # 1个字节 
    bytes_value = TYPE_TO_ENCODE_FUNCTION[type(data).__name__](data)
    value_length = len(bytes_value)
    b += struct.pack('!L', value_length)
    b += bytes_value
    return b
def encode_dict(data):
    print("encode dict")
    b = bytes()
    for key, value in data.items():
       # print("key length of key %s is %d, %s" %(key, len(key), bytes([len(key)])) )
        # key length 1 bytes + key + value type 1 bytes + value length 4 bytes + value 
        bytes_body = encode_any_type(value)  #return value type+value length + value
        #print("body: %s, body bytes:" % value)
       # print(bytes_body)
        b += bytes([len(key)])
        b += key.encode(encoding="utf-8")  #str
        b += bytes_body      
    return b

def encode_str(data):
    #print("encode string")
    b = data.encode(encoding = "utf-8")
    return b
def encode_int(data):
    #print("encode int")
    b = long_to_bytes(data)
   # b = bytes([data])
    return b

def encode_bool(data):
    #print("encode bool")
    b = bytes([1 if data else 0])
    return b

def encode_list(data):
    #print("encode list")
    b = bytes()
    for i in data:
        b += encode_any_type(i)
    return b
def encode_bytes(data):
    return data


def encode(msg_type, msg_body={}):
    assert(msg_type in MessageType)
    msg_body_to_bytes = encode_any_type(msg_body)
    return struct.pack('!L', msg_type)+ msg_body_to_bytes


def decode_int(data):
    return int.from_bytes(data, 'big')
def decode_str(data):
    return data.decode(encoding='utf-8')
def decode_dict(data):
    buffer = Buffer(data)
    ret = {}
    while not buffer.is_empty():
        len_key = buffer.read(1)
        key = buffer.read(len_key[0])
        body_type = buffer.read(1)[0]     # value type
        body = buffer.read(int.from_bytes(buffer.read(4), byteorder='big')) # value length
        body = decode_any_type(body, body_type)   # value
        ret[key.decode()] = body
    return ret
def decode_list(data):
    buffer =  Buffer(data)
    ret = []
    while not buffer.is_empty():
        #value type length value
        val_type = buffer.read(1)[0] #val type是个字节
        val = buffer.read(int.from_bytes(buffer.read(4),'big'))
        val = decode_any_type(val, val_type)
        ret.append(val)
    return ret
def decode_bytes(data):
    return data
def decode_bool(data):
    return True if data[0] else False

def decode_any_type(data, type):
    return TYPE_TO_DECODE_FUNCTION[type](data)



def decode(data):
    print("decoding data")
#    print(data)
    ret={}
    buffer = Buffer(data)
    msg_type = int.from_bytes(buffer.read(4),'big')
    print("msg_type: %d" % msg_type)
    ret['msg_type'] = msg_type
    t = buffer.read(1)[0]
    buffer.read(4)
    ret['msg_body'] = decode_any_type(buffer.read_all(),t)
    return ret
TYPE_TO_ENCODE_FUNCTION = {
    'int': encode_int,
    'str': encode_str,
    'list': encode_list,
    'dict': encode_dict,
    'bool': encode_bool,
    'bytes': encode_bytes
}
TYPE_TO_DECODE_FUNCTION = [
    decode_int, #填充0
    decode_int,
    decode_str,
    decode_list,
    decode_dict,
    decode_bool,
    decode_bytes
]
'''
a = {'key':1, 'ksds':2}
print(type(a).__name__)
print(encode_dict(a))

b = [1,2,3,4]
print(type(b).__name__) 
c =12412563451263
print(type(c).__name__)
d = 'sdsdsdjkajskjk'
print(type(d).__name__)
e = True
print(type(e).__name__)
with open('../../test.png',"rb") as image_file:
    image = image_file.read()
    img = bytes(image)
    print(type(img).__name__)
io = io.BytesIO(img)
img = Image.open(io)
img.show()
'''