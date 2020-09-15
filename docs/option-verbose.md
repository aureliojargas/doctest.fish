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

## Failed tests are always verbose

Note that failed tests are always shown by default, even when not using the verbose mode:

    > ./doctest.fish docs/include/one-fail.md
    
    docs/include/one-fail.md:1: [fail] echo foo
    @@ -1 +1 @@
    -bar
    +foo
    
    docs/include/one-fail.md: 1 of 1 tests FAILED
