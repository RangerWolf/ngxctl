import sqlite3
import time
import logging
from contextlib import closing
import tabulate

# This is copied from ngxtop

# =================================
# Records and statistic processor
# =================================
class SQLProcessor(object):
    def __init__(self, report_queries, fields, index_fields=None):
        self.begin = False
        self.report_queries = report_queries
        self.index_fields = index_fields if index_fields is not None else []
        self.column_list = ','.join(fields)
        self.holder_list = ','.join(':%s' % var for var in fields)
        self.conn = sqlite3.connect(':memory:')
        self.begin = time.time()
        # 多线程之中，可以相互共享
        #self.conn = sqlite3.connect('file::memory:?cache=shared', uri=True, check_same_thread=False)

        self.init_db()

    def process(self, records):
        insert = 'insert into log (%s) values (%s)' % (self.column_list, self.holder_list)
        # print("---- insert:", insert)
        logging.info('sqlite insert: %s', insert)
        with closing(self.conn.cursor()) as cursor:
            for r in records:
                # print("---- r=", r)
                cursor.execute(insert, r)

    def query(self, sql):
        with closing(self.conn.cursor()) as cursor:
            cursor.execute(sql)
            columns = (d[0] for d in cursor.description)
            result = tabulate.tabulate(cursor.fetchall(), headers=columns, tablefmt='orgtbl', floatfmt='.3f')
            return result

    def report(self):
        if not self.begin:
            return ''
        count = self.count()
        duration = time.time() - self.begin
        status = 'running for %.0f seconds, %d records processed: %.2f req/sec'
        output = [status % (duration, count, count / duration)]
        with closing(self.conn.cursor()) as cursor:
            for query in self.report_queries:
                if isinstance(query, tuple):
                    label, query = query
                else:
                    label = ''
                cursor.execute(query)
                columns = (d[0] for d in cursor.description)
                result = tabulate.tabulate(cursor.fetchall(), headers=columns, tablefmt='orgtbl', floatfmt='.3f')
                output.append('%s\n%s' % (label, result))
        return '\n\n'.join(output)

    def init_db(self):
        create_table = 'create table if not exists log (%s)' % self.column_list
        with closing(self.conn.cursor()) as cursor:
            cursor.execute('DROP TABLE IF EXISTS log')

            logging.info('sqlite init: %s', create_table)
            cursor.execute(create_table)
            for idx, field in enumerate(self.index_fields):
                sql = 'create index log_idx%d on log (%s)' % (idx, field)
                logging.info('sqlite init: %s', sql)
                cursor.execute(sql)

    def count(self):
        with closing(self.conn.cursor()) as cursor:
            cursor.execute('select count(1) from log')
            return cursor.fetchone()[0]