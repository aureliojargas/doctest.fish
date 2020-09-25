import argparse
import pathlib
import subprocess
import tempfile


def diff(left, right):
    return subprocess.run(
        ["diff", "-u", left, right],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        check=False,
    )


def save_temp_file(contents):
    path = pathlib.Path(tempfile.mkstemp()[1])
    path.write_text(contents)
    return path


def list_as_text(list_):
    return "\n".join(list_) + "\n"  # ensure \n at EOF


def swap_ns_dict(thing):
    if isinstance(thing, argparse.Namespace):
        return vars(thing).copy()
    return argparse.Namespace(**thing)
