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

FLAG_DEBUG = 0


def setup_cmdline_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--prefix",
        metavar="PREFIX",
        default=" " * 4,
        help="set the command line prefix (default: 4 spaces)",
    )
    parser.add_argument(
        "--prompt",
        metavar="PROMPT",
        default="$ ",
        help="set the prompt string (default: '$ ')",
    )
    parser.add_argument(
        "--shell", choices=["bash", "fish"], default="bash", help="set the shell",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="rewrite the original file with current results",
    )
    parser.add_argument(
        "--color",
        metavar="WHEN",
        choices=["auto", "always", "yes", "never", "no"],
        default="auto",
        help="use colors or not? auto*, always, never",
    )
    parser.add_argument(
        "-q", "--quiet", action="store_true", help="no output is shown",
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
        if FLAG_DEBUG:
            colors = {
                "OTHER": "yellow",
                "COMMA": "magenta",
                "OUTPU": "cyan",
                "PROMP": "green",
            }
            print(
                self.colored(colors[args[0]], "----" + " ".join(str(x) for x in args))
            )


def validate_prompt(string):
    if not string:
        LOG.error("The prompt string cannot be empty, set it via --prompt")


def validate_input_files(paths):
    if not paths:
        LOG.error("no test file informed")

    for path in paths:
        if path.is_dir():
            LOG.error("input file is a directory: %s" % path)
        if not path.is_file():
            LOG.error("cannot read input file: %s" % path)


class ShellBase:
    def __init__(self, input_path=None, config=None):
        self.script = []
        self.config = config or {}
        self.input_path = input_path

    def quote(self, text):
        return shlex.quote(text)

    def echo(self, text):
        self.script.append("echo %s" % self.quote(text))

    def run_command(self, command):
        if self.config.prefix:
            self.run_command_and_add_prefix(command)
        else:
            self.script.append(command)

    def run_command_and_add_prefix(self, command):
        # must be implemented by each shell class
        pass

    def get_run_script_command(self):
        # must be implemented by each shell class
        pass

    def get_script_pre(self):
        # must be implemented by each shell class
        pass

    def get_script_post(self):
        # Always end with a successful silent command ("true"), so the
        # script execution will always return zero if it reached the
        # end. This avoids raising RuntimeError if the user enters a
        # failing command in the very last line of the input file.
        return ["true"]

    def get_script(self):
        return "\n".join(self.get_script_pre() + self.script + self.get_script_post())

    def run_script(self):
        """Regenerate the full document and save into self.output_path"""

        # Run the shell script that will generate the full document
        self.script_path = pathlib.Path(tempfile.mkstemp()[1])
        self.script_path.write_text(self.get_script())
        result = subprocess.run(
            self.get_run_script_command(),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )

        if result.returncode == 0:
            if FLAG_DEBUG:
                print("\nScript:", self.script_path)
            else:
                self.script_path.unlink()
        else:
            print(
                "Unexpected fatal error occurred:\n%s\n" % result.stdout,
                file=sys.stderr,
            )
            raise RuntimeError(
                "Failed running shell script to generate the document",
                str(self.script_path),
            )

        # Save the generated document
        self.output_path = pathlib.Path(tempfile.mkstemp()[1])
        self.output_path.write_text(result.stdout)

    def diff(self, left=None, right=None):
        left = left or self.input_path
        right = right or self.output_path
        return subprocess.run(
            ["diff", "-u", left, right],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )


class Bash(ShellBase):
    def get_run_script_command(self):
        return ["bash", self.script_path]

    def get_script_pre(self):
        return ["_doctester_tmp=$(mktemp)"]

    def run_command_and_add_prefix(self, command):
        # This restores the original prefix to the output lines
        sed_command = shlex.quote("s/^/%s/" % self.config.prefix.replace("/", "\\/"))
        # \n avoids breakage with "true #comment"
        # { ... ; } avoids breakage with "true >foo"
        # true; to avoid empty commands (i.e. comments-only) inside { ... }
        # >out; sed avoids a pipe | breaking some commands "a=1 | sed"
        self.script.append(
            "{ %s\ntrue; } >$_doctester_tmp 2>&1; sed %s $_doctester_tmp; rm $_doctester_tmp"
            % (command, sed_command)
            # XXX save the real $? state after the original command?
        )


class Fish(ShellBase):
    def get_run_script_command(self):
        return ["fish", self.script_path]

    def quote(self, text):
        # https://fishshell.com/docs/current/#quotes
        # The only backslash escape accepted within single quotes is \',
        # which escapes a single quote and \\, which escapes the
        # backslash symbol.
        return "'%s'" % text.replace("\\", "\\\\").replace("'", "\\'")

    def get_script_pre(self):
        return ["set _doctester_tmp (mktemp)"]

    def run_command_and_add_prefix(self, command):
        # This restores the original prefix to the output lines
        # \n avoids breakage with "true #comment"
        # { ... ; } avoids breakage with "true >foo"
        # >out; sed avoids a pipe | breaking some commands "a=1 | sed"
        self.script.append(
            "begin; %s\nend >$_doctester_tmp 2>&1; string replace -r '^' %s < $_doctester_tmp; rm $_doctester_tmp"
            % (command, shlex.quote(self.config.prefix))
        )


def main(config):

    if config.version:
        print(PROGRAM_NAME, __version__)
        sys.exit(0)

    validate_prompt(config.prompt)
    validate_input_files(config.files)

    if config.prefix == "tab":  # XXX document and unittest it
        config.prefix = "\t"

    prefix = config.prefix
    prompt = config.prompt

    command_id = prefix + prompt
    command_id_trimmed = command_id.rstrip(" ")

    # Pre-compute lengths and counts
    # prefix_length = len(prefix)
    command_id_length = len(command_id)
    # input_files_count = (count $input_files)

    total_failed = 0
    total_skipped = 0
    global_diff = []

    for input_path in config.files:
        LOG.info("%s:" % input_path, end=" ", flush=True)

        if FLAG_DEBUG:
            LOG.info("")

        if config.shell == "bash":
            shell = Bash(input_path, config)
        elif config.shell == "fish":
            shell = Fish(input_path, config)

        with input_path.open() as input_file:
            # parsed_data = []
            commands_count = 0
            pending_output = False
            for line_number, line in enumerate(input_file, start=1):
                line = re.sub(r"\r?\n$", "", line)

                if line.startswith(command_id):
                    # Found a command line
                    commands_count += 1
                    cmd = line[command_id_length:]
                    LOG.debug("COMMA", line_number, line)
                    shell.echo(line)
                    shell.run_command(cmd)
                    pending_output = True

                elif line == command_id or line == command_id_trimmed:
                    # Line has prompt, but it is an empty command
                    LOG.debug("PROMP", line_number, line)
                    pending_output = False
                    shell.echo(line)

                elif pending_output and line.startswith(prefix):
                    # Line has the prefix and is not a command, so this is the
                    # command output
                    LOG.debug("OUTPU", line_number, line)
                    # do nothing

                else:
                    # Line is not a command neither command output
                    # show_parsed_line $line_number other $line
                    LOG.debug("OTHER", line_number, line)
                    pending_output = False
                    shell.echo(line)
        if commands_count:
            LOG.info(
                "Found %d commands." % commands_count, end=" ", flush=True,
            )
            shell.run_script()
            diff = shell.diff()
            if diff.returncode == 0:
                LOG.info(LOG.colored("green", "PASSED"))
            else:
                # LOG.info()
                global_diff.append(diff.stdout)
                total_failed += 1

                if config.fix:
                    # mv new old
                    shell.input_path.write_text(shell.output_path.read_text())
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
