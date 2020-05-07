import pymysql.cursors

conn = pymysql.connect(host='localhost',
                       user='root',
                       password='root',
                       port=8889,
                       db='natural-cure-app',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)
