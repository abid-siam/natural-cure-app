import pymysql.cursors

conn = pymysql.connect(host='localhost',
                       user='user',
                       password='',
                       port=8889,
                       db='natural_cure',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)
