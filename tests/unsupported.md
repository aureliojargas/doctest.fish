# Unsupported commands

## commandline

The `commandline` command is only available in interactive sessions. When trying to use it inside a script, this error is shown:

    commandline: Can not set commandline in non-interactive mode

Since documentation can contain examples of `commandline` usage and we cannot really test it, those commands are just skipped from testing.

    > commandline
    > commandline -t

## set -l

When defining a variable using `-l` or `--local` in the command line, you can access that variable normally in the following commands. The same is true inside a script, when the following commands are in the same scope.

Unfortunately, due the way doctest.fish works (using eval inside a loop to run the tests), the local scope is gone in each loop iteration, so each `set --local` variable is only valid for a single line in the test file.

To try to workaround that limitation, doctest.fish removes the `--local` option from the commands before executing them, making the variable accessible from the following tests (in the same test file).

    > set --local dash_dash_local 1
    > echo $dash_dash_local
    1
    > set -l dash_l 1
    > echo $dash_l
    1
