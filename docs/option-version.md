# Option --version

Use `--version` to show the current version for this program:

    > ./doctest.fish --version
    doctest.fish dev

Note that the exit status for this operation is always zero:

    > ./doctest.fish --version; echo $status
    doctest.fish dev
    0
