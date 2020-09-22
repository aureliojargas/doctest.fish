# Input file

You can use any text format as the input file, such as Markdown, reST, HTML, LaTeX, plain text. The only requirement is that the command lines and properly prefixed (see [--prefix](option-prefix.md)) and use the expected prompt identifier (see [--prompt](option-prompt.md)).

Informing [multiple files as input](multifile.md) is also supported.


## Input file checks

No input file informed:

    $ ./doctester.py
    doctester: Error: no test file informed

Input file not found:

    $ ./doctester.py /404-foo-bar
    doctester: Error: cannot read input file: /404-foo-bar

Input file is a directory:

    $ ./doctester.py /
    doctester: Error: input file is a directory: /
