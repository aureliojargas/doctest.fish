# Variables (part 1)

A variable defined in one test should be available for the next tests.

    $ x=1
    $ echo $x
    1

Even if we have different sessions inside the same file.

    $ echo $x
    1

Undefined variables are not a problem.

    $ unset x
    $ printf "$x"
    $

Variables defined in one test file should not spillover to other test files. See `docs/variables-2.md`.

    $ var_from_variables_1=here
    $ echo $var_from_variables_1
    here
