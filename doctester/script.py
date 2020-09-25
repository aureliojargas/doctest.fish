import shlex
import subprocess

from doctester import util

# The output for this parser is a valid shell script, that when
# executed, should recreate the original parsed document.
class Script:
    OUTPUT_MARKER = "<doctester>".rjust(72, "-")

    @staticmethod
    def factory(config):
        data = {"bash": BashScript, "fish": FishScript}
        return data[config.shell](config)

    def __init__(self, config):
        self.config = config
        self.script = []
        self.command_count = 0
        self.output = ""

    def executable(self):  # must be implemented in the children
        pass

    def quote(self, text):  # pylint: disable=no-self-use
        return shlex.quote(text)

    def echo(self, text):
        self.script.append("echo %s" % self.quote(text))

    def eval(self, text):
        self.echo(Script.OUTPUT_MARKER)
        self.script.append(text)
        self.echo(Script.OUTPUT_MARKER)

    def __str__(self):
        # Always end with a successful silent command ("true"), so the
        # script execution will always return zero if it reached the
        # end. This avoids raising RuntimeError if the user enters a
        # failing command in the very last line of the input file.
        return util.list_as_text(self.script + ["true"])

    def run(self):
        script_contents = str(self)
        result = subprocess.run(
            [self.executable()],
            universal_newlines=True,  # renamed to text= in py37
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            input=script_contents,  # must have \n in last line
            check=False,
        )
        self.output = self.fix_output(
            result.stdout.split("\n")[:-1]  # remove \n at EOF
        )
        return result

    # Restore indentation in command output blocks
    # Remove marker lines around command output
    def fix_output(self, text):
        must_indent = False
        filtered = []
        for line in text:
            if line == Script.OUTPUT_MARKER:
                must_indent = not must_indent
                continue  # remove marker
            if must_indent:
                line = self.config.prefix + line
            filtered.append(line)
        return filtered


class BashScript(Script):
    def executable(self):
        return "bash"


class FishScript(Script):
    def executable(self):
        return "fish"

    def quote(self, text):
        # https://fishshell.com/docs/current/#quotes
        # The only backslash escape accepted within single quotes is \',
        # which escapes a single quote and \\, which escapes the
        # backslash symbol.
        return "'%s'" % text.replace("\\", "\\\\").replace("'", "\\'")
