import sys

from doctester import color
from doctester import defaults

# -1 = quiet
#  0 = normal
#  1 = verbose
#  2 = debug
level = 0  # pylint: disable=invalid-name


def info(*args, **kwargs):
    if level >= 0:
        print(*args, **kwargs)


def error(message):
    sys.exit(color.red("%s: Error: %s" % (defaults.name, message)))


def debug(*args):
    if level >= 2:
        colors = {
            "OTHER": "yellow",
            "COMMA": "magenta",
            "OUTPU": "cyan",
            "PROMP": "green",
        }
        color_function = getattr(color, colors[args[0]])
        print(color_function("----" + " ".join(str(x) for x in args)))
