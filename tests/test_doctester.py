import io
import sys
import unittest

from context import doctester

# o ideal seria testar tudo com e sem prefix. Talvez seja viável fazer isso nos testes via Python
# se sim, a doc pode ser uma doc mesmo, e não uma suite de testes
# a doc pode ser simplificada
# os testes python devem ser testes full, tipo os atuais, em vez de ser unit e testar só uma função. ou ter ambos.
# posso ter templates para os testes (sem indent) e e aplicar ou não o indent ao ler estes templates, inclusive indent diferentes como tab
# cada template é isolado (um único tipo de teste) e posso combinar templates pra fazer um test case mais extenso
# e tem também a variação pra cada shell nestes templates (setar var)


class Config:
    def __init__(
        self,
        shell=doctester.Defaults.shell,
        prefix=doctester.Defaults.prefix,
        prompt=doctester.Defaults.prompt,
    ):
        self.shell = shell
        self.prefix = prefix
        self.prompt = prompt
        self.color = doctester.Defaults.color
        self.debug = False


class Template:
    STATUS = {"bash": "$?", "fish": "$status"}

    def __init__(self, shell=None, prefix=None, prompt=None):
        defaults = Config()
        self.shell = shell or defaults.shell
        self.prefix = prefix or defaults.prefix
        self.prompt = prompt or defaults.prompt
        self.status = Template.STATUS[self.shell]

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

    # Ter testes pro parser, todas as combinações
    # Ter testes pro executor e suas pegadinhas

    def test_status(self):
        config = Config()
        for shell in doctester.Defaults.shells:
            config.shell = shell
            t = Template(shell=shell)
            runner = doctester.ScriptRunner(config=config)
            doc = [
                t.cmd_with_status("true"),
                t.out("0"),
                t.cmd_with_status("false"),
                t.out("1"),
                t.cmd_with_status(t.echo("command output and status")),
                t.out("command output and status"),
                t.out("0"),
                t.cmd("false"),
                t.cmd(t.echo(t.status)),
                t.out("0"),
            ]
            # doctester.parse_input(doc, script)
            _, script = doctester.parse_input(
                doc, config.prefix, config.prompt, config.shell
            )
            runner.run_script(script, shell)
            self.assertEqual(runner.output, doc)

    def test_set_read_var(self):
        config = Config()
        for shell in doctester.Defaults.shells:
            config.shell = shell
            t = Template(shell=shell)
            runner = doctester.ScriptRunner(config=config)
            doc = [
                t.cmd(t.set_var("foo", "bar")),
                t.cmd(t.echo("$foo")),
                t.out("bar"),
            ]
            _, script = doctester.parse_input(
                doc, config.prefix, config.prompt, config.shell
            )
            runner.run_script(script, shell)
            self.assertEqual(runner.output, doc)

    def test_syntax_error(self):
        script = doctester.BashScript()
        script.script = ['echo "']
        runner = doctester.ScriptRunner(Config())

        # Silencing stderr to avoid pollution in the test run output
        with self.assertRaises(RuntimeError):
            stderr_orig = sys.stderr
            sys.stderr = io.StringIO()
            runner.run_script(str(script), "bash")
            sys.stderr = stderr_orig

    def test_quote_fish(self):
        script = doctester.FishScript()
        self.assertEqual(script.quote("abc"), "'abc'")
        self.assertEqual(script.quote("a'c"), "'a\\'c'")
        self.assertEqual(script.quote("a\\c"), "'a\\\\c'")
        self.assertEqual(script.quote("'\\'"), "'\\'\\\\\\''")


doctester.LOG = doctester.Log(Config())

if __name__ == "__main__":
    unittest.main()
