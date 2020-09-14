# Option --help (or -h)

Use `--help` to show the help message for this program, listing all the available options:

    > ./doctest.fish --help
    usage: doctest.fish [options] <file ...>
    
    options:
          --color WHEN      use colors or not? auto*, always, never
          --prefix PREFIX   set the command line prefix (default: 4 spaces)
          --prompt PROMPT   set the prompt string (default: "> ")
      -q, --quiet           no output is shown (not even errors)
      -v, --verbose         show information about every executed test
          --version         show the program version and exit
          --yaml            show all test cases as YAML (no test is run)
      -h, --help            show this help message and exit
    
    See also: https://github.com/aureliojargas/doctest.fish

Note that the exit status for this operation is always zero:

    > ./doctest.fish -h | head -n 1; echo $status
    usage: doctest.fish [options] <file ...>
    0
