# Error output (stderr)

When running the tests, doctester.py captures both stdout and stderr so it can properly match the results.

## stderr-only

You can test the error output from commands, no need to mess with redirection:

    $ python3 -m doctester
    doctester: Error: no test file informed

You can also test both the error output and the exit status, by appending a new command to show the value of `$?` in the same test:

    $ python3 -m doctester; echo $?
    doctester: Error: no test file informed
    1

## stdout and stderr

Exactly as when executing the command in the interactive command line, unless redirected, both stdout and stderr appear together as the command output, with no distinction on which is which.

    $ echo this is stdout; echo this is stderr >&2
    this is stdout
    this is stderr
