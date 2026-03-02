import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from skills.data_sandbox.sandbox import DataSandbox


class TestDataSandbox(unittest.TestCase):

    def test_mock_execution(self):
        """In environments without pandas/numpy, mock mode should work."""
        sandbox = DataSandbox()
        result = sandbox.execute("print('hello world')")
        self.assertIn(result["status"], ("success", "success_mock"))
        self.assertEqual(result["exit_code"], 0)

    def test_simple_python_execution(self):
        """Should be able to execute basic Python code."""
        sandbox = DataSandbox()
        if sandbox._mock:
            self.skipTest("Running in mock mode — no pandas/numpy available")
        result = sandbox.execute("print(2 + 2)")
        self.assertEqual(result["status"], "success")
        self.assertIn("4", result["stdout"])

    def test_timeout_enforcement(self):
        """Should timeout long-running scripts."""
        sandbox = DataSandbox(timeout=2)
        if sandbox._mock:
            self.skipTest("Running in mock mode")
        result = sandbox.execute("import time; time.sleep(10)")
        self.assertEqual(result["status"], "timeout")

    def test_syntax_error_handling(self):
        """Should report errors for invalid Python code."""
        sandbox = DataSandbox()
        if sandbox._mock:
            self.skipTest("Running in mock mode")
        result = sandbox.execute("def bad syntax here")
        self.assertEqual(result["status"], "error")
        self.assertNotEqual(result["exit_code"], 0)


if __name__ == "__main__":
    unittest.main()
