#!/usr/bin/env python3
# docchecker?
# checkdocs

import argparse
import re
import shlex
import sys
import pathlib
import subprocess
import tempfile

PROGRAM_NAME = "doctester"
__version__ = "0.1.0"


class Defaults:
    color = "auto"
    colors = ["auto", "always", "yes", "never", "no"]
    prefix = " " * 4
    prompt = "$ "
    shell = "bash"
    shells = ["bash", "fish"]


def setup_cmdline_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--prefix",
        metavar="PREFIX",
        default=Defaults.prefix,
        help="set the command line prefix (default: 4 spaces)",
    )
    parser.add_argument(
        "--prompt",
        metavar="PROMPT",
        default=Defaults.prompt,
        help="set the prompt string (default: '%s')" % Defaults.prompt,
    )
    parser.add_argument(
        "--shell",
        choices=Defaults.shells,
        default=Defaults.shell,
        help="set the shell (default: %s)" % Defaults.shell,
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="rewrite the original file with current results",
    )
    parser.add_argument(
        "--color",
        choices=Defaults.colors,
        default=Defaults.color,
        help="use colors or not? (default: %s)" % Defaults.color,
    )
    parser.add_argument(
        "-q", "--quiet", action="store_true", help="no output is shown",
    )
    parser.add_argument(
        "--debug", action="store_true", help="debug",  # XXX hide
    )
    parser.add_argument(
        "--version", action="store_true", help="show the program version and exit",
    )
    # files
    parser.add_argument(
        "files", metavar="FILE", type=pathlib.Path, nargs="*", help="input files"
    )
    return parser


class Log:
    COLORS = {
        "blue": "\033[34;1m",
        "cyan": "\033[36;1m",
        "green": "\033[32;1m",
        "magenta": "\033[35;1m",
        "red": "\033[31;1m",
        "yellow": "\033[33;1m",
        "reset": "\033[m",
    }

    def __init__(self, config):
        self.config = config
        self.use_colors = self._use_colors()

    def _use_colors(self):
        return self.config.color in ("always", "yes") or (
            self.config.color == "auto" and sys.stdout.isatty()
        )

    def info(self, *args, **kwargs):
        if not self.config.quiet:
            print(*args, **kwargs)

    def error(self, message):
        sys.exit(self.colored("red", "%s: Error: %s" % (PROGRAM_NAME, message)))

    def colored(self, color, text):
        if not self.use_colors:
            return text

        return Log.COLORS[color] + text + Log.COLORS["reset"]

    def debug(self, *args):
        if self.config.debug:
            colors = {
                "OTHER": "yellow",
                "COMMA": "magenta",
                "OUTPU": "cyan",
                "PROMP": "green",
            }
            print(
                self.colored(colors[args[0]], "----" + " ".join(str(x) for x in args))
            )


class ShellBase:
    OUTPUT_MARKER = "<doctester>".rjust(72, "-")

    def __init__(self, input_path=None, config=None, bin=None):
        self.bin = bin
        self.config = config
        self.input_path = input_path
        self.output = []
        self.script = []
        self.commands_found = 0

    @staticmethod
    def factory(*args, **kwargs):
        data = {"bash": Bash, "fish": Fish}
        return data[kwargs["config"].shell](*args, **kwargs)

    def quote(self, text):
        return shlex.quote(text)

    def echo(self, text):
        self.script.append("echo %s" % self.quote(text))

    def run_command(self, command):
        if self.config.prefix:
            self.echo(ShellBase.OUTPUT_MARKER)
            self.script.append(command)
            self.echo(ShellBase.OUTPUT_MARKER)
        else:
            self.script.append(command)

    def get_script(self):
        # Always end with a successful silent command ("true"), so the
        # script execution will always return zero if it reached the
        # end. This avoids raising RuntimeError if the user enters a
        # failing command in the very last line of the input file.
        return list_as_text(self.script + ["true"])

    def run_script(self):
        """Regenerate the full document and save into self.output list"""

        # Run the shell script that will generate the full document
        # ter dois paths (com e sem marker) pode trazer bugs em um deles,
        # o ideal seria testar tudo com e sem prefix. Talvez seja viável fazer isso nos testes via Python
        # se sim, a doc pode ser uma doc mesmo, e não uma suite de testes
        # a doc pode ser simplificada
        # os testes python devem ser testes full, tipo os atuais, em vez de ser unit e testar só uma função. ou ter ambos.
        # posso ter templates para os testes (sem indent) e e aplicar ou não o indent ao ler estes templates, inclusive indent diferentes como tab
        # cada template é isolado (um único tipo de teste) e posso combinar templates pra fazer um test case mais extenso
        # e tem também a variação pra cada shell nestes templates (setar var)

        result = subprocess.run(
            [self.bin],
            universal_newlines=True,  # renamed to text= in py37
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            input=self.get_script(),  # must have \n in last line
        )

        if result.returncode == 0:
            if self.config.debug:
                print("\nScript:", save_temp_file(self.get_script()))
        else:
            print(
                "Unexpected fatal error occurred:\n%s\n" % result.stdout,
                file=sys.stderr,
            )
            raise RuntimeError(
                "Failed running shell script to generate the document",
                str(save_temp_file(self.get_script())),
            )

        self.output = result.stdout.split("\n")[:-1]  # remove \n at EOF

        # Restore indentation in output blocks
        if self.config.prefix:
            in_output = False
            filtered_output = []
            for line in self.output:
                if line == ShellBase.OUTPUT_MARKER:
                    in_output = not in_output
                    continue  # remove marker from output
                if in_output:
                    line = self.config.prefix + line
                filtered_output.append(line)
            self.output = filtered_output

    def diff(self):
        left = self.input_path
        right = save_temp_file(list_as_text(self.output))
        return subprocess.run(
            ["diff", "-u", left, right],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )


class Bash(ShellBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, bin="bash", **kwargs)


class Fish(ShellBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, bin="fish", **kwargs)

    def quote(self, text):
        # https://fishshell.com/docs/current/#quotes
        # The only backslash escape accepted within single quotes is \',
        # which escapes a single quote and \\, which escapes the
        # backslash symbol.
        return "'%s'" % text.replace("\\", "\\\\").replace("'", "\\'")


def save_temp_file(contents):
    path = pathlib.Path(tempfile.mkstemp()[1])
    path.write_text(contents)
    return path


def list_as_text(list_):
    return "\n".join(list_) + "\n"  # ensure \n at EOF


def validate_config(config):
    # prefix
    if config.prefix == "tab":  # XXX document and unittest it
        config.prefix = "\t"

    # prompt
    if not config.prompt:
        LOG.error("The prompt string cannot be empty, set it via --prompt")

    # input files
    if not config.files:
        LOG.error("no test file informed")

    for path in config.files:
        if path.is_dir():
            LOG.error("input file is a directory: %s" % path)
        if not path.is_file():
            LOG.error("cannot read input file: %s" % path)


def parse_input(data, shell_handler):
    command_id = shell_handler.config.prefix + shell_handler.config.prompt
    command_id_trimmed = command_id.rstrip(" ")
    command_id_length = len(command_id)

    pending_output = False
    for line_number, line in enumerate(data, start=1):
        line = re.sub(r"\r?\n$", "", line)

        if line.startswith(command_id):
            # Found a command line
            shell_handler.commands_found += 1
            cmd = line[command_id_length:]
            LOG.debug("COMMA", line_number, line)
            shell_handler.echo(line)
            shell_handler.run_command(cmd)
            pending_output = True

        elif line == command_id or line == command_id_trimmed:
            # Line has prompt, but it is an empty command
            LOG.debug("PROMP", line_number, line)
            pending_output = False
            shell_handler.echo(line)

        elif pending_output and line.startswith(shell_handler.config.prefix):
            # Line has the prefix and is not a command, so this is the
            # command output
            LOG.debug("OUTPU", line_number, line)
            # do nothing

        else:
            # Line is not a command neither command output
            # show_parsed_line $line_number other $line
            LOG.debug("OTHER", line_number, line)
            pending_output = False
            shell_handler.echo(line)


def main(config):

    if config.version:
        print(PROGRAM_NAME, __version__)
        sys.exit(0)

    validate_config(config)

    total_failed = 0
    total_skipped = 0
    global_diff = []

    for input_path in config.files:
        LOG.info("%s:" % input_path, end=" ", flush=True)

        if config.debug:
            LOG.info("")

        shell_handler = ShellBase.factory(input_path=input_path, config=config)

        with input_path.open() as input_fd:
            parse_input(input_fd, shell_handler)

        if shell_handler.commands_found:
            LOG.info(
                "Found %d commands." % shell_handler.commands_found,
                end=" ",
                flush=True,
            )
            shell_handler.run_script()
            diff = shell_handler.diff()
            if diff.returncode == 0:
                LOG.info(LOG.colored("green", "PASSED"))
            else:
                global_diff.append(diff.stdout)
                total_failed += 1

                if config.fix:
                    # mv new old
                    shell_handler.input_path.write_text(
                        list_as_text(shell_handler.output)
                    )
                    LOG.info(LOG.colored("cyan", "FIXED"))
                else:
                    LOG.info(LOG.colored("red", "FAILED"))
                    LOG.info()
                    LOG.info(diff.stdout)

        else:
            LOG.info(LOG.colored("magenta", "No commands found :("))
            total_skipped += 1

    nr_files = len(config.files)
    total_passed = nr_files - total_failed - total_skipped
    if nr_files > 1:
        LOG.info()
        LOG.info("Summary:", end=" ")

        if total_passed == 0 and total_failed == 0:
            LOG.info(
                "%d files checked, but no commands were found (check --prefix and --prompt)"
                % nr_files
            )
        elif total_failed > 0:
            if config.fix:
                LOG.info(
                    "[%s] %d of %d files have been fixed"
                    % (LOG.colored("cyan", "FIXED"), total_failed, nr_files)
                )
            else:
                LOG.info(
                    "[%s] %d of %d files have failed"
                    % (LOG.colored("red", "FAILED"), total_failed, nr_files)
                )
        else:
            LOG.info(
                "[%s] %d files checked" % (LOG.colored("green", "PASSED"), nr_files)
            )

    # if total_failed > 0:
    #     LOG.info()
    #     LOG.info("\n".join(global_diff))

    return total_failed == 0 and total_passed > 0


if __name__ == "__main__":
    parser = setup_cmdline_parser()
    parsed_args = parser.parse_args()

    LOG = Log(parsed_args)
    passed = main(parsed_args)
    sys.exit(0 if passed else 1)
