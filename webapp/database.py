import constant
import pymysql.cursors


class Database:
    def connect(self):
        # Connect to the database
        connection = pymysql.connect(host=constant.DB_HOST,
                                     user=constant.DB_USER,
                                     password=constant.DB_PASSWORD,
                                     db=constant.DB_NAME,
                                     charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor,
                                     autocommit=True)

        if connection:
            return connection
        else:
            return None

    def create_record(self, connection, sql):
        with connection.cursor() as cursor:
            # Create a new record
            try:
                cursor.execute(sql)
            except pymysql.IntegrityError:
                pass

        # connection is not autocommit by default. So you must commit to save
        # your changes.
        connection.commit()

    def read_single_record(self, connection, sql):
        with connection.cursor() as cursor:
            # Read a single record
            cursor.execute(sql)
            result = cursor.fetchone()
            return result

    def read_all_records(self, connection, sql):
        with connection.cursor() as cursor:
            # Read a single record
            cursor.execute(sql)
            result = cursor.fetchall()
            return result

    def write_single_record(self, connection, sql):
        with connection.cursor() as cursor:
            # Write a single record
            cursor.execute(sql)
