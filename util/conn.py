import mysql.connector
from mysql.connector import Error


# MySQL 配置
db_config = {
    "user": "root",
    "password": "741953",
    "host": "127.0.0.1",
    "database": "submitreview",
}

# 连接库
def get_db_connection():
    connection = None
    try:
        connection = mysql.connector.connect(**db_config)
        print("成功连接到数据库!")
    except Error as e:
        print(f"数据库连接失败: {e}")
    return connection, connection.cursor()

def close_connection(conn, cursor):
    try:
        conn.commit()
        cursor.close()
        conn.close()
        print("释放连接成功")
    except Error as e:
        print(f"数据库释放失败: {e}")
        
        

__all__ = ['get_db_connection', 'close_connection']

# 暴露接口（模块级别）
# 显式声明了 all  import * 就只会导入 all 列出的成员