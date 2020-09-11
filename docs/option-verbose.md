# Option --verbose

By default, only a single line with a summary message is shown for each tested file, when all the tests pass:

    > ./doctest.fish docs/status.md
    docs/status.md: 5 tests PASSED

When using the verbose mode, extra messages are shown, listing all the executed tests:

    > ./doctest.fish --verbose docs/status.md
    docs/status.md:3: [ ok ] true; echo $status
    docs/status.md:5: [ ok ] false; echo $status
    docs/status.md:7: [ ok ] echo "command output and status"; echo $status
    docs/status.md:13: [ ok ] false
    docs/status.md:14: [ ok ] echo $status
    docs/status.md: 5 tests PASSED

Note that failed tests are always shown by default, even when not using the verbose mode:

    > ./doctest.fish docs/include/one-fail.md
    
    docs/include/one-fail.md:1: [fail] echo foo
    @@ -1 +1 @@
    -bar
    +foo
    
    docs/include/one-fail.md: 1 of 1 tests FAILED
