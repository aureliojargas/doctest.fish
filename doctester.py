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

    def quote(self, text):
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
        return list_as_text(self.script + ["true"])

    def run(self):
        script_contents = str(self)
        result = subprocess.run(
            [self.executable()],
            universal_newlines=True,  # renamed to text= in py37
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            input=script_contents,  # must have \n in last line
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


def diff(left, right):
    return subprocess.run(
        ["diff", "-u", left, right],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
    )


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


def parse_input(input_, config):
    command_id = config.prefix + config.prompt
    command_id_trimmed = command_id.rstrip(" ")
    command_id_length = len(command_id)
    script = Script.factory(config)

    pending_output = False
    for line_number, line in enumerate(input_, start=1):
        line = re.sub(r"\r?\n$", "", line)

        if line.startswith(command_id):
            # Found a command line
            script.command_count += 1
            cmd = line[command_id_length:]
            LOG.debug("COMMA", line_number, line)
            script.echo(line)
            script.eval(cmd)
            pending_output = True

        elif line == command_id or line == command_id_trimmed:
            # Line has prompt, but it is an empty command
            LOG.debug("PROMP", line_number, line)
            pending_output = False
            script.echo(line)

        elif pending_output and line.startswith(config.prefix):
            # Line has the prefix and is not a command, so this is the
            # command output
            LOG.debug("OUTPU", line_number, line)
            # do nothing

        else:
            # Line is not a command neither command output
            # show_parsed_line $line_number other $line
            LOG.debug("OTHER", line_number, line)
            pending_output = False
            script.echo(line)

    return script


def swap_ns_dict(x):
    if isinstance(x, argparse.Namespace):
        return vars(x).copy()
    return argparse.Namespace(**x)


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

        with input_path.open() as input_fd:
            script = parse_input(input_fd, config)

        if script.command_count:
            LOG.info(
                "Found %d commands." % script.command_count, end=" ", flush=True,
            )

            # run
            run_result = script.run()
            if run_result.returncode == 0:
                if config.debug:
                    print("\nScript:", save_temp_file(str(script)))
            else:
                print(
                    "Unexpected fatal error occurred:\n%s\n" % run_result.stdout,
                    file=sys.stderr,
                )
                raise RuntimeError(
                    "Failed running shell script to generate the document",
                    str(save_temp_file(str(script))),
                )

            # diff
            diff_result = diff(input_path, save_temp_file(list_as_text(script.output)))
            if diff_result.returncode == 0:
                LOG.info(LOG.colored("green", "PASSED"))
            else:
                global_diff.append(diff_result.stdout)
                total_failed += 1

                if config.fix:
                    # mv new old
                    input_path.write_text(list_as_text(script.output))
                    LOG.info(LOG.colored("cyan", "FIXED"))
                else:
                    LOG.info(LOG.colored("red", "FAILED"))
                    LOG.info()
                    LOG.info(diff_result.stdout)

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
