import io
import sys
import unittest


import doctester


class TestX(unittest.TestCase):  # XXX fix name
    def test_syntax_error(self):
        shell = doctester.Bash()
        shell.script = ['echo "']

        # Silencing stderr to avoid pollution in the test run output
        with self.assertRaises(RuntimeError):
            stderr_orig = sys.stderr
            sys.stderr = io.StringIO()
            shell.run_script()
            sys.stderr = stderr_orig

    def test_quote_fish(self):
        shell = doctester.Fish()
        self.assertEqual(shell.quote("abc"), "'abc'")
        self.assertEqual(shell.quote("a'c"), "'a\\'c'")
        self.assertEqual(shell.quote("a\\c"), "'a\\\\c'")
        self.assertEqual(shell.quote("'\\'"), "'\\'\\\\\\''")


if __name__ == "__main__":
    unittest.main()
