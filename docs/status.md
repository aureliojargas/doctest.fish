To test the exit status for specific commands, just show `$status` after the commands, **in the same command line**.

    > true; echo $status
    0
    > false; echo $status
    1
    > echo "command output and status"; echo $status
    command output and status
    0

Using status in a different command line will not work. Note how it is reset back to zero:

    > false
    > echo $status
    0
