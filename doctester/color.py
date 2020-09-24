# Usage:
# >>> import color
# >>> color.green("colored")
# >>> color.on = False
# >>> color.green("not colored")

on = True

codes = {
    "blue": "\x1b[34;1m",
    "cyan": "\x1b[36;1m",
    "green": "\x1b[32;1m",
    "magenta": "\x1b[35;1m",
    "red": "\x1b[31;1m",
    "yellow": "\x1b[33;1m",
    "reset": "\x1b[m",
}


def blue(text):
    return _maybe(text, "blue")


def cyan(text):
    return _maybe(text, "cyan")


def green(text):
    return _maybe(text, "green")


def magenta(text):
    return _maybe(text, "magenta")


def red(text):
    return _maybe(text, "red")


def yellow(text):
    return _maybe(text, "yellow")


def _maybe(text, color):
    return text if not on else codes[color] + text + codes["reset"]
