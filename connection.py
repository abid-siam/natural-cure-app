import pymysql.cursors

conn = pymysql.connect(host='localhost',
                       port= 8889,
                       user='root',
                       password='root',
                       db='natural-cure-app',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)
