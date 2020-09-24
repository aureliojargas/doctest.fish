# Option --quiet (or -q)

When using the quiet mode, nothing is printed to stdout.

This may be useful in automation, when only the exit status will tell if the tests have passed or not:

    $ python3 -m doctester --quiet docs/include/one-ok.md; echo $?
    0
    $ python3 -m doctester --quiet docs/include/one-fail.md; echo $?
    1

Note that even in the quiet mode, error messages are still shown:

    $ python3 -m doctester -q /
    doctester: Error: input file is a directory: /
