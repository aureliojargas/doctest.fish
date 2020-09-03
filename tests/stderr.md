Both stdout and stderr are captured when running the tests.

    > echo stdout; echo stderr >&2
    stdout
    stderr
    > fish -Y
    fish: invalid option -- Y
