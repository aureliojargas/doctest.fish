This file will run the tests for custom prefixes defined in `docs/include/custom-prefix.md`.

When not specifying a custom prefix, no test will be found:

    > ./doctest.fish --color no docs/include/custom-prefix.md
    docs/include/custom-prefix.md: No tests found

When using a custom prefix that is not found in the test file, it's ok:

    > ./doctest.fish --color no --prefix 404 docs/include/custom-prefix.md
    docs/include/custom-prefix.md: No tests found

Now set the tab as the prefix. Only one test is using that prefix:

    > ./doctest.fish --color no --prefix \t docs/include/custom-prefix.md
    docs/include/custom-prefix.md: 1 tests PASSED

Empty prefix is also valid for those cases when there's no indentation at all. For example, Markdown fenced blocks.

    > ./doctest.fish --color no --prefix '' docs/include/custom-prefix.md
    docs/include/custom-prefix.md: 1 tests PASSED
