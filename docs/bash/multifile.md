# Multiple input files

Use bash's glob to test all the files under a directory. For example, to test all the Markdown files in the `docs` directory:

    ./doctester.py docs/*.md

When the program is called with two or more [input files](input-file.md), a global summary message is shown at the end, preceded by a blank line.

## Passed or failed tests

When all the tests have passed, or some tests have failed, the global summary message will use a format similar to that already used in the summary for each individual file.

Tests passed:

    $ ./doctester.py docs/include/one-ok.md{,} | tail -n 2
    
    Summary: [PASSED] 2 files checked

Tests failed:

    $ ./doctester.py docs/include/one-fail.md{,} | tail -n 2
    
    Summary: [FAILED] 2 of 2 files have failed

## No commands found :(

When no tests are found in any of the input files, it's probably the case that the prefix or the prompt used in the test files do not match the default values. Give a hint to the user that [--prefix](option-prefix.md) and/or [--prompt](option-prompt.md) can be used to fix this.

    $ ./doctester.py docs/bash/no-tests-found.md{,}  | tail -n 2
    
    Summary: 2 files checked, but no commands were found (check --prefix and --prompt)
