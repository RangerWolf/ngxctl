# ./tests/test_top.py

import unittest
from click.testing import CliRunner
from ngxctl.cmds.top import top

class TestTopCommand(unittest.TestCase):

    def setUp(self):
        self.runner = CliRunner()

    # def test_top_command(self):
    #     # 模拟运行 top 命令
    #     result = self.runner.invoke(top, ['--conf', '/path/to/nginx.conf'])
    #     self.assertEqual(result.exit_code, 0)
    #     # self.assertIn("Expected output", result.output)  # 替换 "Expected output" 为你的预期输出

    def test_top_command_with_invalid_conf(self):
        # 测试传入无效配置文件的情况
        result = self.runner.invoke(top, ['--conf', '/invalid/path/nginx.conf'])
        self.assertEqual(result.exit_code, 1)
        # self.assertIn("Configuration file not found", result.output)

if __name__ == '__main__':
    unittest.main()
