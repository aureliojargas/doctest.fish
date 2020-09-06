# Option --color

Test the valid values for the `--color` option:

- `auto` (the default)
- `always` or `yes`
- `never` or `no`

The easier to test is `--color never`, we just have plain text in the output:

    > ./doctest.fish --color never tests/include/one-ok.md
    tests/include/one-ok.md: 1 tests PASSED
    > ./doctest.fish --color no tests/include/one-ok.md
    tests/include/one-ok.md: 1 tests PASSED

Since we're running the automated tests, the output is not a terminal, so `--color auto` won't use colors in this case:

    > ./doctest.fish --color auto tests/include/one-ok.md
    tests/include/one-ok.md: 1 tests PASSED

Now forcing colored output with `--color always`.

    > ./doctest.fish --color always tests/include/one-ok.md 2>&1 | tr -d '\033' | sed 's/(B//'
    tests/include/one-ok.md: 1 tests [32mPASSED[m
    > ./doctest.fish --color yes tests/include/one-ok.md 2>&1 | tr -d '\033' | sed 's/(B//'
    tests/include/one-ok.md: 1 tests [32mPASSED[m

> Note that `tr -d '\033'` was used to remove the invisible escape char from the output. This breaks the colored output, but that's ok, we only want to match plain text here and check if the colors were used or not.

> Note also that an extra `sed` command is used to remove an extra `(B` that appears before `[m` in some terminals (i.e.: `xterm-256color`).

Using and invalid value for the `--color` option will produced a non-colored error message:

    > ./doctest.fish --color 404 tests/include/one-ok.md
    doctest.fish: Error: Invalid --color mode '404'. Use: auto, always or never.
