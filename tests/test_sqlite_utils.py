# ./tests/test_sqlite_utils.py

import unittest
from ngxctl.utils.sqlite_utils import SQLProcessor

class TestSQLProcessor(unittest.TestCase):

    def setUp(self):
        self.fields = ['field1', 'field2']
        self.index_fields = ['field1']
        self.records = [
            {'field1': 'value1', 'field2': 'value2'},
            {'field1': 'value3', 'field2': 'value4'}
        ]
        self.report_queries = ['SELECT * FROM log']
        self.sql_processor = SQLProcessor(self.report_queries, self.fields, self.index_fields)

    def test_init_db(self):
        # 测试数据库初始化是否正常
        count = self.sql_processor.count()
        self.assertEqual(count, 0)

    def test_process(self):
        # 测试插入记录是否成功
        self.sql_processor.process(self.records)
        count = self.sql_processor.count()
        self.assertEqual(count, len(self.records))

    def test_query(self):
        # 测试SQL查询功能是否正常
        self.sql_processor.process(self.records)
        result = self.sql_processor.query('SELECT * FROM log')
        self.assertIn('value1', result)
        self.assertIn('value2', result)

    def test_report(self):
        # 测试生成报告是否正常
        self.sql_processor.process(self.records)
        report = self.sql_processor.report()
        self.assertIn('running for', report)
        self.assertIn('value1', report)

if __name__ == '__main__':
    unittest.main()
