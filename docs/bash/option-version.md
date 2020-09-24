# Option --version

Use `--version` to show the current version for this program:

    $ python3 -m doctester --version
    doctester 0.1.0

Note that the exit status for this operation is always zero:

    $ python3 -m doctester --version; echo $?
    doctester 0.1.0
    0
