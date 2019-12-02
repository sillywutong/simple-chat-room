## C/S架构的加解密设计：

> 1. 每次登陆，服务器和用户端产生一个会话密钥，使用AES对称加密算法进行加解密。+ 验证tag=16bytes，使用GCM模式
> 2. 密钥的交换过程参考HTTPS协议，采用diffle-hellman算法进行交换。

层1 解密前

| msg length（本来的message加上padding加密之后的长度） | AES padding length 以字节为单位 | AES 初始向量 | Tag      | MESSAGE    |
| ---------------------------------------------------- | ------------------------------- | ------------ | -------- | ---------- |
| 4bytes                                               | 1 byte                          | 12 bytes     | 16 bytes | msg length |

层2 解密后 （得到解密的message）

| MSG TYPE | BODY LENGTH | MSG BODY(全部都是dict，dict里面可嵌套list) |
| -------- | ----------- | ------------------------------------------ |
| 4 bytes  | 4 bytes     | body length ，键长-键-值类型-值长-值       |

消息类型总共有：

1. 登录：{username:  , password:  }
2. 注册: {username: , password: }
3. 加好友（发起私聊）{from: , to:  }(无需带上时间，只是把两个人的关系放进数据库)
4. 发起群聊: {from:    number:      ，['username1',   'username2',   'username3'...  ]    } 
5. 邀请用户进群聊：{ groupid:      username:    }
6. 聊天消息:{ type :  (0,1表示私聊和群聊)  ,  target_id:  , message：{ type:（0，1表示文字或图片) ,data: } }
7. （查询群内成员，隐式发送） ：{ group_id: }
8. 
9. 服务器响应登录成功：{ user_id: , username: }
10. 登录成功后服务器发送用户好友列表和群组列表（用于初始化窗口的，也可以读取本地聊天记录，但本地读取文件应该比较慢？,以及未读消息{‘friends': [{'username':,'user_id'], 'groups':[{'group_name': ,'group_id': }], 'msg':[按type18发送 ]}
11. 服务器响应登录失败: {errorcode}
12. 服务器响应注册成功: {user_id: , username: }
13. 服务器响应注册失败：{errorcode}
14. 服务器响应发起私聊：{status: } 0表示已经发起过聊天，直接打开以前的窗口，不需要加到数据库里；1 表示是新的好友，开启一个新的窗口
15. 服务器响应发起群聊：{ group id: ，group_name: }
16. 被添加进一个新群聊： {group id: , group_name: }   收到之后会发送一条查询群内成员的报文。
17. 返回群内成员：{group id: ,number: ,['username', 'username', 'username' ,.....]
18. 服务器转发聊天消息： { type:, time: , sender_id:, sender_name: , target_id:, target_name: , message: {type :, data:}}    以这个格式存到数据库中，也以这个格式转发给消息接收者和消息发送者，双方都会以这个格式存进本地聊天记录文件(.json)
19. 重复登录踢出 ：{} (body length=0)
20. 错误消息： {data:'sdfjskdjfkjskdjfksjdkfjk '}



层3 编码与解码 MSG BODY

MSG BODY是一个字典，根据层二的 BODY LENGTH读出整个MSG BODY. MSG BODY解码之后应该是键值对，键都是字符串str.encode(); .decode(). 值有多种类型，所以还得给出值的类型才能解码。层3是：

| key length | key        | value type | value length | value        |
| ---------- | ---------- | ---------- | ------------ | ------------ |
| 1 bytes    | key length | 1 bytes    | 4 bytes      | value length |

value type 有：

整数， string 字符串（包括各种名字，时间）， bool（私聊/群聊，文字/图片），list列表，列表里面可以嵌套任何东西，可以是n个层3的字典。 dict 层3嵌套。













###具体过程

用户登录：

用户																						                                   服务器

首先发送一个连接请求Hello												                                  收到请求，产生公钥+私钥对A，发送公钥A

收到公钥A，用公钥A加密password，和用户                                                      收到signin，用私钥A解密password，与数据库比对
名一起发送Signin																                                   如果正确，产生公钥+私钥对B，发送ACK+公钥B

收到ACK和公钥B，随机产生session key，用公钥B加密发送clientkey			收到clientkey，用私钥B解密得到session key

用session key加密一条什么消息，发送Encrypted message							用session key解出该消息，若成功，发送Hello 																																	done，标记用户状态为在线，保存ip

收到Hello done，可以进入主界面



Corner case：

1. 密码错误的时候，服务器不产生公私钥B，发送NCK。用户收到NCK, 重试密码，公私钥A不变。
2. encryped message解不出来，说明session key 不对，发送hello error，用户收到hello error，重试登录。



注册：

用户																													服务器

发送连接请求Hello																							收到Hello，产生公钥+私钥对A，发送公钥A（不区分是																															登陆还是注册）

收到公钥A，填写name，password，加密发送register								保存密码和账号到数据库，发送ACK register

收到ACK register，进入登陆界面																

corner case：

1. 若账号已有，发送NCK register，用户重填再重新发送。循环直到ACK。



发起会话：

用户																												服务器

发送 name1+name2  create																	   检查name2是否在线，找到ip，无论是否在线都发送ACK 																														create

收到ACK create，进入聊天界面

发送聊天数据 chat，子类型text/image，接收者name2						 收到chat，把数据发送给name2， 发送方name1，加上顺																														序号，监控服务器发给所有用户的chat信息

**中间网络断开了怎么办？**





退出登陆

用户																												服务器

发送 quit																										收到quit，更改状态为离线，再收到用户的chat信息时保存
																														然后发送ACK quit，更改用户的last time，删除session 																														key

收到ACK quit的时候正常退出，返回登陆界面。





群聊：

创建群聊：

create消息中加入字段：类型 双人or多人，人数：1就是单聊，大于1群聊，name列表给出所有name；服务器收到的时候，对所有name检查谁不在线，产生一个group id， 保存id对应的names。服务器发送ACK create group + group id。用户收到的时候要将group id和一个聊天窗口对应起来。

发送消息的时候，chat + group + groupid + 自己的name+ 消息。

服务器收到的时候，查询group id对应的账号，给所有在线的人发，不在线的缓存。





数据库：

离线聊天记录：

group          接收者账号           发送者账号            time         message

group=0表示是双人聊天， group=group id的时候，发送到对应的聊天窗口里去。所有属性确定一条元组。





**并发问题？**

