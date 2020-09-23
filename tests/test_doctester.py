import io
import sys
import unittest

from context import doctester


class Config(doctester.Defaults):
    debug = False


class Template:
    STATUS = {"bash": "$?", "fish": "$status"}

    def __init__(
        self, shell=Config.shell, prefix=Config.prefix, prompt=Config.prompt,
    ):
        self.shell = shell
        self.prefix = prefix
        self.prompt = prompt
        self.status = Template.STATUS[shell]

    def cmd(self, cmd):
        return self.prefix + self.prompt + cmd

    def cmd_with_status(self, cmd):
        return self.cmd(cmd) + self.echo_status()

    def out(self, text):
        return self.prefix + text

    def prompt_alone(self, cmd):
        return self.prefix + self.prompt.rstrip(" ")

    def lorem(self):
        return "Lorem ipsum."

    def set_var(self, name, value):
        if self.shell == "bash":
            return "%s=%s" % (name, value)
        elif self.shell == "fish":
            return "set %s %s" % (name, value)

    def echo(self, string):
        return "echo %s" % string

    def echo_status(self):
        return "; " + self.echo(self.status)

    def cmd_ok_one(self):
        return [self.cmd("echo foo"), self.out("foo")]

    def cmd_ok_two(self):
        return [self.cmd("printf 'a\nb'"), self.out("a"), self.out("b")]

    def cmd_fail_one(self):
        return [self.cmd("echo foo"), self.out("bar")]


class TestX(unittest.TestCase):  # XXX fix name
    def test_status(self):
        t = Template()
        shell = doctester.Bash(config=Config)
        doctester.LOG = doctester.Log(Config)
        doc = [
            t.lorem(),
            t.cmd_with_status("true"),
            t.out("0"),
            t.cmd_with_status("false"),
            t.out("1"),
            t.cmd_with_status(t.echo("command output and status")),
            t.out("command output and status"),
            t.out("0"),
            t.lorem(),
            t.cmd("false"),
            t.cmd(t.echo(t.status)),
            t.out("0"),
        ]
        doctester.parse_input(doc, shell)

    # def test_template(self):
    #     self.assertEqual(Template().cmd_ok_two(), "")
    #     self.assertEqual(Template().echo("$foo"), "")
    #     self.assertEqual(Template().set_var("foo", "bar"), "xxx")
    #     self.assertEqual(Template(shell="fish").set_var("foo", "bar"), "xxx")

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
