Both stdout and stderr are captured when running the tests.

    > echo stdout; echo stderr >&2
    stdout
    stderr
    > fish foo
    foo: No such file or directory
