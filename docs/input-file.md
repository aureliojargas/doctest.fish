# Input file

You can use any text format as the input file, such as Markdown, reST, HTML, LaTeX, plain text. The only requirement is that the command lines and properly prefixed (see [--prefix](option-prefix.md)) and use the expected prompt identifier (see [--prompt](option-prompt.md)).

Informing [multiple files as input](multifile.md) is also supported.


## Input file checks

No input file informed:

    > ./doctest.fish
    doctest.fish: Error: no test file informed

Input file not found:

    > ./doctest.fish /404-foo-bar
    doctest.fish: Error: cannot read input file: /404-foo-bar

Input file is a directory:

    > ./doctest.fish /
    doctest.fish: Error: input file is a directory: /
