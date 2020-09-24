import sys

from doctester import color
from doctester import defaults


class Log:
    def __init__(self, config):
        self.config = config

    def info(self, *args, **kwargs):
        if not self.config.quiet:
            print(*args, **kwargs)

    def error(self, message):
        sys.exit(color.red("%s: Error: %s" % (defaults.name, message)))

    def debug(self, *args):
        if self.config.debug:
            colors = {
                "OTHER": "yellow",
                "COMMA": "magenta",
                "OUTPU": "cyan",
                "PROMP": "green",
            }
            color_function = getattr(color, colors[args[0]])
            print(color_function("----" + " ".join(str(x) for x in args)))
