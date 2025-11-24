import pymysql
import psycopg2
# import cx_Oracle
import sqlite3
from dbutils.pooled_db import PooledDB
from utils.my_decorators import singleton


@singleton
class SQLConnectionPool:

    def __init__(self, db_type, **kwargs):
        self.db_type = db_type.lower()
        self._pool = self._create_pool(**kwargs)

    def _create_pool(self, **kwargs):
        if self.db_type == 'mysql':
            creator = pymysql
            kwargs.setdefault('charset', 'utf8mb4')
        elif self.db_type == 'postgresql':
            creator = psycopg2
        # elif self.db_type == 'oracle':
        #     creator = cx_Oracle
        #     if 'host' in kwargs and 'port' in kwargs and ('sid' in kwargs or 'service_name' in kwargs):
        #         if 'sid' in kwargs:
        #             dsn = cx_Oracle.makedsn(kwargs.pop('host'), kwargs.pop('port'), sid=kwargs.pop('sid'))
        #         else:
        #             dsn = cx_Oracle.makedsn(kwargs.pop('host'), kwargs.pop('port'), service_name=kwargs.pop('service_name'))
        #         kwargs['dsn'] = dsn
        elif self.db_type == 'sqlite':
            creator = sqlite3
        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")

        return PooledDB(creator, **kwargs)

    def get_connection(self):
        return self._pool.connection()

    def execute(self, sql, params=None, fetch=None):
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql, params or ())
                if fetch == 'one':
                    return cursor.fetchone()
                elif fetch == 'all':
                    return cursor.fetchall()
                else:
                    conn.commit()
                    return cursor.rowcount
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def select(self, sql, params=None, fetch='all'):
        return self.execute(sql, params, fetch=fetch)

    def insert(self, sql, params=None):
        return self.execute(sql, params)

    def update(self, sql, params=None):
        return self.execute(sql, params)

    def delete(self, sql, params=None):
        return self.execute(sql, params)

    def close(self):
        self._pool.close()
