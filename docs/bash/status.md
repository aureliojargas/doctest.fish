# Exit status

To test the exit status for specific commands, just show `$?` after the commands, **in the same command line**.

    $ true; echo $?
    0
    $ false; echo $?
    1
    $ echo "command output and status"; echo $?
    command output and status
    0

Using status in a different command line will not work. Note how it is reset back to zero:

    $ false
    $ echo $?
    0
