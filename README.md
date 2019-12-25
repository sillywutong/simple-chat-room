#基于Socket的聊天室设计

17307130331 陈疏桐                            17307130153 陈彦伯

## 1  Basic Idea

本次socket编程实验，我们选择基于python的`socket`库来搭建一个网络聊天室。当下有很多聊天软件、社交应用，例如Facebook、wechat等，都有隐私、数据方面的争议，在最初设计的时候，我们希望做出一个用户对话仅聊天双方可解密的软件，服务端只负责数据的转交。但这样涉及到用户与用户之间进行密钥交换，代价比较大，在代码实现上也较为困难，所以最后我们仍采用了中心化的架构，但服务端不保存用户的聊天记录。聊天室的设计基于以下几种考虑：

1. 安全性。不能做P2P的架构，我们至少要对服务器和用户之间的对话内容加密。
2. 低延迟。要做到即时聊天的即时，又要保证安全，应该用效率高的对称加密算法对聊天内容进行加密。同时，数据包的格式、数据以什么样的类型传输，应该经过精心的设计，使得有效内容占比最高。
3. 覆盖基本功能。聊天室应该满足基本的功能，例如实现私聊和群聊，支持多种消息类型。
4. 鲁棒性。服务端应该尽量覆盖到每一种可能的异常，使之可以在处理异常之后继续正常运行。用户端也应该覆盖各种异常，并给出提示。

## 2  聊天室功能

目前已经实现的功能有：

- [x] 参考HTTPS握手协议，打开应用时用Diffie-Hellman 密钥交换算法交换AES密钥
- [x] 所有应用内数据传输用AES加密，还包括一个校验码验证消息完整性
- [x] 数据传输时序列化为二进制字节；收到数据时反序列化
- [x] 数据库存储用户名密码、好友关系、群组信息和群组成员、离线时聊天记录
- [x] 使用tkinter做图形界面
- [x] 一台电脑可以同时登录多个用户
- [x] 登录、注册；两个界面可以方便地切换
- [x] 重复登录的时候，旧的登录被踢下线
- [x] 支持群聊、私聊
- [x] 输入用户名加好友（加好友实际上等于直接发起会话，因为不需要对方通过）
- [x] 创建一个新的群，并把好友拉入群聊。与微信发起群聊相似，不需要好友同意可以直接发起会话
- [x] 在线时被邀请进入新的群组，会收到提示；在线时被加为好友，会收到提示
- [x] 聊天时如果有一方不在线，将聊天记录暂时保存在服务端数据库中，用户上线时会收到未读消息
- [x] 支持多行内容和图片传输
- [x] 好友列表、群组列表分开，便于查找
- [x] 最近的会话列表，按照最后互动事件的顺序进行排序；显示一条最近消息
- [x] 群聊中显示群成员，可以直接对群成员发起私聊
- [x] 有新消息时打开的聊天窗口自动滚到底部
- [x] 再次打开聊天窗口时自动恢复所有聊天记录
- [x] 覆盖多种异常检测并弹窗提示
- [ ] 群聊窗口中邀请好友加群
- [ ] 本地文件以pkl保存聊天记录；聊天窗口中打开显示聊天记录

### 2.1  用户角度的状态转换图

![image-20191224221434356](C:\Users\CST\AppData\Roaming\Typora\typora-user-images\image-20191224221434356.png)



## 3  协议设计

### 3.1  信息加密

信息加密分为两个阶段完成，一个是密钥交换阶段，另一个是消息传输时的加密阶段。密钥交换在应用打开时完成，参考HTTPS握手协议，这里使用Diffie-Hellman密钥交换算法。用户和服务端各自解得共同密钥，之后的所有数据都用这个共同密钥来加密和解密。会话加密使用带完整性验证的AES对称加密算法。

之所以对称加密来加密会话信息，是因为非对称加密相比与对称加密速度非常慢。而对称加密的密钥显然也不能明文传输，所以需要某种非对称加密算法来进行密钥交换。

之所以不用RSA进行密钥交换，是因为假设用户随机生成一个密钥然后用服务器公钥加密，在这次对话结束之后，假如服务器被第三方劫持，第三方可以获得服务器私钥，则不仅可以窥探以后的会话信息，还可以解出之前所有会话的密钥，从而解密之前的所有消息。而Diffie-Hellman算法每次会话都会生成一个新的随机数，可以解决上述问题。

#### 3.1.1 密钥交换

Diffie-Hellman算法基本流程是：

1. 定义两个全局公开的参数，素数q和一个整数a，a是q的一个原根。
2. 会话双方（A和B）各自随机产生一个作为私钥的随机数XA和XB，然后根据XA和XB计算出公钥$YA=a^{XA} mod q$ , $YB= a^{XB} mod q$ 。
3. 两者交换公钥。
4. 两者根据$K=(YB)^{XA} mod q$和 $K=(YA)^{XB} mod q$计算得到共享密钥。

代码实现时，全局参数q和a保存在`config.json`中，用专门的模块负责计算私钥、公钥和共享密钥。应用开启时，服务器和客户端各自进入搭建会话环境函数，在其中调用加密模块，互相交换公钥，然后计算得到共享密钥，作为全局参数保存起来。当用户下线时，清空共享密钥。

#### 3.1.2   会话加密

会话使用GCM模式的AES加密算法，GCM模式可以提供完整性校验。在我们的应用中，使用sha256散列算法将会话密钥截断成128bit（16字节），作为AES密钥，每次加密数据之前，再随机产生一个12字节的`nounce`（12字节是NIST SP 800-38D推荐的GCM模式下的长度），数据加密之后，会产生一个16字节的MAC用于完整性校验。

代码使用`pycryptodome.AES`库实现。

### 3.2  数据包格式

聊天室协议可以分为三层，第一层为解密前，第二层为解密后，第三层为会话消息。

####3.2.1  每一层数据包格式

##### 第一层 解密前：

| msg length（本来的message加上padding加密之后的长度） | AES padding length 以字节为单位 | AES 初始向量 | Tag      | MESSAGE    |
| ---------------------------------------------------- | ------------------------------- | ------------ | -------- | ---------- |
| 4 bytes                                              | 1 byte                          | 12 bytes     | 16 bytes | msg length |

AES加密要求数据与16字节对齐，所以序列化后的`MESSAGE`可能需要在后面补0作为padding，AES padding length字段给出了padding的长度，`msg length`字段给出了加了padding之后的总长度。带上长度，是为了确定继续接收的大小，每一次有新数据时，调用`socket.recv(4)`先接收前4个字节的`msg length`，根据它来确定接下来要接收多少个字节。

AES初始向量用来和共享密钥一起解密`MESSAGE`。`Tag`用于完整性校验。

##### 第二层 解密后：

| MSG TYPE | MSG BODY，可能是多种python数据类型 |
| -------- | ---------------------------------- |
| 4 bytes  | （数据类型 -  长度 - 值）          |

解密`MESSAGE`得到`MSG_TYPE`和`MSG BODY`, `MSG_TYPE`表示该数据的种类，例如登录、好友请求、服务器给的登录响应等。根据不同的类型, `MSG_BODY`有不同的数据类型和格式。

##### 第三层 会话消息：

`MSG_BODY`可以包含7种数据类型：

- `int`
- `str`
- `list`
- `dict`
- `bool`
- `bytes`
- `datetime`

通常来说，一条消息会采用`dict`或者`list`作为最外层，里面包含多个数据段，字典和列表等也可以多层嵌套。`bytes`一般用来传输图片，`datetime`用来传输时间戳，`str`是很通用的类型，`int`用来表示id、数量等，`bool`通常在响应中表示状态。

除了`dict`以外，其他类型的数据格式都是：

| data type | data length | data        |
| --------- | ----------- | ----------- |
| 1 字节    | 4 字节      | data length |

`dict`中每一个元素的格式是：

| key length | key        | value type | value length | value        |
| ---------- | ---------- | ---------- | ------------ | ------------ |
| 1 byte     | key length | 1 byte     | 4 bytes      | value length |

只有用这种方式，我们才能反序列化得到键和值，并且嵌套这个过程许多次。其中的`value`很可能是另一个`dict`, 也可能是个列表，列表中又可以包含许多不同类型的元素。

####3.2.2  协议包含的消息类型和消息体格式

在`GeneralMessage`模块中，定义了所有消息类型（4字节的`msg_type`)，它们的消息体格式、对应的十进制编码和应用场景为：

| 编号 |      助记符       |                          消息体格式                          |                           应用场景                           |
| ---- | :------------: | :---------------------------------------------: | :-----------------------------------------------------: |
| 1    |       LOGIN       |           `[username, password]`(`list[str,str]`)            |                       用户点击登录按钮                       |
| 2    |     REGISTER      |           `[username, password]`(`list[str,str]`)            |                       用户点击注册按钮                       |
| 3    |    ADD_FRIEND     |                      `username` (`str`)                      |                            加好友                            |
| 4    |     CREATE_G      | `[group_name,[username,username....]]`(`list[str, list[str,str,str...]]`)，其中用户名列表至少有一个（创建者本身） |                            创建群                            |
| 5    |      INVITE       |          `[group_id, username]`,(`list[int, str]`)           |                         邀请好友进群                         |
| 6    |       SEND        | `{'is_private': True, 'target_username'/'group_id':,'type':  ,'data':}`,(`dict{bool, str or int, bool, str}`).                                               其中，`is_private`表示为私聊，`type`区分数据类型是字符串还是图片 |                       用户发送聊天消息                       |
| 7    |   QUERY_MEMBER    |                      `group_id`,(`int`)                      |                  查询群成员（暂时没有用到）                  |
| 10   |      LOGOUT       |                      `username`(`str`)                       |                           用户登出                           |
| 200  |      LG_OK·       |                      `username`(`str`)                       |                   服务端响应用户登录，成功                   |
| 400  |      LG_FAIL      |      `errorcode`(`int`)，0表示用户不存在，1表示密码错误      |                       响应用户登录失败                       |
| 201  |      REG_OK       |                `{}`(`dict{}`)，不允许发送None                |                       响应用户注册成功                       |
| 401  |     REG_FAIL      |             `errorcode`(`int`)，表示用户已经存在             |                       响应用户注册失败                       |
| 202  |    INITIALIZE     | `{'friends':[username,username...],'groups':[[group_name, group_id],[group_name,group_id]...],'msgs':[msg]}`,(`dict{list[str],list[list[str,str]], list[dict{...}]}`) | 用户登录成功之后，用于初始化界面的。发送好友列表、群组列表和离线消息。 |
| 300  | STATUS_ADD_FRIEND | `{'success':, 'error','username':}`(`dict{bool, str, str }`) | 响应添加好友请求是否成功，`error`给出错误信息，错误可能来自不能加自己为好友、用户名不存在、已经是朋友关系等。 |
| 301  |    NEW_FRIEND     |                      `username`(`str`)                       |         当用户在线时，别人加自己为好友会收到这个提示         |
| 303  |     ADD_TO_G      | `{‘source_name':,'group_id':,'group_name':,'group_members':[username,...]}`,(`dict{str,int,str,list[str,str...]}`) |               用户在线时被加入群会收到这个提示               |
| 304  |     G_MEMBER      | `[group_id,[username,username...]]`(`list[int,list[str,str...]]`) |              响应群成员查询请求（暂时没有用到）              |
| 305  |   STATUS_INVITE   | `{'success':,'error':,'group_id':,'group_name':,'group_members':[username...]}`(`dict{bool,str,int,str,list[str,str]}`) |     响应邀请好友进群的请求，返回给该邀请者一个群成员列表     |
| 306  |    NEW_MEMBER     | `{'source_name':,'group_id','group_name':,'group_members':[username...]}`(`dict{str,int, str, list[str,str]}`) |          当有新成员加入群时，旧的成员会收到一条提示          |
| 100  |       PASS        | `{'is_private': True, 'time':,source_username':,'target_username'/'group_id':,'type':  ,'data':}`,(`dict{bool, datetime, str, str or int, bool, str}`) |                     聊天信息由服务器转交                     |
| 500  |       KICK        |                              {}                              | 重复登陆时旧的会话收到这条消息，由服务端踢下线，用户端关闭窗口 |
| 501  |   GENERAL_ERROR   |                            `str`                             |                         其他异步错误                         |

#### 3.2.3  封装和解封装过程

`GeneralMessage`模块定义了所有的消息类型、对应编号，并且负责完成数据的序列化和反序列化。为每一种类型实现序列化和反序列化函数，以及总的`encode`和`decode`函数。在发送消息之前，将原始python类型的数据，调用`encode`序列化，其中递归地根据类型调用具体序列化函数，把数据封装成第三层的格式。

计算消息体的总长度，再加上一个字节的消息类型（`msg_type`），封装成第二层格式。

最后将第二层的数据加上padding，计算padding长度，用AES加密，得到MAC和加密后的数据总长，与初始向量一起封装成第一层。然后就可以用socket发送数据包了。



收到数据时，首先接收前4个字节，计算得到未来要从socket接收的数据长度。然后依次得到AES初始向量、MAC和加密数据。用AES解密并进行完整性校验，解封得到第二层。

读取第二层的前4个byte，得到数据类型。剩下的数据就是第三层。

反序列化第三层数据，得到原始消息。根据第二层解封时得到的消息类型，服务端转到不同的事件处理程序，在具体的处理程序中，按格式解释原始消息中的各种参数。



## 4  应用架构

### 4.1   数据库设计

服务端保存用户信息、好友关系、群组关系和离线聊天记录。其中，为了有一定的安全性，用户密码简单地使用MD5散列算法“加密”存储，md5虽然可以暴力破解，但是对于复杂的密码破解耗时还是比较长，md5算法速度快，也是各大网站常用的密码存储方法。

应用允许用户为群组重复命名，所以群组以`id`唯一标识。但用户名是唯一的，直接做主键。数据库的关系模式如下：

```sql
CREATE TABLE IF NOT EXISTS "history"(
"id" INTEGER not NULL,
"type" INTEGER not NULL,
"target_id" INTEGER not NULL,
"source_id" INTEGER not NULL,
"msg" BLOB,
PRIMARY KEY("id" ASC)
);
CREATE TABLE IF NOT EXISTS "users"(
"username" TEXT not NULL,
"password" TEXT not NULL,
PRIMARY KEY("username" ASC)
);
CREATE TABLE IF NOT EXISTS "history_private_text"(
"id" INTEGER not NULL,
"target_username" TEXT not NULL,
"source_username" TEXT not NULL,
"time" DATETIME not NULL,
"text" TEXT not NULL,
PRIMARY KEY("id" ASC),
FOREIGN KEY ("target_username") REFERENCES "users"("username"),
FOREIGN KEY ("source_username") REFERENCES "users"("username")
);
CREATE TABLE IF NOT EXISTS "history_private_image"(
"id" INTEGER not NULL,
"target_username" TEXT not NULL,
"source_username" TEXT not NULL,
"time" DATETIME not NULL,
"img" BLOB not NULL,
PRIMARY KEY("id" ASC),
FOREIGN KEY ("target_username") REFERENCES "users"("username"),
FOREIGN KEY ("source_username") REFERENCES "users"("username")
);
CREATE TABLE IF NOT EXISTS "history_group_text"(
"id" INTEGER not NULL,
"group_id" INTEGER not NULL,
"source_username" TEXT not NULL,
"time" DATETIME not NULL,
"text" TEXT not NULL,
PRIMARY KEY("id" ASC),
FOREIGN KEY ("group_id") REFERENCES "groups"("group_id"),
FOREIGN KEY ("source_username") REFERENCES "users"("username")
);
CREATE TABLE IF NOT EXISTS "history_group_image"(
"id" INTEGER not NULL,
"group_id" INTEGER not NULL,
"source_username" TEXT not NULL,
"time" DATETIME not NULL,
"img" BLOB not NULL,
PRIMARY KEY("id" ASC),
FOREIGN KEY ("group_id") REFERENCES "groups"("group_id"),
FOREIGN KEY ("source_username") REFERENCES "users"("username")
);
CREATE TABLE IF NOT EXISTS "group_member"(
"group_id" INTEGER NOT NULL,
"username" TEXT NOT NULL,
PRIMARY KEY("group_id" ASC, "username"),
FOREIGN KEY ("group_id") REFERENCES "groups"("group_id"),
FOREIGN KEY ("username") REFERENCES "users"("username")
);
CREATE TABLE IF NOT EXISTS "groups"(
"group_id" INTEGER NOT NULL,
"group_name" TEXT NOT NULL,
PRIMARY KEY("group_id" ASC)
);
CREATE TABLE IF NOT EXISTS "friends"(
"username1" TEXT NOT NULL,
"username2" TEXT NOT NULL,
PRIMARY KEY("username1", "username2"),
FOREIGN KEY ("username1") REFERENCES "users"("username"),
FOREIGN KEY ("username2") REFERENCES "users"("username")
);
```

### 4.2  socket通信

服务端和用户端之间通过建立在TCP上的socket进行通信:

```c
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
```

服务端开启时，建立套接字，然后绑定到一个端口，并调用`listen`进行监听：

```c
sock.bind((config['server']['ip'], config['server']['port']))
sock.listen(1)
```

当用户端开启时，也创建一个套接字，调用`.connect`请求连接服务端。

服务端收到一个新的连接请求时，调用`.accept`接受。然后双方用`.send()`发送自己的公钥，并用`.recv`接收对方的公钥，产生共享密钥之后，会话成功建立。

之后的会话信息都用共享密钥加密。两者调用`.sendall()`发送封装好的数据包，用`.recv()`接收数据包。这里要注意`.send()`和`.sendall()`的区别。调用`.send(data)`，不一定会立即将所有数据都发送到对方，而是可能将数据先存放在缓冲区中，然后返回实际发送出去的字节数，如果用`send()`，应用程序需要检查已经发送的大小，然后循环发送直到所有数据都发送出去。`.sendall`则自动完成了后面的逻辑，直到所有数据都实际发送、或者遇到了错误才会返回，并且遇到错误时应用程序无法得知已经发送的大小，需要重新发送。

两者通过`.recv`接收数据`.recv`返回实际接收的数据。当有新数据到来的时候，首先设置缓冲区大小为4个字节，接收数据包的前四个字节（计算接下来要接收的长度）。同时，进行差错控制。如果对方掉线，`.recv`会返回0（字节）。我们用`.recv(MSG_WAITALL)`来接收前4个字节，`.recv`和`.send()`一样，也可能不会接收到完整缓冲区大小的数据后才返回，实际接收的数据长度可能小于我们定义的缓冲区长度。而加上`MSG_WAITALL`选项，它会在接收完指定长度的数据、或者遇到错误才返回。所以，这里判断实际接收的大小，如果不足4个字节就说明对方已经崩溃或者关闭连接。

如果服务端检测到一个用户退出，就调用对应套接字的`close`关闭连接，同时，跟会话有关的数据，例如会话与socket的对应关系、会话和用户名的对应关系、会话列表中对应的项也要被删掉。

#### 4.2.1  服务端IO复用

服务端使用IO复用`select`库来同时监听多个连接。

`select`库的工作原理是，进程指定内核监听哪些文件描述符的哪些事件，当没有文件描述符事件发生的时候，进程被阻塞，超过一定时间后，进程被唤醒，内核再次遍历所有的文件描述符，检查是否有事件发生。如果有，内核返回对应的文件描述符，把这个文件描述符复制到用户空间，让进程进行处理。

在服务端，开启时建立的`socket`套接字需要不断地监听是否有新的用户要接入，这是一个读事件；当用户接入之后，双方会建立起一个会话`Session`，数据在会话中加密发送，这个类里面封装了数据包从原始数据到加密后的封装以及解封装的过程，`.sendall`在这个类中调用。所以服务端也要监听这些`Session`：

```python
while(1):
        rlist, wlist, xlist = select.select(list(map(lambda x: x.socket, sessions))+[sock], [],[]) #sock监听新的用户连接
```

当进程从`select()`函数返回的时候，说明有文件描述符事件发生。我们遍历`rlist`，如果文件描述符是`sock`，表明是一个新的用户连接，我们调用`server_new_session`建立新的会话，并建立会话和socket、用户名等的对应关系。 否则，就是旧的会话收到了新数据包，我们用`.recv`开始接收：

首先以`MSG_WAITALL`选项接收前四个字节，计算得包长度后，接收剩余字节。由于`recv`返回时不一定是接收了指定的数据长度，所以我们需要循环判断，直到整个数据包都被接收下来才可以进行处理。除了前四个字节，后面的数据都不用`MSG_WAITALL`选项，是因为这个选项会使服务端阻塞，使它在接收一个很长的数据包时没有办法处理其他套接字发过来的小数据包，造成效率降低；并且网络堆栈可能不够大，使得`recv`发生错误。因此在服务端，我们定义一个缓冲区`bytes_buffer`来暂存接收下来的数据，定义`bytes_torecv`和`bytes_recved`：

```python
bytes_buffer[sess] += sess.socket.recv(to_receive[sess] - received[sess])
received[sess] = len(bytes_buffer[sess])
```

当两者长度相同的时候，表明一个数据包完整接收。我们用一个`BytesReader`类读出缓冲区中的数据，然后把`bytes_buffer`清空，继续接收下一个包。

#### 4.2.2  用户端多线程

用户端有登录、注册、主界面、聊天等多个窗口，每个窗口在打开的时候，需要监听服务端发来的数据，当窗口关闭的时候不再监听。所以这里我们用`Thread`库来处理。

用户端开启时进入欢迎界面，第一次进入欢迎界面时，调用`client_new_session`与服务端连接并建立会话。

之后，我们建立一个线程`main_listener`，这个后台线程负责监听套接字，接收服务端发来的所有数据包。还是用`seclect`来阻塞，不同的是这里只需要监听一个套接字：

```python
rlist, wlist, xlist = select.select([session.socket], [session.socket],[])
```

`main_listener`只负责处理服务端关闭事件、重复登录被踢下线的事件，其他类型的数据包应该交给具体的窗口去处理。所以我们定义了一个列表`specific_listener`，这个列表实际上存放的是许多处理函数。每个窗口类都会定义一个处理函数`handler`，它负责处理用户进行某种操作后从服务端收到的响应。当窗口被打开的时候，我们将`handler`加到列表中去，当窗口关闭的时候把它删除。这样，在`main_listener`中接收到数据包后，遍历`specific_listener`列表并依次调用所有处理函数，将消息类型和消息体传给`handler`。



### 4.3  实现逻辑

遵循模块化编程，应用的文件结构是：

```xml-dtd
| config.json
| client.py
| server.py
└ client						%客户端
| | __init__.py
| └ client_global             % 全局变量
| | | __init__.py
| └ interface                 % 窗口和交互事件
| | | buildsession.py
| | | chat_window.py
| | | chatform.py
| | | contactlist.py
| | | group_creater.py
| | | login.py
| | | register.py
| | | welcome.py
| | | welcomebase.py
| | | chat_history_window.py
| | | vertical_scrolled_frame.py
| └ listener				 % 监听套接字
| | | __init__.py
| └ history_file_controller  % 处理本地聊天记录（未完成）
| | | __init__.py
└ common						% 用户、服务端一些公用模块
| | __init__.py
| | config.py					% 读取配置文件
| └ channel						% 会话
| | | __init__.py
| | | Session.py				% 会话类
| └ Crypto						% 加密模块
| | | crypt.py
| | | prime.py
| └ message						% 消息类型、消息体序列和反序列化
| | | __init__.py
| | | GeneralMessage.py
| └ utils						% 其他工具
| | | __init__.py
└ server						% 服务端
| | __init__.py
| └ server_global				% 全局变量
| | | __init__.py	
| └ events						% 事件处理	
| | | add_friend.py
| | | invite_to_group.py
| | | login.py
| | | logout.py
| | | register.py
| | | send_message.py
| | | new_group.py
| | | query_member.py
| └ database					% 数据库操作
| | | __init__.py
| | database.db
| | main.sql

```

#### 4.3.1  服务端

![image-20191225123321891](C:\Users\CST\AppData\Roaming\Typora\typora-user-images\image-20191225123321891.png)

#### 4.3.2  用户端

![image-20191225141108200](C:\Users\CST\AppData\Roaming\Typora\typora-user-images\image-20191225141108200.png)



## 5  运行截图

<img src="C:\Users\CST\AppData\Roaming\Typora\typora-user-images\image-20191225141249471.png" alt="image-20191225141249471" style="zoom:30%;" />



<img src="C:\Users\CST\AppData\Roaming\Typora\typora-user-images\image-20191225141425077.png" alt="image-20191225141425077" style="zoom:23%;" /><img src="C:\Users\CST\AppData\Roaming\Typora\typora-user-images\image-20191225141749022.png" alt="image-20191225141749022" style="zoom:26%;" /><img src="C:\Users\CST\AppData\Roaming\Typora\typora-user-images\image-20191225141845407.png" alt="image-20191225141845407" style="zoom:30%;" /><img src="C:\Users\CST\AppData\Roaming\Typora\typora-user-images\image-20191225142547368.png" alt="image-20191225142547368" style="zoom:25%;" />

<img src="C:\Users\CST\AppData\Roaming\Typora\typora-user-images\image-20191225142029385.png" alt="image-20191225142029385" style="zoom:33%;" /><img src="C:\Users\CST\AppData\Roaming\Typora\typora-user-images\image-20191225142116576.png" alt="image-20191225142116576" style="zoom:25%;" /><img src="C:\Users\CST\AppData\Roaming\Typora\typora-user-images\image-20191225142144804.png" alt="image-20191225142144804" style="zoom:33%;" />

<img src="C:\Users\CST\AppData\Roaming\Typora\typora-user-images\image-20191225142240307.png" alt="image-20191225142240307" style="zoom:30%;" /><img src="C:\Users\CST\AppData\Roaming\Typora\typora-user-images\image-20191225142343913.png" alt="image-20191225142343913" style="zoom:33%;" />

<img src="C:\Users\CST\AppData\Roaming\Typora\typora-user-images\image-20191225143119268.png" alt="image-20191225143119268" style="zoom:28%;" /><img src="C:\Users\CST\AppData\Roaming\Typora\typora-user-images\image-20191225143928438.png" alt="image-20191225143928438" style="zoom:33%;" /><img src="C:\Users\CST\AppData\Roaming\Typora\typora-user-images\image-20191225144009803.png" alt="image-20191225144009803" style="zoom:25%;" />

<img src="C:\Users\CST\AppData\Roaming\Typora\typora-user-images\image-20191225144321662.png" alt="image-20191225144321662" style="zoom:20%;" /><img src="C:\Users\CST\AppData\Roaming\Typora\typora-user-images\image-20191225144954072.png" alt="image-20191225144954072" style="zoom:18%;" />

<img src="C:\Users\CST\AppData\Roaming\Typora\typora-user-images\image-20191225144823963.png" alt="image-20191225144823963" style="zoom:33%;" />

<img src="C:\Users\CST\AppData\Roaming\Typora\typora-user-images\image-20191225145728706.png" alt="image-20191225145728706" style="zoom:33%;" />

##6  设计的优缺点

聊天室协议设计的优点：

1. 会话消息全部加密，包括发送用户名、密码、服务端的响应等，比较安全。并且使用的加密方式比较高效。
2. 加密时先用diffie-hellman交换密钥，即使窃取了双方交换的公钥，也无法解密消息。
3. 数据包序列化成二进制流发送，而不是以字符串或JSON的形式发送，这样更节省流量，并且解析起来也更方便，不需要考虑使用什么作为分隔符等问题。
4. 可以传输任意复杂消息体，多种python类型可以自由组合。
5. 数据包格式按照最方便解析的顺序来设计，先是长度，用于决定接收缓冲区大小；再是类型，最后消息体也是按类型-长度-值来存放。
6. 加密、数据包和数据传输形式的设计，让消息延迟很低。即使发送1M的大图，对方也基本可以马上收到。
7. 支持多种消息类型，文字可以多行发送，图片不限制大小。这两种消息格式相同，只用`type`来区分，所以未来还可以加入更多类型，可扩展性强。
8. 灵活自由。如果要加入新功能，只需要为新的消息类型定义一个编号，再分别定义具体的处理程序即可。应用的基本逻辑不会变化。

应用设计的优点：

1. 代码上，模块分工清晰，用户端和服务端代码可以完全分离。
2. 可扩展性强。要加入新数据类型，只需要在`GeneralMessage`里添加序列化和反序列化函数；要加新消息类型，只需要在`GeneralMessage`中定义新编号，并在`event`中加入新的处理程序即可。
3. 功能比较完整。
4. 界面清晰，最近会话列表自动排序，以颜色区分私聊和群聊。
5. 覆盖各种可能异常。



设计的缺点：

1. 因为没办法像HTTPS协议那样制作证书，没有办法防止中间人攻击（中间人可以冒充服务器与用户端交换公钥，用户端无法分辨，导致之后的会话信息全部被中间人窃取）
2. 有一些消息类型采用了字典格式，比如聊天记录、初始化消息等，这样方便写代码，但是键占据了很多字节，造成浪费，特别是当一次发送很多条聊天记录的时候。
3. 数据库还是存在较多冗余。如果用户也用`id`来唯一标识的话，私聊和群聊的格式就可以完全统一，并且用户名也可以重复、可以是特殊符号，少了很多限制。聊天记录实际上完全可以序列化成二进制存储，用户登录的时候直接取出来就可以发送，所以4个聊天记录表可以统一成一个。
4. 当同时登录的用户数目过多时，对于服务端，`select`需要不断在内核和用户空间之间复制文件描述符，以及遍历整个文件描述符表，这些操作代价会很高。

未来的工作：

1. 目前本地聊天记录还未实现。离线消息保存在服务端，本来发送出去之后应该删掉，但现在暂时还保留着。
2. 在群聊窗口中添加一个邀请好友的按钮。这个功能对应的数据包、事件处理实际上都有，只是没有按钮来触发这个事件而已。
3. 完善界面排版。目前界面对不同分辨率屏幕的适应不好，导致排版有些错乱。
4. 删除会话和退出群聊功能。
5. 优化消息格式，尽量把冗余降低。
6. 优化数据库模式。

----

[1] https://github.com/KevinWang15/network-pj-chatroom 前期框架搭建参考

[2] https://stackoverflow.com/questions/16188420/tkinter-scrollbar-for-frame 垂直滚动条组件

[3] https://stackoverflow.com/questions/8730927/convert-python-long-int-to-fixed-size-byte-arra 长整数转字节



