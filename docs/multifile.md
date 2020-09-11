# Multiple input files

When the program is called with two or more input files, a summary message is shown at the end, preceded by a blank line.

When no tests are found in any of the input files, it's probably the case that the prefix or the prompt used in the test files do not match the default values. Give a hint to the user that `--prefix` and/or `--prompt` can be used to fix this.

    > ./doctest.fish docs/no-tests-found.md{,}  | tail -n 2
    
    Summary: 2 input files, no tests were found (check --prefix and --prompt)

For passed/failed messages, use a format similar to that already used in the summary for each individual file.

Passed:

    > ./doctest.fish docs/include/one-ok.md{,} | tail -n 2
    
    Summary: 2 input files, 2 tests passed

Failed:

    > ./doctest.fish docs/include/one-fail.md{,} | tail -n 2
    
    Summary: 2 input files, 2 of 2 tests failed
