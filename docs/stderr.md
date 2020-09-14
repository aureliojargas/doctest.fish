# Error output (stderr)

When running the tests, doctest.fish captures both stdout and stderr so it can properly match the results.

## stderr-only

You can test the error output from commands, no need to mess with redirection:

    > fish foo
    foo: No such file or directory

You can also test both the error output and the exit status, by appending a new command to show the value of `$status` in the same test:

    > fish foo; echo $status
    foo: No such file or directory
    127

## stdout and stderr

Exactly as when executing the command in the interactive command line, unless redirected, both stdout and stderr appear together as the command output, with no distinction on which is which.

    > echo this is stdout; echo this is stderr >&2
    this is stdout
    this is stderr
