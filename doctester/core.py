import argparse

# import logging
import re
import sys
import pathlib

from doctester import color
from doctester import defaults
from doctester import log
from doctester import script
from doctester import util

LOG = None
# LOG.basicConfig(format="%(levelname)s:%(message)s", level=LOG.DEBUG)
# LOG.basicConfig(format="%(levelname)s:%(message)s", level=LOG.INFO)


def setup_cmdline_parser():
    parser = argparse.ArgumentParser(prog=defaults.name, description=__doc__)
    parser.add_argument(
        "--prefix",
        metavar="PREFIX",
        default=defaults.prefix,
        help="set the command line prefix (default: 4 spaces)",
    )
    parser.add_argument(
        "--prompt",
        metavar="PROMPT",
        default=defaults.prompt,
        help="set the prompt string (default: '%s')" % defaults.prompt,
    )
    parser.add_argument(
        "--shell",
        choices=defaults.shells,
        default=defaults.shell,
        help="set the shell (default: %s)" % defaults.shell,
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="rewrite the original file with current results",
    )
    parser.add_argument(
        "--color",
        choices=defaults.colors,
        default=defaults.color,
        help="use colors or not? (default: %s)" % defaults.color,
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


def validate_config(config):
    # color
    color.on = config.color in ("always", "yes") or (
        config.color == "auto" and sys.stdout.isatty()
    )

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
    skript = script.Script.factory(config)

    pending_output = False
    for line_number, line in enumerate(input_, start=1):
        line = re.sub(r"\r?\n$", "", line)

        if line.startswith(command_id):
            # Found a command line
            skript.command_count += 1
            cmd = line[command_id_length:]
            LOG.debug("COMMA", line_number, line)
            skript.echo(line)
            skript.eval(cmd)
            pending_output = True

        elif line == command_id or line == command_id_trimmed:
            # Line has prompt, but it is an empty command
            LOG.debug("PROMP", line_number, line)
            pending_output = False
            skript.echo(line)

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
            skript.echo(line)

    return skript


def main(config):
    global LOG

    LOG = log.Log(config)

    if config.version:
        print(defaults.name, defaults.version)
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
            skript = parse_input(input_fd, config)

        if skript.command_count:
            LOG.info(
                "Found %d commands." % skript.command_count, end=" ", flush=True,
            )

            # run
            run_result = skript.run()
            if run_result.returncode == 0:
                if config.debug:
                    print("\nScript:", util.save_temp_file(str(skript)))
            else:
                print(
                    "Unexpected fatal error occurred:\n%s\n" % run_result.stdout,
                    file=sys.stderr,
                )
                raise RuntimeError(
                    "Failed running shell script to generate the document",
                    str(util.save_temp_file(str(skript))),
                )

            # diff
            diff_result = util.diff(
                input_path, util.save_temp_file(util.list_as_text(skript.output))
            )
            if diff_result.returncode == 0:
                LOG.info(color.green("PASSED"))
            else:
                global_diff.append(diff_result.stdout)
                total_failed += 1

                if config.fix:
                    # mv new old
                    input_path.write_text(util.list_as_text(skript.output))
                    LOG.info(color.cyan("FIXED"))
                else:
                    LOG.info(color.red("FAILED"))
                    LOG.info()
                    LOG.info(diff_result.stdout)

        else:
            LOG.info(color.magenta("No commands found :("))
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
                    % (color.cyan("FIXED"), total_failed, nr_files)
                )
            else:
                LOG.info(
                    "[%s] %d of %d files have failed"
                    % (color.red("FAILED"), total_failed, nr_files)
                )
        else:
            LOG.info("[%s] %d files checked" % (color.green("PASSED"), nr_files))

    # if total_failed > 0:
    #     LOG.info()
    #     LOG.info("\n".join(global_diff))

    return total_failed == 0 and total_passed > 0
