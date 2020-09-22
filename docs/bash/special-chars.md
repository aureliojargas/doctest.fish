# Special chars

Tests to make sure that characters which are special to bash won't get mangled during the doctester.py processing.

> Important: This file contains literal tabs. Keep it that way.

Quoted escapes:

    $ printf "a\tb\nc"; echo
    a	b
    c
    $ printf "a\\tb\\nc"; echo
    a	b
    c
    $ printf "a\\\tb\\\nc"; echo
    a\tb\nc
    $ printf "a\\\\tb\\\\nc"; echo
    a\tb\nc

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
