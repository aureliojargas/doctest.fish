Each test file should have its own pristine environment when running the tests.

Variables defined in one test file should not spillover to other test files. See `tests/variables-1.md`.

    > echo -n $var_from_variables_1
    >
