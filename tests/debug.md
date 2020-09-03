# Option --debug

When using the debug mode, extra messages are shown in specific points during the parsing of the original test file and during test execution. The idea is having a "behind the curtains" view of the process, hopefully allowing us to easily find bugs.

> For this one we will run the tests from `tests/status.md`, which should be a somewhat stable file (won't change too much in the future) and have diverse enough lines (command, output, other) to produce a rich debug result.

    > ./doctest.fish --debug tests/status.md
    Line 1: ? [To test the exit status for specific commands, just show `$status` after the commands, **in the same command line**.]
    Line 1: OTHER [To test the exit status for specific commands, just show `$status` after the commands, **in the same command line**.]
    Line 2: ? []
    Line 2: OTHER []
    Line 3: ? [    > true; echo $status]
    Line 3: COMMAND [true; echo $status]
    Line 4: ? [    0]
    Line 4: OUTPUT [0]
    Line 5: ? [    > false; echo $status]
    Line 5: COMMAND [false; echo $status]
    Line 6: ? [    1]
    Line 6: OUTPUT [1]
    Line 7: ? [    > echo "command output and status"; echo $status]
    Line 7: COMMAND [echo "command output and status"; echo $status]
    Line 8: ? [    command output and status]
    Line 8: OUTPUT [command output and status]
    Line 9: ? [    0]
    Line 9: OUTPUT [0]
    Line 10: ? []
    Line 10: OTHER []
    Line 11: ? [Using status in a different command line will not work. Note how it is reset back to zero:]
    Line 11: OTHER [Using status in a different command line will not work. Note how it is reset back to zero:]
    Line 12: ? []
    Line 12: OTHER []
    Line 13: ? [    > false]
    Line 13: COMMAND [false]
    Line 14: ? [    > echo $status  # DOES NOT WORK]
    Line 14: COMMAND [echo $status  # DOES NOT WORK]
    Line 15: ? [    0]
    Line 15: OUTPUT [0]
    Line 16: ? []
    Line 16: OTHER []
    tests/status.md: OK (5 tests passed)
