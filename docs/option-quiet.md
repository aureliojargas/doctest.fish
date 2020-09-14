# Option --quiet (or -q)

When using the quiet mode, nothing is printed to stdout.

This may be useful in automation, when only the exit status will tell if the tests have passed or not:

    > ./doctest.fish --quiet docs/include/one-ok.md; echo $status
    0
    > ./doctest.fish --quiet docs/include/one-fail.md; echo $status
    1

Note that even in the quiet mode, error messages are still shown:

    > ./doctest.fish -q /
    doctest.fish: Error: input file is a directory: /
