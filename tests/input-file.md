No input file informed:

    > ./doctest.fish
    doctest.fish: Error: no test file informed

Input file not found:

    > ./doctest.fish /404-foo-bar
    doctest.fish: Error: cannot read input file: /404-foo-bar

Input file is a directory:

    > ./doctest.fish /
    doctest.fish: Error: input file is a directory: /
