# Option --quiet

When using the quiet mode, nothing should be printed to stdout in a normal run. Only the exit status will tell if the tests have passed or not:

    > ./doctest.fish -q tests/include/one-ok.md; echo $status
    0

Failed tests also won't be printed, but the exit status 1 will signal that one or more tests have failed:

    > ./doctest.fish -q tests/include/one-fail.md; echo $status
    1

Usage error messages are still shown even in quiet mode:

    > ./doctest.fish --quiet /
    doctest.fish: Error: input file is a directory: /
