# Option --debug

When using the debug mode, extra messages are shown in specific points during the parsing of the original test file and during the test execution phase.

The idea is having a "behind the curtains" colored view of the whole process, hopefully helping doctest.fish developers to find problems.

## Hidden option

Since `--debug` is only meant to be used by doctest.fish developers, it is a "hidden" option, in the sense that it does not show up in the user-centric `--help` message:

    > ./doctest.fish --help | grep -- --debug
    >

## Output example

In the following example, [docs/status.md](status.md) is used as the test input file because it has diverse enough lines (command with no output, single line output, multiline output, non-test lines) to produce a rich debug result.

Note that `--verbose` is also used to get the most detailed output possible.

    > ./doctest.fish --debug --verbose docs/status.md
    Line 1: ? [# Exit status]
    Line 1: OTHER [# Exit status]
    Line 2: ? []
    Line 2: OTHER []
    Line 3: ? [To test the exit status for specific commands, just show `$status` after the commands, **in the same command line**.]
    Line 3: OTHER [To test the exit status for specific commands, just show `$status` after the commands, **in the same command line**.]
    Line 4: ? []
    Line 4: OTHER []
    Line 5: ? [    > true; echo $status]
    Line 5: COMMAND [true; echo $status]
    Line 6: ? [    0]
    Line 6: OUTPUT [0]
    Line 7: ? [    > false; echo $status]
    Line 7: COMMAND [false; echo $status]
    Line 8: ? [    1]
    Line 8: OUTPUT [1]
    Line 9: ? [    > echo "command output and status"; echo $status]
    Line 9: COMMAND [echo "command output and status"; echo $status]
    Line 10: ? [    command output and status]
    Line 10: OUTPUT [command output and status]
    Line 11: ? [    0]
    Line 11: OUTPUT [0]
    Line 12: ? []
    Line 12: OTHER []
    Line 13: ? [Using status in a different command line will not work. Note how it is reset back to zero:]
    Line 13: OTHER [Using status in a different command line will not work. Note how it is reset back to zero:]
    Line 14: ? []
    Line 14: OTHER []
    Line 15: ? [    > false]
    Line 15: COMMAND [false]
    Line 16: ? [    > echo $status]
    Line 16: COMMAND [echo $status]
    Line 17: ? [    0]
    Line 17: OUTPUT [0]
    Line 18: ? []
    Line 18: OTHER []
    [5:cmd:true; echo $status]
    [6:out:0]
    [7:cmd:false; echo $status]
    docs/status.md:5: [ ok ] true; echo $status
    [8:out:1]
    [9:cmd:echo "command output and status"; echo $status]
    docs/status.md:7: [ ok ] false; echo $status
    [10:out:command output and status]
    [11:out:0]
    [15:cmd:false]
    docs/status.md:9: [ ok ] echo "command output and status"; echo $status
    [16:cmd:echo $status]
    docs/status.md:15: [ ok ] false
    [17:out:0]
    [0:cmd:]
    docs/status.md:16: [ ok ] echo $status
    docs/status.md: 5 tests PASSED

For comparison, here's the default output, with debug and verbose modes turned off:

    > ./doctest.fish docs/status.md
    docs/status.md: 5 tests PASSED
