# Special chars

Tests to make sure that characters which are special to fish won't get mangled during the doctester.py processing.

> Important: This file contains literal tabs. Keep it that way.

Unquoted escapes:

    $ echo a\tb\nc
    a	b
    c
    $ echo a\\tb\\nc
    a\tb\nc
    $ echo a\\\tb\\\nc
    a\	b\
    c
    $ echo a\\\\tb\\\\nc
    a\\tb\\nc

Quoted escapes:

    $ echo "a\tb\nc"
    a\tb\nc
    $ echo "a\\tb\\nc"
    a\tb\nc
    $ echo "a\\\tb\\\nc"
    a\\tb\\nc
    $ echo "a\\\\tb\\\\nc"
    a\\tb\\nc

Literal tab in the command:

    $ echo a	b
    a b
    $ echo "a	b"
    a	b

Literal quotes:

    $ echo \"a\'b
    "a'b
    $ echo "\"a'b"
    "a'b
    $ echo '"a\'b'
    "a'b
