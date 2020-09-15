# Option --verbose (or -v)

By default, only a single line with a summary message is shown for each tested file, when all the tests pass:

    > ./doctest.fish docs/status.md
    docs/status.md: 5 tests PASSED

When using the verbose mode, extra messages are shown, listing all the executed tests:

    > ./doctest.fish --verbose docs/status.md
    docs/status.md:5: [ ok ] true; echo $status
    docs/status.md:7: [ ok ] false; echo $status
    docs/status.md:9: [ ok ] echo "command output and status"; echo $status
    docs/status.md:15: [ ok ] false
    docs/status.md:16: [ ok ] echo $status
    docs/status.md: 5 tests PASSED

## Verbosity level 2

The `--verbose` option is cumulative, so using it twice (`-v -v`) increases the output verbosity even more:

    > ./doctest.fish -v -v docs/status.md
    Parsing file docs/status.md
    Parsing finished, 10 command/output lines found
    Testing commands from file docs/status.md
    Running [true; echo $status], expecting [0]
    docs/status.md:5: [ ok ] true; echo $status
    Running [false; echo $status], expecting [1]
    docs/status.md:7: [ ok ] false; echo $status
    Running [echo "command output and status"; echo $status], expecting [command output and status\n0]
    docs/status.md:9: [ ok ] echo "command output and status"; echo $status
    Running [false], expecting []
    docs/status.md:15: [ ok ] false
    Running [echo $status], expecting [0]
    docs/status.md:16: [ ok ] echo $status
    docs/status.md: 5 tests PASSED
    Testing finished for file docs/status.md

## Verbosity level 3

There's also the third level of verbosity, showing information about the parsing of the input file and the processing of test data. It's probably too much information, but it may help to spot problems in desperate times.

    > ./doctest.fish -vvv docs/status.md
    Parsing file docs/status.md
       1 other   [# Exit status]
       2 other   []
       3 other   [To test the exit status for specific commands, just show `$status` after the commands, **in the same command line**.]
       4 other   []
       5 command [true; echo $status]
       6 output  [0]
       7 command [false; echo $status]
       8 output  [1]
       9 command [echo "command output and status"; echo $status]
      10 output  [command output and status]
      11 output  [0]
      12 other   []
      13 other   [Using status in a different command line will not work. Note how it is reset back to zero:]
      14 other   []
      15 command [false]
      16 command [echo $status]
      17 output  [0]
      18 other   []
    Parsing finished, 10 command/output lines found
    Testing commands from file docs/status.md
      [5:cmd:true; echo $status]
      [6:out:0]
      [7:cmd:false; echo $status]
    Running [true; echo $status], expecting [0]
    docs/status.md:5: [ ok ] true; echo $status
      [8:out:1]
      [9:cmd:echo "command output and status"; echo $status]
    Running [false; echo $status], expecting [1]
    docs/status.md:7: [ ok ] false; echo $status
      [10:out:command output and status]
      [11:out:0]
      [15:cmd:false]
    Running [echo "command output and status"; echo $status], expecting [command output and status\n0]
    docs/status.md:9: [ ok ] echo "command output and status"; echo $status
      [16:cmd:echo $status]
    Running [false], expecting []
    docs/status.md:15: [ ok ] false
      [17:out:0]
      [0:cmd:]
    Running [echo $status], expecting [0]
    docs/status.md:16: [ ok ] echo $status
    docs/status.md: 5 tests PASSED
    Testing finished for file docs/status.md

> Note: You can use the long `--verbose --verbose --verbose`, the short `-v -v -v` or the shorter `-vvv`.

## Failed tests are always verbose

Note that failed tests are always shown by default, even when not using the verbose mode:

    > ./doctest.fish docs/include/one-fail.md
    
    docs/include/one-fail.md:1: [fail] echo foo
    @@ -1 +1 @@
    -bar
    +foo
    
    docs/include/one-fail.md: 1 of 1 tests FAILED
