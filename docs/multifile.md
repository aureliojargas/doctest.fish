# Multiple input files

Use fish's glob to test all the files under a directory. For example, to test all the Markdown files in the `docs` directory, recursively:

    ./doctest.fish docs/**.md

When the program is called with two or more [input files](input-file.md), a global summary message is shown at the end, preceded by a blank line.

## Passed or failed tests

When all the tests have passed, or some tests have failed, the global summary message will use a format similar to that already used in the summary for each individual file.

Tests passed:

    > ./doctest.fish docs/include/one-ok.md{,} | tail -n 2
    
    Summary: 2 input files, 2 tests passed

Tests failed:

    > ./doctest.fish docs/include/one-fail.md{,} | tail -n 2
    
    Summary: 2 input files, 2 of 2 tests failed

## No tests found

When no tests are found in any of the input files, it's probably the case that the prefix or the prompt used in the test files do not match the default values. Give a hint to the user that [--prefix](option-prefix.md) and/or [--prompt](option-prompt.md) can be used to fix this.

    > ./doctest.fish docs/no-tests-found.md{,}  | tail -n 2
    
    Summary: 2 input files, no tests were found (check --prefix and --prompt)
