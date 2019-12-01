'''
查询数据库
'''
import sqlite3

conn = sqlite3.connect('../database.db', isolation_level=None)  #每一次修改数据库都是立即写入，速度慢，但是保证不出现并发错误；想加快速度可以用#BEGIN TRANSACTION COMMIT

