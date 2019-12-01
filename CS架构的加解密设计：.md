## C/S架构的加解密设计：

> 1. 每次登陆，服务器和用户端产生一个会话密钥，使用AES对称加密算法进行加解密。+ 验证tag=16bytes，使用GCM模式
> 2. 密钥的交换过程参考HTTPS协议，采用diffle-hellman算法进行交换。

层1 解密前

| msg Length 以字节为单位，是不含padding的真实长度 | AES padding length 以字节为单位 | AES 初始向量 | MESSAGE | TAG 用于完整性验证 |
| ------------------------------------------------ | ------------------------------- | ------------ | ------- | ------------------ |
| 4bytes                                           | 1 byte                          | 12 bytes     | \       | 16 bytes           |

层2 解密后 （得到解密的message）

|









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

