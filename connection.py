import pymysql.cursors

conn = pymysql.connect(host='localhost',
                       user='root',
                       password='',
                       db='natural_cure',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)
