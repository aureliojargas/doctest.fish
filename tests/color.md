# Option --color

Test the valid values for the `--color` option:

- `auto` (the default)
- `always` or `yes`
- `never` or `no`

The easier to test is `--color never`, we just have plain text in the output:

    > ./doctest.fish --color never tests/include/one-ok.md
    tests/include/one-ok.md: OK (1 tests passed)
    > ./doctest.fish --color no tests/include/one-ok.md
    tests/include/one-ok.md: OK (1 tests passed)

Since we're running the automated tests, the output is not a terminal, so `--color auto` won't use colors in this case:

    > ./doctest.fish --color auto tests/include/one-ok.md
    tests/include/one-ok.md: OK (1 tests passed)

Now forcing colored output with `--color always`.

    > ./doctest.fish --color always tests/include/one-ok.md 2>&1 | tr -d '\033'
    tests/include/one-ok.md: [32mOK (1 tests passed)
    (B[m
    > ./doctest.fish --color yes tests/include/one-ok.md 2>&1 | tr -d '\033'
    tests/include/one-ok.md: [32mOK (1 tests passed)
    (B[m

> Note that `tr -d '\033'` was used to remove the invisible escape char from the output. This breaks the colored output, but that's ok, we only want to match plain text here and check if the colors were used or not.

Using and invalid value for the `--color` option will produced a non-colored error message:

    > ./doctest.fish --color 404 tests/include/one-ok.md
    doctest.fish: Error: Invalid --color mode '404'. Use: auto, always or never.
